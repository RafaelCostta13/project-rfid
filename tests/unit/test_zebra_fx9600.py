from collections.abc import Callable

import pytest

from rfid_reader.domain import TagRead
from rfid_reader.readers.base import ReaderConnectionError
from rfid_reader.readers.zebra_fx9600 import (
    SllurpStateIds,
    ZebraFX9600Reader,
)


class FakeMessage:
    def __init__(self, success: bool = True) -> None:
        self._success = success

    def isSuccess(self) -> bool:
        return self._success


class FakeLowLevelClient:
    def __init__(self) -> None:
        self.start_calls = 0
        self.stop_calls = 0
        self.states: list[int] = []

    def startInventory(self) -> None:
        self.start_calls += 1

    def stopPolitely(self, onCompletion: Callable[..., None] | None = None) -> None:
        self.stop_calls += 1
        if onCompletion is not None:
            onCompletion(18, True)

    def setState(self, state: int) -> None:
        self.states.append(state)


class FakeSllurpClient:
    def __init__(self, *, configure_on_connect: bool = True) -> None:
        self.llrp = FakeLowLevelClient()
        self._configure_on_connect = configure_on_connect
        self._message_callbacks: dict[str, Callable[..., None]] = {}
        self._state_callbacks: dict[int, Callable[..., None]] = {}
        self._tag_callback: Callable[..., None] | None = None
        self._disconnect_callback: Callable[..., None] | None = None
        self.alive = False
        self.connect_calls = 0
        self.disconnect_calls = 0
        self.hard_disconnect_calls = 0

    def add_state_callback(self, state: int, callback: Callable[..., None]) -> None:
        self._state_callbacks[state] = callback

    def add_message_callback(
        self,
        message_type: str,
        callback: Callable[..., None],
    ) -> None:
        self._message_callbacks[message_type] = callback

    def add_tag_report_callback(self, callback: Callable[..., None]) -> None:
        self._tag_callback = callback

    def add_disconnected_callback(self, callback: Callable[..., None]) -> None:
        self._disconnect_callback = callback

    def connect(self) -> None:
        self.connect_calls += 1
        self.alive = True
        if self._configure_on_connect:
            self._message_callbacks["SET_READER_CONFIG_RESPONSE"](
                self,
                FakeMessage(),
            )

    def disconnect(self, timeout: float = 0) -> None:
        self.disconnect_calls += 1
        self.alive = False
        if self._disconnect_callback is not None:
            self._disconnect_callback(self)

    def hard_disconnect(self) -> None:
        self.hard_disconnect_calls += 1
        self.alive = False

    def is_alive(self) -> bool:
        return self.alive

    def join(self, timeout: float | None = None) -> None:
        return None

    def emit_inventorying(self, state: int = 18) -> None:
        self._state_callbacks[state](self, state)

    def emit_tags(self, tags: list[dict[object, object]]) -> None:
        assert self._tag_callback is not None
        self._tag_callback(self, tags)

    def lose_connection(self) -> None:
        self.alive = False
        assert self._disconnect_callback is not None
        self._disconnect_callback(self)


def create_reader(
    client: FakeSllurpClient,
    timeout: float = 0.1,
) -> ZebraFX9600Reader:
    return ZebraFX9600Reader(
        "reader.local",
        5084,
        "fx9600-test",
        1,
        timeout,
        client_factory=lambda host, port, timeout_seconds, antenna: (
            client,
            SllurpStateIds(connected=3, inventorying=18),
        ),
    )


def test_connects_once_and_keeps_session_ready() -> None:
    client = FakeSllurpClient()
    reader = create_reader(client)

    reader.connect()
    reader.connect()

    assert reader.is_connected()
    assert client.connect_calls == 1


def test_connection_times_out_without_configuration_response() -> None:
    client = FakeSllurpClient(configure_on_connect=False)
    reader = create_reader(client, timeout=0.01)

    with pytest.raises(ReaderConnectionError, match="timeout"):
        reader.connect()

    assert not reader.is_connected()
    assert client.disconnect_calls == 1


def test_starts_only_one_inventory_and_preserves_received_epc() -> None:
    client = FakeSllurpClient()
    reader = create_reader(client)
    received: list[TagRead] = []
    reader.connect()

    assert reader.start_inventory(received.append)
    assert not reader.start_inventory(received.append)
    client.emit_inventorying()
    client.emit_tags(
        [
            {"EPC": b"e28011700001", "AntennaID": 1, "TagSeenCount": 2},
            {"EPC": "E28011700002"},
        ]
    )

    assert reader.is_inventorying()
    assert [tag.epc for tag in received] == ["e28011700001", "E28011700002"]
    assert received[0].antenna_id == 1
    assert received[0].seen_count == 2
    assert client.llrp.start_calls == 1


def test_stop_removes_inventory_and_blocks_late_reports() -> None:
    client = FakeSllurpClient()
    reader = create_reader(client)
    received: list[TagRead] = []
    reader.connect()
    reader.start_inventory(received.append)

    assert reader.stop_inventory()
    client.emit_tags([{"EPC": b"late-tag"}])

    assert received == []
    assert client.llrp.stop_calls == 1
    assert client.llrp.states == [3]
    assert not reader.is_inventorying()


def test_lost_connection_clears_inventory_and_notifies_listener() -> None:
    client = FakeSllurpClient()
    reader = create_reader(client)
    disconnected: list[bool] = []
    reader.set_disconnect_callback(lambda: disconnected.append(True))
    reader.connect()
    reader.start_inventory(lambda tag: None)

    client.lose_connection()

    assert disconnected == [True]
    assert not reader.is_connected()
    assert not reader.is_inventorying()


def test_disconnect_stops_inventory_before_closing_session() -> None:
    client = FakeSllurpClient()
    reader = create_reader(client)
    reader.connect()
    reader.start_inventory(lambda tag: None)

    reader.disconnect()

    assert client.llrp.stop_calls == 1
    assert client.disconnect_calls == 1
    assert not reader.is_connected()
