import json
from pathlib import Path
from urllib.request import Request

import pytest

from rfid_reader.config import Settings, load_config
from rfid_reader.domain import ConnectionKind, ConnectionStatus
from rfid_reader.integrations.backend_client import (
    BackendClientError,
    BackendRFIDClient,
    HttpResponse,
)
from rfid_reader.services.backend import BackendConfigurationService, BackendHealthChecker
from rfid_reader.services.reader_configuration import DotEnvReaderConfigurationStore


def settings() -> Settings:
    return Settings(
        reader_host="192.168.0.100",
        reader_port=5084,
        reader_name="reader",
        antennas=(1,),
        deduplication_window_seconds=2.0,
        connection_timeout_seconds=3.0,
        status_check_interval_seconds=5.0,
        sharepoint_sync_url="https://example.test/sync",
        sharepoint_sync_timeout_seconds=10.0,
        tag_lookup_queue_size=100,
        local_database_path=Path("local.sqlite3"),
        log_level="INFO",
    )


def response(status: int, payload: object) -> HttpResponse:
    return HttpResponse(status, json.dumps(payload).encode())


def test_health_ok_uses_normalized_endpoint_and_one_request() -> None:
    requests: list[Request] = []

    def transport(request: Request, timeout: float) -> HttpResponse:
        requests.append(request)
        assert timeout == 2.5
        return response(200, {"status": "ok", "database": "ok"})

    health = BackendRFIDClient(" https://backend.test/ ", 2.5, transport=transport).health()

    assert health.system_ok
    assert requests[0].full_url == "https://backend.test/api/v1/health"
    assert len(requests) == 1


def test_health_uses_only_system_field_for_the_single_status() -> None:
    client = BackendRFIDClient(
        "https://backend.test",
        3.0,
        transport=lambda request, timeout: response(
            200, {"status": "ok", "database": "unavailable"}
        ),
    )

    assert client.health().system_ok


@pytest.mark.parametrize(
    ("status", "payload"),
    [
        (503, {"status": "error", "database": "unavailable"}),
        (200, {"foo": "bar"}),
        (200, b"not-json"),
    ],
)
def test_unhealthy_or_invalid_health_is_not_reported_as_ok(status: int, payload: object) -> None:
    body = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
    client = BackendRFIDClient(
        "https://backend.test",
        3.0,
        transport=lambda request, timeout: HttpResponse(status, body),
    )

    if status == 200:
        with pytest.raises(BackendClientError):
            client.health()
    else:
        health = client.health()
        assert not health.system_ok


def test_timeout_and_empty_url_are_unavailable_without_invalid_request() -> None:
    calls = 0

    def transport(request: Request, timeout: float) -> HttpResponse:
        nonlocal calls
        calls += 1
        raise TimeoutError

    health = BackendRFIDClient("", 3.0, transport=transport).health()
    assert not health.system_ok
    with pytest.raises(BackendClientError):
        BackendRFIDClient("https://backend.test", 3.0, transport=transport).health()
    assert calls == 1


def test_checker_maps_one_health_response_to_system_and_database() -> None:
    calls = 0

    def factory() -> BackendRFIDClient:
        nonlocal calls
        calls += 1
        return BackendRFIDClient(
            "https://backend.test",
            3.0,
            transport=lambda request, timeout: response(
                503, {"status": "error", "database": "unavailable"}
            ),
        )

    result = BackendHealthChecker(factory).check()

    assert result == {
        ConnectionKind.SYSTEM: ConnectionStatus.ERROR,
    }
    assert calls == 1


def test_backend_url_is_persisted_with_existing_dotenv_store(tmp_path: Path) -> None:
    path = tmp_path / ".env"
    path.write_text("SHAREPOINT_SYNC_URL=https://example.test/sync\n", encoding="utf-8")
    service = BackendConfigurationService(settings(), DotEnvReaderConfigurationStore(path))

    assert service.save(" https://new-backend.test/ ")
    assert service.current() == "https://new-backend.test/"
    assert (
        load_config(
            {
                "SHAREPOINT_SYNC_URL": "https://example.test/sync",
                "RFID_BACKEND_BASE_URL": service.current(),
            }
        ).backend_base_url
        == "https://new-backend.test/"
    )


