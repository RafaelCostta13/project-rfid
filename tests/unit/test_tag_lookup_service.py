import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path

import pytest

from rfid_reader.domain import (
    LocalTagRecord,
    RfidReadResult,
    TagLookupChanged,
    TagLookupEvent,
    TagLookupSessionStarted,
    TagLookupStatus,
    TagRead,
)
from rfid_reader.integrations.backend_client import BackendClientError, RfidRecordData
from rfid_reader.services.epc_filter import EpcFilterState
from rfid_reader.services.local_database import LocalTagRepository
from rfid_reader.services.tag_lookup import FRIENDLY_ERROR_MESSAGE, TagLookupService

EPC_01 = "4550432D3031"
EPC_02 = "4550432D3032"
EPC_OTHER_DOCK = "4F54484552"
EPC_INACTIVE = "494E414354495645"
EPC_MISSING = "4D495353494E47"
EPC_ERROR = "4552524F52"


def tag(epc: str, antenna_id: int | None = 1) -> TagRead:
    return TagRead(
        epc=epc,
        reader_id="reader-01",
        antenna_id=antenna_id,
        read_at=datetime.now(UTC),
    )


def wait_until(predicate: Callable[[], bool], timeout: float = 1.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.005)
    raise AssertionError("condicao assincrona nao foi atendida")


def record(
    sharepoint_id: int,
    epc: str,
    *,
    dock: str = "D01",
    status: str = "Ativo",
) -> LocalTagRecord:
    return LocalTagRecord(
        sharepoint_id=sharepoint_id,
        status=status,
        customer=f"Cliente {epc}",
        invoice_number=f"NF {epc}",
        volume="1/1",
        order_number=f"Pedido {epc}",
        dock=dock,
        epc=epc,
        sharepoint_modified="2026-10-05T10:00:00Z",
    )


def repository(tmp_path: Path) -> LocalTagRepository:
    repo = LocalTagRepository(tmp_path / "local.sqlite3")
    repo.initialize()
    repo.apply_sync(
        "D01",
        (
            record(1, EPC_01),
            record(2, EPC_02),
            record(3, EPC_OTHER_DOCK, dock="D05"),
            record(4, EPC_INACTIVE, status="Inativo"),
        ),
        "2026-10-05T10:15:00Z",
        full_sync=True,
    )
    return repo


class LocalCompatibilityClient:
    """Adapta a fixture SQLite antiga ao contrato do cliente Backend nos testes."""

    def __init__(
        self,
        repository: LocalTagRepository,
        dock: str,
        post_error: Exception | None = None,
        read_count: int = 0,
    ) -> None:
        self._repository = repository
        self._dock = dock
        self._post_error = post_error
        self._read_count = read_count
        self.get_requests: list[str] = []
        self.post_requests: list[str] = []

    def get_rfid_record(self, epc: str) -> RfidRecordData | None:
        self.get_requests.append(epc)
        try:
            result = self._repository.find_by_epc(epc, self._dock)
        except Exception as error:
            raise BackendClientError("falha simulada no Backend") from error
        if result is None:
            return None
        return RfidRecordData(
            datahora="",
            volume=result.volume,
            pedido=result.order_number,
            notafiscal=result.invoice_number,
            destinatario=result.customer,
            endereco="",
            numero="",
            cidade="",
            uf="",
            doca=result.dock,
            epc=result.epc,
            tag=None,
            fornecedor=result.customer,
            status="pendente",
            first_read_at=None,
            last_read_at=None,
            read_count=self._read_count,
        )

    def create_rfid_read(self, epc: str) -> RfidReadResult:
        self.post_requests.append(epc)
        if self._post_error is not None:
            raise self._post_error
        return RfidReadResult(
            success=True,
            epc=epc,
            first_read=True,
            duplicate=False,
            status="lido",
            read_count=1,
            first_read_at="2026-10-07T10:00:00Z",
            last_read_at="2026-10-07T10:00:00Z",
        )


def completed(events: list[TagLookupEvent], epc: str) -> list[TagLookupChanged]:
    return [
        event
        for event in events
        if isinstance(event, TagLookupChanged)
        and event.result.epc == epc
        and event.result.status is not TagLookupStatus.CONSULTING
    ]


