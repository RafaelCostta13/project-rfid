import threading
import time
from collections.abc import Callable
from datetime import UTC, datetime

import pytest

from rfid_reader.domain import (
    TagLookupChanged,
    TagLookupEvent,
    TagLookupResult,
    TagLookupSessionStarted,
    TagLookupStatus,
    TagRead,
)
from rfid_reader.integrations.sharepoint_client import (
    TagLookupClientError,
)
from rfid_reader.services.tag_lookup import FRIENDLY_ERROR_MESSAGE, TagLookupService

EPC_01 = "4550432D3031"
EPC_02 = "4550432D3032"
EPC_03 = "4550432D3033"
EPC_IN_FLIGHT = "494E2D464C49474854"
EPC_OLD = "4F4C44"
EPC_NEW = "4E4557"
EPC_QUEUED = "515545554544"
EPC_OVERFLOW = "4F564552464C4F57"
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
    raise AssertionError("condição assíncrona não foi atendida")


class RecordingClient:
    def __init__(self) -> None:
        self.epcs: list[str] = []

    def lookup(self, epc: str) -> TagLookupResult:
        self.epcs.append(epc)
        return TagLookupResult(
            epc,
            TagLookupStatus.FOUND,
            f"Encontrada {epc}",
            customer=f"Cliente {epc}",
            order_number=f"Pedido {epc}",
        )


class FailingClient:
    def __init__(self, error: Exception) -> None:
        self._error = error

    def lookup(self, epc: str) -> TagLookupResult:
        raise self._error


class BlockingClient:
    def __init__(self) -> None:
        self.started = threading.Event()
        self.release = threading.Event()
        self.epcs: list[str] = []

    def lookup(self, epc: str) -> TagLookupResult:
        self.epcs.append(epc)
        self.started.set()
        if not self.release.wait(1.0):
            raise AssertionError("teste não liberou o cliente")
        return TagLookupResult(epc, TagLookupStatus.FOUND, "Encontrada")


def completed(events: list[TagLookupEvent], epc: str) -> list[TagLookupChanged]:
    return [
        event
        for event in events
        if isinstance(event, TagLookupChanged)
        and event.result.epc == epc
        and event.result.status is not TagLookupStatus.CONSULTING
    ]


def test_deduplicates_same_reader_antenna_and_epc_in_one_session() -> None:
    client = RecordingClient()
    events: list[TagLookupEvent] = []
    service = TagLookupService(client, 10, events.append)
    try:
        service.start_session()

        assert service.submit(tag(EPC_01))
        assert not service.submit(tag(EPC_01))
        wait_until(lambda: len(completed(events, EPC_01)) == 1)

        assert client.epcs == [EPC_01]
    finally:
        service.close()


def test_same_epc_on_another_antenna_has_an_independent_lookup() -> None:
    client = RecordingClient()
    events: list[TagLookupEvent] = []
    service = TagLookupService(client, 10, events.append)
    try:
        service.start_session()

        service.submit(tag(EPC_01, 1))
        service.submit(tag(EPC_01, 2))
        wait_until(lambda: len(completed(events, EPC_01)) == 2)

        assert client.epcs == [EPC_01, EPC_01]
    finally:
        service.close()


def test_new_session_allows_a_new_lookup_for_same_tag() -> None:
    client = RecordingClient()
    events: list[TagLookupEvent] = []
    service = TagLookupService(client, 10, events.append)
    try:
        first_session = service.start_session()
        service.submit(tag(EPC_01))
        wait_until(lambda: len(client.epcs) == 1)

        second_session = service.start_session()
        service.submit(tag(EPC_01))
        wait_until(lambda: len(client.epcs) == 2)

        assert second_session == first_session + 1
        assert sum(isinstance(event, TagLookupSessionStarted) for event in events) == 2
    finally:
        service.close()


def test_processes_multiple_epcs_with_individual_results() -> None:
    client = RecordingClient()
    events: list[TagLookupEvent] = []
    service = TagLookupService(client, 10, events.append)
    try:
        service.start_session()
        for epc in (EPC_01, EPC_02, EPC_03):
            service.submit(tag(epc))

        wait_until(
            lambda: (
                sum(
                    isinstance(event, TagLookupChanged)
                    and event.result.status is TagLookupStatus.FOUND
                    for event in events
                )
                == 3
            )
        )

        assert client.epcs == [EPC_01, EPC_02, EPC_03]
        results = {
            event.result.epc: event.result
            for event in events
            if isinstance(event, TagLookupChanged) and event.result.status is TagLookupStatus.FOUND
        }
        assert results[EPC_01].customer == f"Cliente {EPC_01}"
        assert results[EPC_02].customer == f"Cliente {EPC_02}"
        assert results[EPC_03].order_number == f"Pedido {EPC_03}"
    finally:
        service.close()