def backend_record(epc: str = "E280691500005029EEA6A275") -> dict[str, object]:
    return {
        "datahora": "2026-10-06T14:41:25.000Z",
        "volume": "2/4",
        "pedido": "0007819215",
        "notafiscal": "1198780",
        "destinatario": "EURO IMPORT COMERCIO E SERVICOS LTDA",
        "endereco": "AV DAS NACOES UNIDAS",
        "numero": "17381",
        "cidade": "SAO PAULO",
        "uf": "SP",
        "doca": "DOCA 35",
        "epc": epc,
        "tag": None,
        "fornecedor": "BMW",
        "status": "pendente",
        "first_read_at": None,
        "last_read_at": None,
        "read_count": 15,
    }


def test_get_rfid_record_parses_new_contract_and_preserves_strings() -> None:
    requests: list[Request] = []

    def transport(request: Request, timeout: float) -> HttpResponse:
        requests.append(request)
        return response(200, {"found": True, "data": backend_record()})

    record = BackendRFIDClient("https://backend.test/", 3.0, transport=transport).get_rfid_record(
        "  e280691500005029eea6a275  "
    )

    assert record is not None
    assert record.epc == "E280691500005029EEA6A275"
    assert record.pedido == "0007819215"
    assert record.tag is None
    assert record.read_count == 15
    assert requests[0].full_url.endswith("/api/v1/rfid_records/E280691500005029EEA6A275")


def test_get_rfid_record_treats_documented_404_as_business_not_found() -> None:
    client = BackendRFIDClient(
        "https://backend.test",
        3.0,
        transport=lambda request, timeout: response(
            404,
            {
                "found": False,
                "error": "epc_not_found",
                "epc": "E280691500005029EEA6A275",
            },
        ),
    )

    assert client.get_rfid_record("E280691500005029EEA6A275") is None


@pytest.mark.parametrize(
    "payload",
    [
        {"found": False, "data": backend_record()},
        {"found": True, "data": {**backend_record(), "epc": "OTHER"}},
        {"found": True, "data": {**backend_record(), "read_count": "15"}},
    ],
)
def test_get_rfid_record_rejects_inconsistent_contract(payload: dict[str, object]) -> None:
    client = BackendRFIDClient(
        "https://backend.test",
        3.0,
        transport=lambda request, timeout: response(200, payload),
    )

    with pytest.raises(BackendClientError):
        client.get_rfid_record("E280691500005029EEA6A275")


def test_create_rfid_read_posts_only_normalized_epc_and_parses_success() -> None:
    requests: list[Request] = []

    def transport(request: Request, timeout: float) -> HttpResponse:
        requests.append(request)
        return response(
            200,
            {
                "success": True,
                "epc": "E280691500005029EEA6A275",
                "first_read": False,
                "duplicate": True,
                "status": "lido",
                "read_count": 2,
                "first_read_at": "2026-10-07T10:00:00Z",
                "last_read_at": "2026-10-07T11:00:00Z",
            },
        )

    result = BackendRFIDClient("https://backend.test", 3.0, transport=transport).create_rfid_read(
        " e280691500005029eea6a275 "
    )

    assert result.success
    assert result.duplicate
    assert result.read_count == 2
    assert requests[0].full_url == "https://backend.test/api/v1/rfid_reads"
    assert requests[0].data == b'{"epc": "E280691500005029EEA6A275"}'
    assert set(json.loads(requests[0].data)) == {"epc"}


@pytest.mark.parametrize(
    ("status", "payload"),
    [
        (404, {"success": False, "error": "epc_not_found"}),
        (422, {"success": False, "error": "epc_required"}),
        (200, {"success": False}),
        (200, {"success": True, "epc": "OTHER"}),
    ],
)
def test_create_rfid_read_rejects_unsuccessful_or_inconsistent_response(
    status: int, payload: dict[str, object]
) -> None:
    client = BackendRFIDClient(
        "https://backend.test",
        3.0,
        transport=lambda request, timeout: response(status, payload),
    )

    with pytest.raises(BackendClientError):
        client.create_rfid_read("E280691500005029EEA6A275")