def test_deduplicates_same_reader_antenna_and_epc_in_one_session(tmp_path: Path) -> None:
    events: list[TagLookupEvent] = []
    service = TagLookupService(
        lambda: LocalCompatibilityClient(repository(tmp_path), "D01"), 10, events.append
    )
    try:
        service.start_session()

        assert service.submit(tag(EPC_01))
        assert not service.submit(tag(EPC_01))
        wait_until(lambda: len(completed(events, EPC_01)) == 1)

        assert completed(events, EPC_01)[0].result.customer == f"Cliente {EPC_01}"
        assert completed(events, EPC_01)[0].result.supplier == f"Cliente {EPC_01}"
    finally:
        service.close()


def test_found_epc_executes_one_get_and_one_post_in_session(tmp_path: Path) -> None:
    events: list[TagLookupEvent] = []
    client = LocalCompatibilityClient(repository(tmp_path), "D01")
    service = TagLookupService(lambda: client, 10, events.append)
    try:
        service.start_session()
        assert service.submit(tag(EPC_01))
        assert not service.submit(tag(EPC_01))
        wait_until(lambda: len(completed(events, EPC_01)) == 1)
        assert client.get_requests == [EPC_01]
        assert client.post_requests == [EPC_01]
        assert completed(events, EPC_01)[0].result.record_status == "lido"
    finally:
        service.close()


def test_resume_session_preserves_deduplication_and_counts_new_epcs(tmp_path: Path) -> None:
    events: list[TagLookupEvent] = []
    service = TagLookupService(
        lambda: LocalCompatibilityClient(repository(tmp_path), "D01"), 10, events.append
    )
    try:
        session_id = service.start_session()
        assert service.submit(tag(EPC_01))
        wait_until(lambda: len(completed(events, EPC_01)) == 1)
        service.stop_accepting()
        service.resume_session()
        assert not service.submit(tag(EPC_01, 2))
        assert service.submit(tag(EPC_02))
        wait_until(lambda: len(completed(events, EPC_02)) == 1)
        assert service.session_id == session_id
        assert service.complete_session(session_id) == 2
    finally:
        service.close()


def test_complete_session_returns_only_confirmed_found_epcs(tmp_path: Path) -> None:
    events: list[TagLookupEvent] = []
    service = TagLookupService(
        lambda: LocalCompatibilityClient(repository(tmp_path), "D01"), 10, events.append
    )
    try:
        session_id = service.start_session()
        assert service.submit(tag(EPC_01))
        assert service.submit(tag(EPC_02))
        wait_until(lambda: len(completed(events, EPC_02)) == 1)
        service.stop_accepting()

        assert service.complete_session(session_id) == 2
    finally:
        service.close()


def test_previously_read_epc_is_extra_box_and_still_executes_post(
    tmp_path: Path,
) -> None:
    events: list[TagLookupEvent] = []
    client = LocalCompatibilityClient(repository(tmp_path), "D01", read_count=1)
    service = TagLookupService(lambda: client, 10, events.append)
    try:
        service.start_session()
        assert service.submit(tag(EPC_01))
        wait_until(lambda: len(completed(events, EPC_01)) == 1)

        result = completed(events, EPC_01)[0].result
        assert result.status is TagLookupStatus.EXTRA_BOX
        assert client.get_requests == [EPC_01]
        assert client.post_requests == [EPC_01]
    finally:
        service.close()


def test_not_found_does_not_execute_post(tmp_path: Path) -> None:
    events: list[TagLookupEvent] = []
    client = LocalCompatibilityClient(repository(tmp_path), "D01")
    service = TagLookupService(lambda: client, 10, events.append)
    try:
        service.start_session()
        assert service.submit(tag(EPC_MISSING))
        wait_until(lambda: len(completed(events, EPC_MISSING)) == 1)
        assert client.get_requests == [EPC_MISSING]
        assert client.post_requests == []
        assert completed(events, EPC_MISSING)[0].result.status is TagLookupStatus.NOT_FOUND
    finally:
        service.close()


def test_post_failure_is_not_retried_in_same_session(tmp_path: Path) -> None:
    events: list[TagLookupEvent] = []
    client = LocalCompatibilityClient(
        repository(tmp_path), "D01", post_error=BackendClientError("timeout")
    )
    service = TagLookupService(lambda: client, 10, events.append)
    try:
        service.start_session()
        assert service.submit(tag(EPC_01))
        assert not service.submit(tag(EPC_01))
        wait_until(lambda: len(completed(events, EPC_01)) == 1)
        assert client.post_requests == [EPC_01]
        assert completed(events, EPC_01)[0].result.status is TagLookupStatus.ERROR
    finally:
        service.close()