def test_multiple_hex_epcs_are_forwarded_without_conversion() -> None:
    client = RecordingClient()
    events: list[TagLookupEvent] = []
    service = TagLookupService(client, 10, events.append)
    try:
        service.start_session()
        service.submit(tag("5441472D3031"))
        service.submit(tag("5441472D3032"))

        wait_until(
            lambda: (
                len(completed(events, "5441472D3031")) == 1
                and len(completed(events, "5441472D3032")) == 1
            )
        )

        assert completed(events, "5441472D3031")[0].result.epc == "5441472D3031"
        assert completed(events, "5441472D3032")[0].result.epc == "5441472D3032"
        assert client.epcs == ["5441472D3031", "5441472D3032"]
    finally:
        service.close()


def test_invalid_epc_is_ignored_without_lookup_or_visual_event(
    caplog: pytest.LogCaptureFixture,
) -> None:
    client = RecordingClient()
    events: list[TagLookupEvent] = []
    service = TagLookupService(client, 10, events.append)
    try:
        service.start_session()

        with caplog.at_level("WARNING"):
            assert not service.submit(tag("INVALID-EPC"))

        assert client.epcs == []
        assert not any(isinstance(event, TagLookupChanged) for event in events)
        assert "tag_lookup_invalid_epc_ignored" in caplog.text
    finally:
        service.close()


def test_stop_prevents_new_lookups() -> None:
    client = RecordingClient()
    events: list[TagLookupEvent] = []
    service = TagLookupService(client, 10, events.append)
    try:
        service.start_session()
        service.stop_accepting()

        assert not service.submit(tag(EPC_01))
        time.sleep(0.02)

        assert client.epcs == []
        assert not any(isinstance(event, TagLookupChanged) for event in events)
    finally:
        service.close()


def test_in_flight_lookup_can_finish_after_stop() -> None:
    client = BlockingClient()
    events: list[TagLookupEvent] = []
    service = TagLookupService(client, 10, events.append)
    try:
        session_id = service.start_session()
        service.submit(tag(EPC_IN_FLIGHT))
        assert client.started.wait(1.0)

        service.stop_accepting()
        client.release.set()
        wait_until(lambda: len(completed(events, EPC_IN_FLIGHT)) == 1)

        assert completed(events, EPC_IN_FLIGHT)[0].session_id == session_id
        assert completed(events, EPC_IN_FLIGHT)[0].result.status is TagLookupStatus.FOUND
    finally:
        client.release.set()
        service.close()


def test_old_session_result_does_not_update_new_session() -> None:
    client = BlockingClient()
    events: list[TagLookupEvent] = []
    service = TagLookupService(client, 10, events.append)
    try:
        old_session = service.start_session()
        service.submit(tag(EPC_OLD))
        assert client.started.wait(1.0)

        new_session = service.start_session()
        service.submit(tag(EPC_NEW))
        client.release.set()
        wait_until(lambda: len(completed(events, EPC_NEW)) == 1)

        assert old_session != new_session
        assert completed(events, EPC_OLD) == []
        assert completed(events, EPC_NEW)[0].session_id == new_session
    finally:
        client.release.set()
        service.close()


def test_queue_full_marks_affected_epc_as_error_without_blocking() -> None:
    client = BlockingClient()
    events: list[TagLookupEvent] = []
    service = TagLookupService(client, 1, events.append)
    try:
        service.start_session()
        service.submit(tag(EPC_IN_FLIGHT))
        assert client.started.wait(1.0)
        service.submit(tag(EPC_QUEUED))

        assert not service.submit(tag(EPC_OVERFLOW))

        errors = completed(events, EPC_OVERFLOW)
        assert len(errors) == 1
        assert errors[0].result.status is TagLookupStatus.ERROR
        assert errors[0].result.message == FRIENDLY_ERROR_MESSAGE
    finally:
        client.release.set()
        service.close()


def test_client_failure_marks_only_that_epc_as_error() -> None:
    events: list[TagLookupEvent] = []
    service = TagLookupService(
        FailingClient(TagLookupClientError("network unavailable")),
        10,
        events.append,
    )
    try:
        service.start_session()
        service.submit(tag(EPC_ERROR))
        wait_until(lambda: len(completed(events, EPC_ERROR)) == 1)

        result = completed(events, EPC_ERROR)[0].result
        assert result.status is TagLookupStatus.ERROR
        assert result.message == FRIENDLY_ERROR_MESSAGE
    finally:
        service.close()
