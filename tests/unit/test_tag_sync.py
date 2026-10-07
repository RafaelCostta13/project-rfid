from pathlib import Path

import pytest

from rfid_reader.domain import LocalTagRecord
from rfid_reader.integrations.sharepoint_sync_client import SyncClientError, SyncPayload
from rfid_reader.services.local_database import LocalDatabaseError, LocalTagRepository
from rfid_reader.services.tag_sync import (
    TagSyncLocalError,
    TagSyncRemoteError,
    TagSyncService,
)


def record(sharepoint_id: int = 10, epc: str = "ABC123") -> LocalTagRecord:
    return LocalTagRecord(
        sharepoint_id=sharepoint_id,
        status="Ativo",
        customer="CLIENTE ALFA",
        invoice_number="100001",
        volume="1/1",
        order_number="500001",
        dock="D01",
        epc=epc,
        sharepoint_modified="2026-10-05T10:10:00Z",
    )


class FakeSyncClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []
        self.responses: list[SyncPayload | Exception] = []

    def sync(self, dock: str, modified_since: str) -> SyncPayload:
        self.calls.append((dock, modified_since))
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


class FailingCursorRepository(LocalTagRepository):
    def sync_control(self, dock: str):  # type: ignore[no-untyped-def]
        raise LocalDatabaseError("cursor indisponível")


def service(tmp_path: Path, client: FakeSyncClient) -> tuple[TagSyncService, LocalTagRepository]:
    repo = LocalTagRepository(tmp_path / "local.sqlite3")
    repo.initialize()
    return TagSyncService(client, repo, lambda: "D01"), repo


def test_initial_sync_uses_empty_cursor_and_initializes_dock(tmp_path: Path) -> None:
    client = FakeSyncClient()
    client.responses.append(SyncPayload("T1", (record(),)))
    sync, repo = service(tmp_path, client)

    sync.sync_current_dock()

    assert client.calls == [("D01", "")]
    assert repo.is_operational("D01")
    assert repo.find_by_epc("ABC123", "D01") is not None
    assert repo.sync_control("D01") is not None
    assert repo.sync_control("D01").last_sync == "T1"  # type: ignore[union-attr]


def test_empty_initial_sync_is_valid(tmp_path: Path) -> None:
    client = FakeSyncClient()
    client.responses.append(SyncPayload("T1", ()))
    sync, repo = service(tmp_path, client)

    sync.sync_current_dock()

    assert repo.is_operational("D01")
    assert repo.sync_control("D01") is not None


def test_incremental_sync_uses_confirmed_cursor(tmp_path: Path) -> None:
    client = FakeSyncClient()
    client.responses.extend(
        [
            SyncPayload("T1", (record(),)),
            SyncPayload("T2", (record(11, "DEF456"),)),
        ]
    )
    sync, repo = service(tmp_path, client)

    sync.sync_current_dock()
    sync.sync_current_dock()

    assert client.calls == [("D01", ""), ("D01", "T1")]
    control = repo.sync_control("D01")
    assert control is not None
    assert control.last_sync == "T2"


def test_remote_failure_preserves_previous_local_base(tmp_path: Path) -> None:
    client = FakeSyncClient()
    client.responses.extend([SyncPayload("T1", (record(),)), SyncClientError("offline")])
    sync, repo = service(tmp_path, client)
    sync.sync_current_dock()

    with pytest.raises(TagSyncRemoteError):
        sync.sync_current_dock()

    assert repo.find_by_epc("ABC123", "D01") is not None
    control = repo.sync_control("D01")
    assert control is not None
    assert control.last_sync == "T1"


def test_health_check_does_not_advance_cursor_or_write_items(tmp_path: Path) -> None:
    client = FakeSyncClient()
    client.responses.extend(
        [
            SyncPayload("T1", (record(),)),
            SyncPayload("T2", (record(11, "DEF456"),)),
        ]
    )
    sync, repo = service(tmp_path, client)
    sync.sync_current_dock()

    assert sync.check_remote()

    assert client.calls == [("D01", ""), ("D01", "T1")]
    assert repo.find_by_epc("DEF456", "D01") is None
    control = repo.sync_control("D01")
    assert control is not None
    assert control.last_sync == "T1"


def test_missing_dock_blocks_sync(tmp_path: Path) -> None:
    repo = LocalTagRepository(tmp_path / "local.sqlite3")
    repo.initialize()
    client = FakeSyncClient()
    sync = TagSyncService(client, repo, lambda: "")

    with pytest.raises(TagSyncRemoteError):
        sync.sync_current_dock()
    assert not sync.check_remote()
    assert client.calls == []


def test_local_write_failure_is_not_reported_as_remote_sync_failure(tmp_path: Path) -> None:
    client = FakeSyncClient()
    client.responses.append(
        SyncPayload(
            "T2",
            (
                record(10, "ABC123"),
                record(11, "ABC123"),
            ),
        )
    )
    sync, repo = service(tmp_path, client)

    with pytest.raises(TagSyncLocalError):
        sync.sync_current_dock()

    assert client.calls == [("D01", "")]
    assert not repo.is_operational("D01")


def test_health_check_still_checks_remote_when_local_cursor_fails(tmp_path: Path) -> None:
    client = FakeSyncClient()
    client.responses.append(SyncPayload("T2", ()))
    repo = FailingCursorRepository(tmp_path / "local.sqlite3")
    repo.initialize()
    sync = TagSyncService(client, repo, lambda: "D01")

    assert sync.check_remote()

    assert client.calls
    assert client.calls[0][0] == "D01"
    assert client.calls[0][1] != ""