def test_same_epc_on_another_antenna_is_processed_once_per_session(tmp_path: Path) -> None:
    events: list[TagLookupEvent] = []
    client = LocalCompatibilityClient(repository(tmp_path), "D01")
    service = TagLookupService(lambda: client, 10, events.append)
    try:
        service.start_session()

        assert service.submit(tag(EPC_01, 1))
        assert not service.submit(tag(EPC_01.lower(), 2))
        wait_until(lambda: len(completed(events, EPC_01)) == 1)
        assert not service.submit(tag(EPC_01, 2))
        assert client.get_requests == [EPC_01]
        assert client.post_requests == [EPC_01]
        assert completed(events, EPC_01)[0].key.antenna_id == 1
        service.start_session()
        assert service.submit(tag(EPC_01, 2))
        wait_until(lambda: len(completed(events, EPC_01)) == 2)
        assert client.get_requests == [EPC_01, EPC_01]
        assert client.post_requests == [EPC_01, EPC_01]
    finally:
        service.close()


@pytest.mark.parametrize("case", ["found", "already_read", "missing", "post_error"])
def test_concurrent_antennas_do_not_duplicate_business_processing(
    tmp_path: Path, case: str
) -> None:
    events: list[TagLookupEvent] = []
    client = LocalCompatibilityClient(
        repository(tmp_path),
        "D01",
        read_count=1 if case == "already_read" else 0,
        post_error=BackendClientError("timeout") if case == "post_error" else None,
    )
    epc = EPC_MISSING if case == "missing" else EPC_01
    service = TagLookupService(lambda: client, 10, events.append)
    try:
        service.start_session()
        with ThreadPoolExecutor(max_workers=4) as pool:
            accepted = list(pool.map(lambda i: service.submit(tag(epc, i % 2 + 1)), range(100)))
        assert sum(accepted) == 1
        wait_until(lambda: len(completed(events, epc)) == 1)
        assert not service.submit(tag(epc, 2))
        assert client.get_requests == [epc]
        assert client.post_requests == ([] if case == "missing" else [epc])
        expected = {
            "found": TagLookupStatus.FOUND,
            "already_read": TagLookupStatus.EXTRA_BOX,
            "missing": TagLookupStatus.NOT_FOUND,
            "post_error": TagLookupStatus.ERROR,
        }
        assert completed(events, epc)[0].result.status is expected[case]
    finally:
        service.close()


def test_new_session_allows_a_new_lookup_for_same_tag(tmp_path: Path) -> None:
    events: list[TagLookupEvent] = []
    service = TagLookupService(
        lambda: LocalCompatibilityClient(repository(tmp_path), "D01"), 10, events.append
    )
    try:
        first_session = service.start_session()
        service.submit(tag(EPC_01))
        wait_until(lambda: len(completed(events, EPC_01)) == 1)

        second_session = service.start_session()
        service.submit(tag(EPC_01))
        wait_until(lambda: len(completed(events, EPC_01)) == 2)

        assert second_session == first_session + 1
        assert sum(isinstance(event, TagLookupSessionStarted) for event in events) == 2
    finally:
        service.close()


@pytest.mark.parametrize("antennas", [(1, 1), (1, 2)])
def test_processes_multiple_epcs_with_individual_results(
    tmp_path: Path, antennas: tuple[int, int]
) -> None:
    events: list[TagLookupEvent] = []
    service = TagLookupService(
        lambda: LocalCompatibilityClient(repository(tmp_path), "D01"), 10, events.append
    )
    try:
        service.start_session()
        for epc, antenna in zip((EPC_01, EPC_02), antennas, strict=True):
            assert service.submit(tag(epc, antenna))

        wait_until(
            lambda: len(completed(events, EPC_01)) == 1 and len(completed(events, EPC_02)) == 1
        )

        results = {
            event.result.epc: event.result
            for event in events
            if isinstance(event, TagLookupChanged) and event.result.status is TagLookupStatus.FOUND
        }
        assert results[EPC_01].customer == f"Cliente {EPC_01}"
        assert results[EPC_02].order_number == f"Pedido {EPC_02}"
        assert completed(events, EPC_01)[0].key.antenna_id == antennas[0]
        assert completed(events, EPC_02)[0].key.antenna_id == antennas[1]
    finally:
        service.close()


