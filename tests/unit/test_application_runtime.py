import builtins
import threading
import time
from collections.abc import Callable, Iterator
from datetime import UTC, datetime
from pathlib import Path

import pytest

from rfid_reader.config import load_config
from rfid_reader.domain import ConnectionKind, ConnectionStatus, InventoryStatus, TagRead
from rfid_reader.readers.base import ReaderConnectionError
from rfid_reader.runtime import (
    ApplicationRuntime,
    RuntimeDependencies,
    RuntimeEvent,
    RuntimeShutdownError,
)


class FakeReader:
    def __init__(self) -> None:
        self.connected = False
        self.reading = False
        self.starts = 0
        self.stops = 0
        self.connections = 0
        self.fail_start = False
        self.fail_connect = False
        self.tag_callback: Callable[[TagRead], None] = lambda tag: None
        self.disconnect_callback: Callable[[], None] = lambda: None

    def connect(self) -> None:
        if self.fail_connect:
            raise ReaderConnectionError("simulado")
        if not self.connected:
            self.connections += 1
        self.connected = True

    def disconnect(self) -> None:
        self.connected = False
        self.reading = False
        self.disconnect_callback()

    def is_connected(self) -> bool:
        return self.connected

    def is_inventorying(self) -> bool:
        return self.reading

    def configure_connection(self, host: str, port: int, reader_id: str) -> None:
        pass

    def set_disconnect_callback(self, callback: Callable[[], None]) -> None:
        self.disconnect_callback = callback

    def start_inventory(self, callback: Callable[[TagRead], None]) -> bool:
        self.starts += 1
        self.tag_callback = callback
        self.reading = not self.fail_start
        return self.reading

    def stop_inventory(self) -> bool:
        self.stops += 1
        self.reading = False
        return True

    def emit(self, epc: str = "E280691500005029EEA6A275") -> None:
        self.tag_callback(TagRead(epc, "simulated", 1, datetime.now(UTC)))


class FakeChecker:
    def __init__(self, status: ConnectionStatus = ConnectionStatus.CONNECTED) -> None:
        self.status = status
        self.closed = False

    def check(self) -> ConnectionStatus:
        return self.status

    def close(self) -> None:
        self.closed = True


def wait_until(predicate: Callable[[], bool], timeout: float = 3.0) -> None:
    deadline = time.monotonic() + timeout
    while not predicate():
        assert time.monotonic() < deadline, "A simulação não atingiu o estado esperado"
        threading.Event().wait(0.005)


@pytest.fixture
def runtime(tmp_path: Path) -> Iterator[ApplicationRuntime]:
    reader = FakeReader()
    reader.connect()
    checkers = {
        kind: FakeChecker()
        for kind in (
            ConnectionKind.RFID,
            ConnectionKind.INTERNET,
            ConnectionKind.WAVESHARE,
            ConnectionKind.SYSTEM,
        )
    }
    app = ApplicationRuntime(
        load_config({"RFID_STATUS_CHECK_INTERVAL_SECONDS": "0.01"}),
        tmp_path / ".env",
        RuntimeDependencies(reader=reader, checkers=checkers),
    )
    yield app
    app.close()


def test_runtime_does_not_import_tkinter_or_start_workers(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    original = builtins.__import__

    def guarded(name: str, *args: object, **kwargs: object) -> object:
        assert not name.startswith(("tkinter", "rfid_reader.ui"))
        return original(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded)
    before = {thread.ident for thread in threading.enumerate()}
    app = ApplicationRuntime(load_config({}), tmp_path / ".env")
    try:
        assert not app.reader.is_connected()
        assert {thread.ident for thread in threading.enumerate()} == before
    finally:
        app.close()


def test_runtime_start_commands_states_and_idempotent_shutdown(runtime: ApplicationRuntime) -> None:
    events: list[RuntimeEvent] = []
    runtime.subscribe(events.append)
    runtime.start()
    runtime.start()
    wait_until(lambda: runtime.automatic.ready)
    assert runtime.start_automatic()
    wait_until(lambda: runtime.automatic.enabled)
    assert runtime.inventory.status is InventoryStatus.STOPPED
    assert any(event.channel == "automatic" and event.value is True for event in events)
    assert len(runtime.statuses()) == 5
    assert runtime.stop_automatic()
    wait_until(lambda: not runtime.automatic.enabled)
    runtime.close()
    runtime.close()
    assert not runtime.reader.is_connected()
    assert not runtime.start_automatic()
    assert not any(
        thread.is_alive()
        and thread.name.startswith(("tag-lookup", "connection-monitor", "application-command"))
        for thread in threading.enumerate()
    )


def test_runtime_unsubscribe_detaches_consumer(runtime: ApplicationRuntime) -> None:
    events: list[RuntimeEvent] = []
    unsubscribe = runtime.subscribe(events.append)
    unsubscribe()
    runtime.start()
    wait_until(lambda: runtime.automatic.ready)
    assert not events


def test_shutdown_failure_does_not_leave_other_workers_alive(
    runtime: ApplicationRuntime, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fail() -> None:
        raise ReaderConnectionError("falha simulada durante disconnect")

    runtime.start()
    wait_until(lambda: runtime.automatic.ready)
    monkeypatch.setattr(runtime.reader, "disconnect", fail)
    with pytest.raises(RuntimeShutdownError, match="inventory"):
        runtime.close()
    assert not runtime.start_automatic()
    assert not any(
        thread.is_alive() and thread.name.startswith(("tag-lookup", "connection-monitor"))
        for thread in threading.enumerate()
    )
