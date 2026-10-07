from pathlib import Path

import pytest

from rfid_reader.domain import LocalTagRecord
from rfid_reader.services.local_database import LocalDatabaseError, LocalTagRepository


def record(
    sharepoint_id: int,
    epc: str,
    *,
    dock: str = "D01",
    status: str = "Ativo",
    customer: str = "CLIENTE ALFA",
) -> LocalTagRecord:
    return LocalTagRecord(
        sharepoint_id=sharepoint_id,
        status=status,
        customer=customer,
        invoice_number="100001",
        volume="1/3",
        order_number="500001",
        dock=dock,
        epc=epc,
        sharepoint_modified="2026-10-05T10:10:00Z",
    )


def repository(tmp_path: Path) -> LocalTagRepository:
    repo = LocalTagRepository(tmp_path / "rfid-reader.sqlite3")
    repo.initialize()
    return repo


def test_creates_database_schema_and_initializes_empty_full_sync(tmp_path: Path) -> None:
    repo = repository(tmp_path)

    repo.apply_sync("D01", (), "2026-10-05T10:15:00Z", full_sync=True)

    assert repo.database_path.exists()
    control = repo.sync_control("D01")
    assert control is not None
    assert control.initialized
    assert control.last_sync == "2026-10-05T10:15:00Z"
    assert control.last_full_sync == "2026-10-05T10:15:00Z"
    assert repo.is_operational("D01")


def test_upsert_inserts_updates_and_queries_by_epc_and_dock(tmp_path: Path) -> None:
    repo = repository(tmp_path)
    repo.apply_sync(
        "D01",
        (record(10, "ABC123"), record(11, "OTHER", dock="D05")),
        "2026-10-05T10:15:00Z",
        full_sync=True,
    )
    repo.apply_sync(
        "D01",
        (record(10, "ABC123", customer="CLIENTE BETA"),),
        "2026-10-05T10:30:00Z",
        full_sync=False,
    )

    result = repo.find_by_epc("ABC123", "D01")

    assert result is not None
    assert result.customer == "CLIENTE BETA"
    assert repo.find_by_epc("ABC123", "D05") is None
    assert repo.find_by_epc("MISSING", "D01") is None
    control = repo.sync_control("D01")
    assert control is not None
    assert control.last_sync == "2026-10-05T10:30:00Z"
    assert control.last_full_sync == "2026-10-05T10:15:00Z"


def test_inactive_records_remain_stored_but_are_not_operational_results(tmp_path: Path) -> None:
    repo = repository(tmp_path)
    repo.apply_sync(
        "D01",
        (record(10, "ABC123", status="Inativo"),),
        "2026-10-05T10:15:00Z",
        full_sync=True,
    )

    assert repo.find_by_epc("ABC123", "D01") is None
    assert repo.is_operational("D01")


def test_cursors_are_separated_by_dock(tmp_path: Path) -> None:
    repo = repository(tmp_path)
    repo.apply_sync("D01", (record(10, "ABC123"),), "T1", full_sync=True)
    repo.apply_sync("D05", (record(20, "DEF456", dock="D05"),), "T5", full_sync=True)

    d01 = repo.sync_control("D01")
    d05 = repo.sync_control("D05")

    assert d01 is not None and d01.last_sync == "T1"
    assert d05 is not None and d05.last_sync == "T5"
    assert repo.find_by_epc("DEF456", "D01") is None
    assert repo.find_by_epc("DEF456", "D05") is not None


def test_failed_upsert_rolls_back_records_and_cursor(tmp_path: Path) -> None:
    repo = repository(tmp_path)
    repo.apply_sync("D01", (record(10, "ABC123"),), "T1", full_sync=True)

    with pytest.raises(LocalDatabaseError):
        repo.apply_sync(
            "D01",
            (record(11, "NEW001"), record(12, "ABC123")),
            "T2",
            full_sync=False,
        )

    assert repo.find_by_epc("NEW001", "D01") is None
    assert repo.find_by_epc("ABC123", "D01") is not None
    control = repo.sync_control("D01")
    assert control is not None
    assert control.last_sync == "T1"
