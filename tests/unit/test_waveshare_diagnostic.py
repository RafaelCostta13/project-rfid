import threading
import time

import pytest

from rfid_reader.domain import (
    ConnectionKind,
    ConnectionStatus,
    InventoryStatus,
    WaveshareConnectionSettings,
)
from rfid_reader.integrations.waveshare_modbus import (
    WaveshareDiagnosticPort,
    WaveshareProtocolError,
)
from rfid_reader.services.automatic_inventory import AutomaticInventoryController
from rfid_reader.services.waveshare_diagnostic import (
    PORT_REQUIRED_MESSAGE,
    DiagnosticEvent,
    DiagnosticEventKind,
    WaveshareDiagnosticService,
)


def settings(port: str = "COM5") -> WaveshareConnectionSettings:
    return WaveshareConnectionSettings(port, 9600, 8, "None", 1, 1)


class Response:
    def __init__(self, bits: list[bool] | None = None, error: bool = False) -> None:
        self.bits = bits or []
        self.error = error

    def isError(self) -> bool:  # noqa: N802
        return self.error


class ModbusClient:
    def __init__(self) -> None:
        self.calls: list[tuple[object, ...]] = []
        self.inputs = [False, True, False, True, False]
        self.relays = [False] * 8
        self.write_error = False
        self.closed = False

    def connect(self) -> bool:
        self.calls.append(("connect",))
        return True

    def read_discrete_inputs(self, address: int, *, count: int, device_id: int) -> Response:
        self.calls.append(("inputs", address, count, device_id))
        return Response(self.inputs[:count])

    def read_coils(self, address: int, *, count: int, device_id: int) -> Response:
        self.calls.append(("coils", address, count, device_id))
        return Response(self.relays[address : address + count])

    def write_coil(self, address: int, value: bool, *, device_id: int) -> Response:
        self.calls.append(("write", address, value, device_id))
        if not self.write_error:
            self.relays[address] = value
        return Response(error=self.write_error)

    def close(self) -> None:
        self.calls.append(("close",))
        self.closed = True


def test_port_uses_confirmed_addresses_and_reads_back_each_relay() -> None:
    client = ModbusClient()
    port = WaveshareDiagnosticPort(settings(), lambda config, timeout: client)

    assert port.connect() == (False, True, False, True, False)
    assert port.read_relays() == (False,) * 8
    for channel in range(1, 9):
        assert port.set_relay(channel, True)
        assert not port.set_relay(channel, False)
    port.close()

    assert ("inputs", 0, 5, 1) in client.calls
    assert ("coils", 0, 8, 1) in client.calls
    for address in range(8):
        assert ("write", address, True, 1) in client.calls
        assert ("write", address, False, 1) in client.calls
        assert ("coils", address, 1, 1) in client.calls
    assert client.closed


@pytest.mark.parametrize(("channel", "address"), [(6, 5), (7, 6), (8, 7)])
def test_ch6_ch7_ch8_on_off_use_their_own_coils(channel: int, address: int) -> None:
    client = ModbusClient()
    port = WaveshareDiagnosticPort(settings(), lambda config, timeout: client)

    assert port.set_relay(channel, True) is True
    assert client.relays[address] is True
    assert sum(client.relays) == 1
    assert port.set_relay(channel, False) is False

    assert client.relays == [False] * 8
    assert client.calls == [
        ("write", address, True, 1),
        ("coils", address, 1, 1),
        ("write", address, False, 1),
        ("coils", address, 1, 1),
    ]


def test_failed_write_does_not_confirm_state() -> None:
    client = ModbusClient()
    client.write_error = True
    port = WaveshareDiagnosticPort(settings(), lambda config, timeout: client)

    with pytest.raises(WaveshareProtocolError):
        port.set_relay(5, True)

    assert client.relays == [False] * 8


class FakePort:
    def __init__(self) -> None:
        self.inputs = (False,) * 5
        self.relays = (False,) * 8
        self.closed = False
        self.fail_poll = False
        self.fail_connect = False
        self.fail_relay = False
        self.calls: list[str] = []
        self.started = threading.Event()

    def connect(self) -> tuple[bool, ...]:
        self.calls.append("connect")
        self.started.set()
        if self.fail_connect:
            raise WaveshareProtocolError("falha na conexão")
        return self.inputs

    def read_inputs(self) -> tuple[bool, ...]:
        self.calls.append("poll")
        if self.fail_poll:
            raise WaveshareProtocolError("falha simulada")
        return self.inputs

    def read_relays(self) -> tuple[bool, ...]:
        self.calls.append("relays")
        return self.relays

    def set_relay(self, channel: int, enabled: bool) -> bool:
        self.calls.append(f"CH{channel}={enabled}")
        if self.fail_relay:
            raise WaveshareProtocolError("falha no relé")
        return enabled

    def close(self) -> None:
        self.calls.append("close")
        self.closed = True


def wait_for(events: list[DiagnosticEvent], kind: DiagnosticEventKind) -> None:
    deadline = time.monotonic() + 3
    while not any(event.kind is kind for event in events):
        if time.monotonic() > deadline:
            pytest.fail(f"Evento {kind} não recebido")
        time.sleep(0.01)


