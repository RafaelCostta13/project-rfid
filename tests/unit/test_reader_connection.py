from rfid_reader.domain import ConnectionStatus
from rfid_reader.readers.base import (
    DisconnectCallback,
    ReaderConnectionError,
    TagCallback,
)
from rfid_reader.services.reader_connection import ReaderConnectionChecker


class FakeReader:
    def __init__(self, connected: bool = False, fail_connect: bool = False) -> None:
        self.connected = connected
        self.fail_connect = fail_connect
        self.connect_calls = 0

    def connect(self) -> None:
        self.connect_calls += 1
        if self.fail_connect:
            raise ReaderConnectionError("indisponível")
        self.connected = True

    def disconnect(self) -> None:
        self.connected = False

    def is_connected(self) -> bool:
        return self.connected

    def start_inventory(self, callback: TagCallback) -> bool:
        return False

    def stop_inventory(self) -> bool:
        return False

    def is_inventorying(self) -> bool:
        return False

    def set_disconnect_callback(self, callback: DisconnectCallback) -> None:
        return None


def test_connects_reader_once_and_reuses_ready_session() -> None:
    reader = FakeReader()
    checker = ReaderConnectionChecker(reader)

    assert checker.check() is ConnectionStatus.CONNECTED
    assert checker.check() is ConnectionStatus.CONNECTED
    assert reader.connect_calls == 1


def test_reports_disconnected_when_reader_connection_fails() -> None:
    checker = ReaderConnectionChecker(FakeReader(fail_connect=True))

    assert checker.check() is ConnectionStatus.DISCONNECTED
