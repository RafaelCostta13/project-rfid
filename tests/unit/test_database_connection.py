from pathlib import Path

from rfid_reader.domain import ConnectionKind, ConnectionStatus, LocalTagRecord
from rfid_reader.services.connection_monitor import ConnectionMonitor
from rfid_reader.services.local_database import LocalTagRepository
from rfid_reader.services.local_database_connection import (
    LocalDatabaseConnectionChecker,
    SyncConnectionChecker,
)


class SyncProbe:
    def __init__(self, result: bool = True) -> None:
        self.result = result
        self.calls = 0

    def check_remote(self) -> bool:
        self.calls += 1
        return self.result


def record(epc: str = "ABC123", dock: str = "D01") -> LocalTagRecord:
    return LocalTagRecord(
        sharepoint_id=1,
        status="Ativo",
        customer="CLIENTE",
        invoice_number="100001",
        volume="1/1",
        order_number="500001",
        dock=dock,
        epc=epc,
        sharepoint_modified="2026-10-05T10:00:00Z",
    )


def repository(tmp_path: Path) -> LocalTagRepository:
    repo = LocalTagRepository(tmp_path / "local.sqlite3")
    repo.initialize()
    return repo


def test_local_database_requires_initialized_dock(tmp_path: Path) -> None:
    repo = repository(tmp_path)
    checker = LocalDatabaseConnectionChecker(repo, lambda: "D01")

    assert checker.check() is ConnectionStatus.ERROR

    repo.apply_sync("D01", (), "2026-10-05T10:15:00Z", full_sync=True)

    assert checker.check() is ConnectionStatus.CONNECTED


def test_local_database_status_is_separated_by_dock(tmp_path: Path) -> None:
    repo = repository(tmp_path)
    repo.apply_sync("D01", (record(),), "2026-10-05T10:15:00Z", full_sync=True)

    assert LocalDatabaseConnectionChecker(repo, lambda: "D01").check() is ConnectionStatus.CONNECTED
    assert LocalDatabaseConnectionChecker(repo, lambda: "D05").check() is ConnectionStatus.ERROR


def test_local_database_checker_closes_to_disconnected(tmp_path: Path) -> None:
    checker = LocalDatabaseConnectionChecker(repository(tmp_path), lambda: "D01")

    checker.close()

    assert checker.check() is ConnectionStatus.DISCONNECTED


def test_sync_checker_uses_dock_modified_since_health_without_changing_database() -> None:
    probe = SyncProbe(True)
    now = 0.0
    checker = SyncConnectionChecker(
        probe, lambda: ConnectionStatus.CONNECTED, 60.0, clock=lambda: now
    )

    assert checker.check() is ConnectionStatus.CONNECTED
    assert checker.check() is ConnectionStatus.CONNECTED
    assert probe.calls == 1


def test_sync_checker_suspends_while_internet_is_unavailable_and_recovers() -> None:
    probe = SyncProbe(True)
    internet = ConnectionStatus.DISCONNECTED
    now = 0.0
    checker = SyncConnectionChecker(probe, lambda: internet, 60.0, clock=lambda: now)

    assert checker.check() is ConnectionStatus.DISCONNECTED
    assert probe.calls == 0

    internet = ConnectionStatus.CONNECTED
    assert checker.check() is ConnectionStatus.CONNECTED
    assert probe.calls == 1


def test_sync_checker_reports_remote_failure_without_invalidating_local_database(
    tmp_path: Path,
) -> None:
    repo = repository(tmp_path)
    repo.apply_sync("D01", (record(),), "2026-10-05T10:15:00Z", full_sync=True)
    sync = SyncConnectionChecker(SyncProbe(False), lambda: ConnectionStatus.CONNECTED, 60.0)
    database = LocalDatabaseConnectionChecker(repo, lambda: "D01")

    assert database.check() is ConnectionStatus.CONNECTED
    assert sync.check() is ConnectionStatus.ERROR
    assert database.check() is ConnectionStatus.CONNECTED


def test_monitor_publishes_database_and_sync_as_separate_statuses(tmp_path: Path) -> None:
    repo = repository(tmp_path)
    repo.apply_sync("D01", (), "2026-10-05T10:15:00Z", full_sync=True)
    updates: list[tuple[ConnectionKind, ConnectionStatus]] = []

    monitor = ConnectionMonitor(
        {
            ConnectionKind.DATABASE: LocalDatabaseConnectionChecker(repo, lambda: "D01"),
            ConnectionKind.SYNC: SyncConnectionChecker(
                SyncProbe(False), lambda: ConnectionStatus.CONNECTED, 60.0
            ),
        },
        0.01,
        lambda kind, status: updates.append((kind, status)),
    )
    monitor.start()
    try:
        import time

        deadline = time.monotonic() + 1.0
        while time.monotonic() < deadline and not (
            (ConnectionKind.DATABASE, ConnectionStatus.CONNECTED) in updates
            and (ConnectionKind.SYNC, ConnectionStatus.ERROR) in updates
        ):
            time.sleep(0.005)
    finally:
        monitor.stop()

    assert (ConnectionKind.DATABASE, ConnectionStatus.CONNECTED) in updates
    assert (ConnectionKind.SYNC, ConnectionStatus.ERROR) in updates
