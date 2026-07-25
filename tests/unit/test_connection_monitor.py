import threading

from rfid_reader.domain import ConnectionKind, ConnectionStatus
from rfid_reader.services.connection_monitor import ConnectionMonitor


class FakeChecker:
    def __init__(self, statuses: list[ConnectionStatus]) -> None:
        self._statuses = iter(statuses)
        self._last = statuses[-1]
        self.closed = False

    def check(self) -> ConnectionStatus:
        return next(self._statuses, self._last)

    def close(self) -> None:
        self.closed = True


class FailingChecker:
    def __init__(self) -> None:
        self.closed = False

    def check(self) -> ConnectionStatus:
        raise RuntimeError("falha simulada")

    def close(self) -> None:
        self.closed = True


def test_publishes_initial_and_changed_states_independently() -> None:
    rfid = FakeChecker([ConnectionStatus.CONNECTED])
    internet = FakeChecker([ConnectionStatus.DISCONNECTED])
    updates: list[tuple[ConnectionKind, ConnectionStatus]] = []
    completed = threading.Event()

    def listener(kind: ConnectionKind, status: ConnectionStatus) -> None:
        updates.append((kind, status))
        if len(updates) >= 4:
            completed.set()

    monitor = ConnectionMonitor(
        {
            ConnectionKind.RFID: rfid,
            ConnectionKind.INTERNET: internet,
        },
        1.0,
        listener,
    )

    monitor.start()
    assert completed.wait(1.0)
    monitor.stop()

    assert (ConnectionKind.RFID, ConnectionStatus.CHECKING) in updates
    assert (ConnectionKind.INTERNET, ConnectionStatus.CHECKING) in updates
    assert (ConnectionKind.RFID, ConnectionStatus.CONNECTED) in updates
    assert (ConnectionKind.INTERNET, ConnectionStatus.DISCONNECTED) in updates
    assert rfid.closed
    assert internet.closed


def test_converts_checker_failure_to_error_without_stopping_other_checker() -> None:
    rfid = FailingChecker()
    internet = FakeChecker([ConnectionStatus.CONNECTED])
    updates: list[tuple[ConnectionKind, ConnectionStatus]] = []
    completed = threading.Event()

    def listener(kind: ConnectionKind, status: ConnectionStatus) -> None:
        updates.append((kind, status))
        if (ConnectionKind.RFID, ConnectionStatus.ERROR) in updates and (
            ConnectionKind.INTERNET,
            ConnectionStatus.CONNECTED,
        ) in updates:
            completed.set()

    monitor = ConnectionMonitor(
        {
            ConnectionKind.RFID: rfid,
            ConnectionKind.INTERNET: internet,
        },
        1.0,
        listener,
    )

    monitor.start()
    assert completed.wait(1.0)
    monitor.stop()

    assert monitor.statuses() == {
        ConnectionKind.RFID: ConnectionStatus.ERROR,
        ConnectionKind.INTERNET: ConnectionStatus.CONNECTED,
    }
    assert rfid.closed
    assert internet.closed


def test_publishes_periodic_status_changes() -> None:
    checker = FakeChecker([ConnectionStatus.CONNECTED, ConnectionStatus.DISCONNECTED])
    updates: list[tuple[ConnectionKind, ConnectionStatus]] = []
    disconnected = threading.Event()

    def listener(kind: ConnectionKind, status: ConnectionStatus) -> None:
        updates.append((kind, status))
        if status is ConnectionStatus.DISCONNECTED:
            disconnected.set()

    monitor = ConnectionMonitor(
        {ConnectionKind.RFID: checker},
        0.01,
        listener,
    )

    monitor.start()
    assert disconnected.wait(1.0)
    monitor.stop()

    assert updates == [
        (ConnectionKind.RFID, ConnectionStatus.CHECKING),
        (ConnectionKind.RFID, ConnectionStatus.CONNECTED),
        (ConnectionKind.RFID, ConnectionStatus.DISCONNECTED),
    ]