def test_missing_port_does_not_open_client() -> None:
    events: list[DiagnosticEvent] = []
    service = WaveshareDiagnosticService(
        lambda: settings(""),
        events.append,
        lambda config: pytest.fail("não deve abrir a COM"),
    )

    service.connect()

    assert events == [DiagnosticEvent(DiagnosticEventKind.DISCONNECTED, PORT_REQUIRED_MESSAGE)]


def test_worker_serializes_commands_and_releases_port_on_disconnect() -> None:
    events: list[DiagnosticEvent] = []
    port = FakePort()
    service = WaveshareDiagnosticService(lambda: settings(), events.append, lambda config: port)

    service.connect()
    wait_for(events, DiagnosticEventKind.CONNECTED)
    for channel in range(1, 9):
        service.set_relay(channel, True)
    deadline = time.monotonic() + 3
    while len([event for event in events if event.kind is DiagnosticEventKind.RELAYS]) < 9:
        if time.monotonic() > deadline:
            pytest.fail("Comandos não processados")
        time.sleep(0.01)
    service.close()

    assert port.closed
    assert port.calls[0:2] == ["connect", "relays"]
    assert port.calls[-1] == "close"
    assert [f"CH{channel}=True" for channel in range(1, 9)] == [
        call for call in port.calls if call.startswith("CH")
    ]
    assert events[-1].kind is DiagnosticEventKind.DISCONNECTED


def test_polling_failure_disconnects_and_forgets_states() -> None:
    events: list[DiagnosticEvent] = []
    port = FakePort()
    port.fail_poll = True
    service = WaveshareDiagnosticService(lambda: settings(), events.append, lambda config: port)

    service.connect()
    wait_for(events, DiagnosticEventKind.DISCONNECTED)
    service.close()

    assert port.closed
    assert events[-1].message == "Comunicação com a Waveshare perdida."


def test_connection_failure_closes_port_without_showing_connected() -> None:
    events: list[DiagnosticEvent] = []
    port = FakePort()
    port.fail_connect = True
    service = WaveshareDiagnosticService(lambda: settings(), events.append, lambda config: port)

    service.connect()
    wait_for(events, DiagnosticEventKind.DISCONNECTED)
    service.close()

    assert port.closed
    assert not any(event.kind is DiagnosticEventKind.CONNECTED for event in events)


def test_failed_relay_command_emits_error_without_confirmed_state() -> None:
    events: list[DiagnosticEvent] = []
    port = FakePort()
    port.fail_relay = True
    service = WaveshareDiagnosticService(lambda: settings(), events.append, lambda config: port)

    service.connect()
    wait_for(events, DiagnosticEventKind.CONNECTED)
    service.set_relay(5, True)
    wait_for(events, DiagnosticEventKind.RELAY_ERROR)
    service.close()

    assert not any(
        event.kind is DiagnosticEventKind.RELAYS and event.channel == 5 for event in events
    )
    assert port.closed


class FakeInventory:
    def __init__(self) -> None:
        self.status = InventoryStatus.STOPPED
        self.started = threading.Event()
        self.stopped = threading.Event()

    def start(self) -> bool:
        self.status = InventoryStatus.READING
        self.started.set()
        return True

    def stop(self) -> bool:
        self.status = InventoryStatus.STOPPED
        self.stopped.set()
        return True


@pytest.mark.parametrize("failure", ["poll", "relay", "close"])
def test_automatic_worker_stops_on_failure_and_preserves_other_relays(failure: str) -> None:
    events: list[DiagnosticEvent] = []
    port = FakePort()
    port.inputs = (True,) * 5
    inventory = FakeInventory()
    controller = AutomaticInventoryController(inventory)
    service = WaveshareDiagnosticService(
        lambda: settings(), events.append, lambda config: port, automatic=controller
    )
    try:
        controller.update_connection_status(ConnectionKind.INTERNET, ConnectionStatus.CONNECTED)
        controller.update_connection_status(ConnectionKind.RFID, ConnectionStatus.CONNECTED)
        controller.update_connection_status(ConnectionKind.DATABASE, ConnectionStatus.CONNECTED)
        service.connect_automatic()
        wait_for(events, DiagnosticEventKind.AUTOMATIC)
        polls_before_enable = port.calls.count("poll")
        assert controller.enable()
        # Primeiro estado processado antes da borda simulada.
        deadline = time.monotonic() + 2
        while "CH1=True" not in port.calls:
            assert time.monotonic() < deadline
            time.sleep(0.01)
        while port.calls.count("poll") == polls_before_enable:
            assert time.monotonic() < deadline
            time.sleep(0.01)
        before = len(port.calls)
        service.set_relay(1, False)
        service.set_relay(4, True)
        port.inputs = (False, True, True, True, True)
        assert inventory.started.wait(2)
        deadline = time.monotonic() + 2
        while "CH2=True" not in port.calls:
            assert time.monotonic() < deadline
            time.sleep(0.01)
        if failure == "poll":
            port.fail_poll = True
        elif failure == "relay":
            port.fail_relay = True
            port.inputs = (False, False, True, True, True)
        else:
            service.close()
        assert inventory.stopped.wait(2)
        wait_for(events, DiagnosticEventKind.DISCONNECTED)
        assert not controller.enabled
        assert "CH4=True" in port.calls[before:]
        assert not any(call.startswith(("CH5=", "CH6=", "CH7=", "CH8=")) for call in port.calls)
    finally:
        service.close()
    assert port.closed
