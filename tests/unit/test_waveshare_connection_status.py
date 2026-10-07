import threading

import pytest

from rfid_reader.domain import ConnectionKind, ConnectionStatus, WaveshareConnectionSettings
from rfid_reader.integrations.waveshare_modbus import (
    PymodbusWaveshareConnectionTester,
    WavesharePortBusyError,
    WavesharePortOpenError,
    WaveshareProtocolError,
    WaveshareSerialGate,
    WaveshareTimeoutError,
)
from rfid_reader.services.waveshare_connection import WaveshareConnectionChecker
from rfid_reader.services.waveshare_diagnostic import (
    DiagnosticEvent,
    DiagnosticEventKind,
    WaveshareDiagnosticService,
)
from rfid_reader.ui.components import CONNECTION_NAMES, ConnectionBar


def settings(port: str = "COM5") -> WaveshareConnectionSettings:
    return WaveshareConnectionSettings(port, 9600, 8, "None", 1, 1)


class FakeTester:
    def __init__(self, error: Exception | None = None) -> None:
        self.error = error
        self.calls: list[WaveshareConnectionSettings] = []

    def test(self, connection: WaveshareConnectionSettings) -> None:
        self.calls.append(connection)
        if self.error is not None:
            raise self.error


@pytest.mark.parametrize(
    ("error", "expected"),
    [
        (None, ConnectionStatus.CONNECTED),
        (WavesharePortOpenError(), ConnectionStatus.DISCONNECTED),
        (WavesharePortBusyError(), ConnectionStatus.DISCONNECTED),
        (WaveshareTimeoutError(), ConnectionStatus.DISCONNECTED),
        (WaveshareProtocolError(), ConnectionStatus.ERROR),
    ],
)
def test_periodic_status_reflects_modbus_response(
    error: Exception | None, expected: ConnectionStatus
) -> None:
    tester = FakeTester(error)
    service = WaveshareDiagnosticService(lambda: settings(), lambda event: None)
    checker = WaveshareConnectionChecker(service, tester)

    assert checker.check() is expected
    assert tester.calls == [settings()]
    checker.close()


def test_unconfigured_port_is_disconnected_without_opening_serial() -> None:
    tester = FakeTester()
    service = WaveshareDiagnosticService(lambda: settings(""), lambda event: None)

    assert WaveshareConnectionChecker(service, tester).check() is ConnectionStatus.DISCONNECTED
    assert tester.calls == []


def test_busy_port_is_checking_without_a_diagnostic_session() -> None:
    gate = WaveshareSerialGate()
    tester = PymodbusWaveshareConnectionTester(
        client_factory=lambda connection, timeout: pytest.fail("COM não deve ser aberta"),
        serial_gate=gate,
    )
    service = WaveshareDiagnosticService(lambda: settings(), lambda event: None, serial_gate=gate)
    gate.acquire()
    try:
        assert service.probe_status(tester) is ConnectionStatus.CHECKING
    finally:
        gate.release()


class FakePort:
    def __init__(self) -> None:
        self.closed = False

    def connect(self) -> tuple[bool, ...]:
        return (False,) * 5

    def read_inputs(self) -> tuple[bool, ...]:
        return (False,) * 5

    def read_relays(self) -> tuple[bool, ...]:
        return (False,) * 8

    def set_relay(self, channel: int, enabled: bool) -> bool:
        return enabled

    def close(self) -> None:
        self.closed = True


def test_monitor_uses_active_diagnostic_without_second_serial_client() -> None:
    gate = WaveshareSerialGate()
    events: list[DiagnosticEvent] = []
    connected = threading.Event()

    def on_event(event: DiagnosticEvent) -> None:
        events.append(event)
        if event.kind is DiagnosticEventKind.CONNECTED:
            connected.set()

    port = FakePort()
    service = WaveshareDiagnosticService(
        lambda: settings(), on_event, lambda connection: port, serial_gate=gate
    )
    tester = PymodbusWaveshareConnectionTester(
        client_factory=lambda connection, timeout: pytest.fail("COM não deve ser reaberta"),
        serial_gate=gate,
    )
    service.connect()
    try:
        assert connected.wait(1.0)
        assert WaveshareConnectionChecker(service, tester).check() is ConnectionStatus.CONNECTED
    finally:
        service.close()
    assert port.closed


def test_shared_gate_rejects_temporary_probe_while_diagnostic_owns_port() -> None:
    gate = WaveshareSerialGate()
    gate.acquire()
    tester = PymodbusWaveshareConnectionTester(
        client_factory=lambda connection, timeout: pytest.fail("COM não deve ser aberta"),
        serial_gate=gate,
    )
    try:
        with pytest.raises(WavesharePortBusyError):
            tester.test(settings())
    finally:
        gate.release()


def test_connection_bar_has_waveshare_with_existing_status_vocabulary() -> None:
    assert CONNECTION_NAMES[ConnectionKind.WAVESHARE] == "Comandos"
    assert ConnectionBar._status_text(ConnectionKind.WAVESHARE, ConnectionStatus.CONNECTED) == (
        "● Comandos: Conectado"
    )
    assert ConnectionBar._status_text(ConnectionKind.WAVESHARE, ConnectionStatus.DISCONNECTED) == (
        "● Comandos: Desconectado"
    )
