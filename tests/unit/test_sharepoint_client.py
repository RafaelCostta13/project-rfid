import json
from urllib.request import Request

import pytest

import rfid_reader.integrations.sharepoint_sync_client as sync_module
from rfid_reader.integrations.sharepoint_sync_client import (
    HttpResponse,
    PowerAutomateSyncClient,
    SyncHttpError,
    SyncResponseError,
    SyncTimeoutError,
)


def json_response(payload: object, status_code: int = 200) -> HttpResponse:
    return HttpResponse(status_code, json.dumps(payload).encode("utf-8"))


def client_with(
    response: HttpResponse,
    capture: list[tuple[Request, float]] | None = None,
) -> PowerAutomateSyncClient:
    def transport(request: Request, timeout: float) -> HttpResponse:
        if capture is not None:
            capture.append((request, timeout))
        return response

    return PowerAutomateSyncClient(
        "https://example.test/sync?token=fake",
        7.5,
        transport=transport,
    )


def valid_payload(count: int = 1) -> dict[str, object]:
    items: list[dict[str, object]] = []
    if count:
        items.append(
            {
                "sharepointId": 10,
                "status": "Ativo",
                "cliente": "CLIENTE ALFA",
                "notaFiscal": "100001",
                "volume": "1/3",
                "pedido": "500001",
                "doca": "D01",
                "epc": "484C443030303030303031",
                "modified": "2026-10-05T10:10:00Z",
            }
        )
    return {
        "success": True,
        "syncUntil": "2026-10-05T10:15:00Z",
        "count": count,
        "items": items,
    }


def test_sends_only_dock_and_modified_since_with_timeout() -> None:
    captured: list[tuple[Request, float]] = []
    client = client_with(json_response(valid_payload()), captured)

    result = client.sync("D01", "2026-10-05T10:00:00Z")

    request, timeout = captured[0]
    payload = json.loads(request.data or b"")
    assert request.get_method() == "POST"
    assert request.get_header("Content-type") == "application/json"
    assert payload == {"doca": "D01", "modifiedSince": "2026-10-05T10:00:00Z"}
    assert "epc" not in payload
    assert timeout == 7.5
    assert result.sync_until == "2026-10-05T10:15:00Z"
    assert result.items[0].sharepoint_id == 10
    assert result.items[0].epc == "484C443030303030303031"


def test_accepts_empty_incremental_response() -> None:
    client = client_with(json_response(valid_payload(0)))

    result = client.sync("D01", "2026-10-05T10:15:00Z")

    assert result.sync_until == "2026-10-05T10:15:00Z"
    assert result.items == ()


def test_extracts_payload_from_power_automate_body_string() -> None:
    client = client_with(json_response({"body": json.dumps(valid_payload())}))

    result = client.sync("D01", "")

    assert result.items[0].customer == "CLIENTE ALFA"


def test_accepts_power_automate_stringified_scalar_values() -> None:
    payload = valid_payload()
    payload["success"] = "true"
    payload["count"] = "1"
    item = payload["items"][0]
    assert isinstance(item, dict)
    item["sharepointId"] = "10"
    payload["items"] = json.dumps(payload["items"])
    client = client_with(json_response({"body": payload}))

    result = client.sync("D01", "")

    assert result.items[0].sharepoint_id == 10
    assert result.items[0].epc == "484C443030303030303031"


def test_accepts_direct_power_automate_item_list_without_sync_envelope() -> None:
    item = {
        "sharepointId": 10,
        "status": "Ativo",
        "cliente": "CLIENTE ALFA",
        "notafiscal": "100001",
        "volume": "1/3",
        "pedido": "500001",
        "doca": "D01",
        "epc": "484C443030303030303031",
        "modified": "2026-10-05T10:10:00Z",
    }
    client = client_with(json_response([item]))

    result = client.sync("D01", "")

    assert result.sync_until == "2026-10-05T10:10:00Z"
    assert len(result.items) == 1
    assert result.items[0].invoice_number == "100001"


@pytest.mark.parametrize(
    "payload",
    [
        {"success": False, "syncUntil": "T", "count": 0, "items": []},
        {"success": True, "syncUntil": "T", "count": 1, "items": []},
        {"success": True, "syncUntil": "T", "count": 0, "items": {}},
        {"success": True, "count": 0, "items": []},
        {"success": True, "syncUntil": "T", "count": 1, "items": [{}]},
    ],
)
def test_rejects_invalid_payloads(payload: object) -> None:
    client = client_with(json_response(payload))

    with pytest.raises(SyncResponseError):
        client.sync("D01", "")


def test_rejects_non_success_http_status() -> None:
    client = client_with(HttpResponse(503, b"unavailable"))

    with pytest.raises(SyncHttpError) as raised:
        client.sync("D01", "")

    assert raised.value.status_code == 503


def test_converts_urlopen_timeout_to_known_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def timeout(request: Request, timeout: float) -> HttpResponse:
        raise TimeoutError

    monkeypatch.setattr(sync_module, "urlopen", timeout)
    client = PowerAutomateSyncClient("https://example.test/sync", 1.0)

    with pytest.raises(SyncTimeoutError):
        client.sync("D01", "")


def test_rejects_invalid_json() -> None:
    client = client_with(HttpResponse(200, b"not-json"))

    with pytest.raises(SyncResponseError, match="JSON"):
        client.sync("D01", "")