def test_invalid_epc_is_ignored_without_lookup_or_visual_event(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    events: list[TagLookupEvent] = []
    service = TagLookupService(
        lambda: LocalCompatibilityClient(repository(tmp_path), "D01"), 10, events.append
    )
    try:
        service.start_session()

        with caplog.at_level("WARNING"):
            assert not service.submit(tag("INVALID-EPC"))

        assert not any(isinstance(event, TagLookupChanged) for event in events)
        assert "tag_lookup_invalid_epc_ignored" in caplog.text
    finally:
        service.close()


def test_unauthorized_epc_is_ignored_before_deduplication_and_backend(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    events: list[TagLookupEvent] = []
    client = LocalCompatibilityClient(repository(tmp_path), "D01")
    service = TagLookupService(
        lambda: client,
        10,
        events.append,
        epc_filter_provider=lambda: EpcFilterState(True, ("484C44",)),
    )
    try:
        service.start_session()
        with caplog.at_level("INFO"):
            assert not service.submit(tag(EPC_01))
        assert client.get_requests == []
        assert client.post_requests == []
        assert not any(isinstance(event, TagLookupChanged) for event in events)
        assert "tag_read_received" not in caplog.text
    finally:
        service.close()


def test_logs_every_received_tag_before_local_lookup(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    events: list[TagLookupEvent] = []
    service = TagLookupService(
        lambda: LocalCompatibilityClient(repository(tmp_path), "D01"), 10, events.append
    )
    received = TagRead(
        epc=EPC_MISSING,
        reader_id="reader-01",
        antenna_id=2,
        read_at=datetime(2026, 10, 6, 12, 34, 56, tzinfo=UTC),
        rssi=-47,
    )
    try:
        service.start_session()

        with caplog.at_level("INFO"):
            assert service.submit(received)

        assert "tag_read_received" in caplog.text
        assert "epc=4D495353494E47" in caplog.text
        assert "antenna=2" in caplog.text
        assert "rssi=-47" in caplog.text
        assert "read_at=2026-10-06T12:34:56+00:00" in caplog.text
    finally:
        service.close()


def test_stop_prevents_new_lookups(tmp_path: Path) -> None:
    events: list[TagLookupEvent] = []
    service = TagLookupService(
        lambda: LocalCompatibilityClient(repository(tmp_path), "D01"), 10, events.append
    )
    try:
        service.start_session()
        service.stop_accepting()

        assert not service.submit(tag(EPC_01))
        time.sleep(0.02)

        assert not any(isinstance(event, TagLookupChanged) for event in events)
    finally:
        service.close()


def test_epc_missing_other_dock_or_inactive_is_ignored_without_error(tmp_path: Path) -> None:
    events: list[TagLookupEvent] = []
    service = TagLookupService(
        lambda: LocalCompatibilityClient(repository(tmp_path), "D01"), 10, events.append
    )
    try:
        service.start_session()
        assert service.submit(tag(EPC_MISSING))
        assert service.submit(tag(EPC_OTHER_DOCK))
        assert service.submit(tag(EPC_INACTIVE))
        time.sleep(0.1)

        wait_until(
            lambda: (
                len(completed(events, EPC_MISSING)) == 1
                and len(completed(events, EPC_OTHER_DOCK)) == 1
                and len(completed(events, EPC_INACTIVE)) == 1
            )
        )
        assert all(
            completed(events, epc)[0].result.status is TagLookupStatus.NOT_FOUND
            for epc in (EPC_MISSING, EPC_OTHER_DOCK, EPC_INACTIVE)
        )
    finally:
        service.close()


def test_local_database_failure_marks_only_that_epc_as_error(tmp_path: Path) -> None:
    events: list[TagLookupEvent] = []
    repo = LocalTagRepository(tmp_path / "missing-schema.sqlite3")
    service = TagLookupService(lambda: LocalCompatibilityClient(repo, "D01"), 10, events.append)
    try:
        service.start_session()
        service.submit(tag(EPC_ERROR))
        wait_until(lambda: len(completed(events, EPC_ERROR)) == 1)

        result = completed(events, EPC_ERROR)[0].result
        assert result.status is TagLookupStatus.ERROR
        assert result.message == FRIENDLY_ERROR_MESSAGE
    finally:
        service.close()
