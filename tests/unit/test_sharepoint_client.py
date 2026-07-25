import json
from urllib.request import Request

import pytest

import rfid_reader.integrations.sharepoint_client as sharepoint_module
from rfid_reader.domain import TagLookupStatus
from rfid_reader.integrations.sharepoint_client import (
    HttpResponse,
    SharePointLookupClient,
    TagLookupHttpError,
    TagLookupResponseError,
    TagLookupTimeoutError,
)


def json_response(payload: object, status_code: int = 200) -> HttpResponse:
    return HttpResponse(status_code, json.dumps(payload).encode("utf-8"))


def client_with(
    response: HttpResponse,
    capture: list[tuple[Request, float]] | None = None,
) -> SharePointLookupClient:
    def transport(request: Request, timeout: float) -> HttpResponse:
        if capture is not None:
            capture.append((request, timeout))
        return response

    return SharePointLookupClient(
        "https://example.test/lookup?token=fake",
        7.5,
        transport=transport,
    )


def test_sends_post_json_content_type_and_timeout() -> None:
    captured: list[tuple[Request, float]] = []
    client = client_with(
        json_response(
            {
                "sucesso": True,
                "mensagem": "Etiqueta encontrada",
                "epc": "EPC-01",
            }
        ),
        captured,
    )

    result = client.lookup("EPC-01")

    request, timeout = captured[0]
    assert request.get_method() == "POST"
    assert request.get_header("Content-type") == "application/json"
    assert json.loads(request.data or b"") == {"epc": "EPC-01"}
    assert timeout == 7.5
    assert result.status is TagLookupStatus.FOUND
    assert result.message == "Etiqueta encontrada"


def test_sends_original_hex_epc_without_ascii_conversion() -> None:
    captured: list[tuple[Request, float]] = []
    epc = "484C44303130313237353835"
    client = client_with(
        json_response(
            {
                "sucesso": True,
                "mensagem": "Etiqueta encontrada",
                "epc": epc,
            }
        ),
        captured,
    )

    result = client.lookup(epc)

    request, _ = captured[0]
    assert json.loads(request.data or b"") == {"epc": epc}
    assert result.epc == epc
    assert result.tag == ""


def test_extracts_additional_fields_from_power_automate_body() -> None:
    client = client_with(
        json_response(
            {
                "statusCode": "200",
                "headers": {"Content-Type": "application/json"},
                "body": {
                    "sucesso": True,
                    "mensagem": "EPC localizado com sucesso",
                    "epc": "EPC-01",
                    "cliente": "HARLEY DAVIDSON",
                    "notaFiscal": "00127585",
                    "pedido": "00100066805",
                    "volume": "1/2",
                    "doca": "",
                },
            }
        )
    )

    result = client.lookup("EPC-01")

    assert result.status is TagLookupStatus.FOUND
    assert result.message == "EPC localizado com sucesso"
    assert result.customer == "HARLEY DAVIDSON"
    assert result.invoice_number == "00127585"
    assert result.order_number == "00100066805"
    assert result.volume == "1/2"
    assert result.dock == ""


def test_keeps_backward_compatibility_with_payload_at_root() -> None:
    client = client_with(
        json_response(
            {
                "sucesso": True,
                "mensagem": "Encontrada",
                "epc": "EPC-01",
                "cliente": "Cliente legado",
            }
        )
    )

    result = client.lookup("EPC-01")

    assert result.status is TagLookupStatus.FOUND
    assert result.customer == "Cliente legado"


def test_missing_and_null_additional_fields_become_empty_text() -> None:
    client = client_with(
        json_response(
            {
                "body": {
                    "sucesso": True,
                    "mensagem": "Encontrada",
                    "epc": "EPC-01",
                    "cliente": None,
                    "notaFiscal": None,
                    "doca": None,
                }
            }
        )
    )

    result = client.lookup("EPC-01")

    assert result.customer == ""
    assert result.invoice_number == ""
    assert result.order_number == ""
    assert result.volume == ""
    assert result.dock == ""


def test_numeric_additional_fields_are_normalized_as_text() -> None:
    client = client_with(
        json_response(
            {
                "body": {
                    "sucesso": False,
                    "mensagem": "Não localizada",
                    "epc": "EPC-01",
                    "notaFiscal": 127585,
                    "pedido": 100066805,
                    "volume": 2,
                    "doca": 4,
                }
            }
        )
    )

    result = client.lookup("EPC-01")

    assert result.status is TagLookupStatus.NOT_FOUND
    assert result.invoice_number == "127585"
    assert result.order_number == "100066805"
    assert result.volume == "2"
    assert result.dock == "4"


@pytest.mark.parametrize("success", [True, "true", "True", 1, "1"])
def test_normalizes_supported_true_values(success: object) -> None:
    client = client_with(
        json_response(
            {
                "sucesso": success,
                "mensagem": "Encontrada",
                "epc": "EPC-01",
            }
        )
    )

    assert client.lookup("EPC-01").status is TagLookupStatus.FOUND


@pytest.mark.parametrize("success", [False, "false", "False", 0, "0", "other", None])
def test_treats_other_success_values_as_not_found(success: object) -> None:
    client = client_with(
        json_response(
            {
                "sucesso": success,
                "mensagem": "Etiqueta não localizada",
                "epc": "EPC-01",
            }
        )
    )

    result = client.lookup("EPC-01")

    assert result.status is TagLookupStatus.NOT_FOUND
    assert result.message == "Etiqueta não localizada"


def test_rejects_non_success_http_status() -> None:
    client = client_with(HttpResponse(503, b"unavailable"))

    with pytest.raises(TagLookupHttpError) as raised:
        client.lookup("EPC-01")

    assert raised.value.status_code == 503


def test_propagates_transport_timeout() -> None:
    def timeout(request: Request, timeout_seconds: float) -> HttpResponse:
        raise TagLookupTimeoutError("timeout")

    client = SharePointLookupClient(
        "https://example.test/lookup",
        1.0,
        transport=timeout,
    )

    with pytest.raises(TagLookupTimeoutError):
        client.lookup("EPC-01")


def test_converts_urlopen_timeout_to_known_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def timeout(request: Request, timeout: float) -> HttpResponse:
        raise TimeoutError

    monkeypatch.setattr(sharepoint_module, "urlopen", timeout)
    client = SharePointLookupClient("https://example.test/lookup", 1.0)

    with pytest.raises(TagLookupTimeoutError):
        client.lookup("EPC-01")


def test_rejects_invalid_json() -> None:
    client = client_with(HttpResponse(200, b"not-json"))

    with pytest.raises(TagLookupResponseError, match="JSON"):
        client.lookup("EPC-01")


@pytest.mark.parametrize("body", [None, "not-an-object", []])
def test_rejects_invalid_body_structure(body: object) -> None:
    client = client_with(json_response({"statusCode": "200", "body": body}))

    with pytest.raises(TagLookupResponseError, match="body"):
        client.lookup("EPC-01")


def test_envelope_without_body_or_lookup_fields_is_invalid() -> None:
    client = client_with(
        json_response(
            {
                "statusCode": "200",
                "headers": {"Content-Type": "application/json"},
            }
        )
    )

    with pytest.raises(TagLookupResponseError, match="campos obrigatórios"):
        client.lookup("EPC-01")


@pytest.mark.parametrize("missing_field", ["sucesso", "mensagem", "epc"])
def test_rejects_missing_required_fields(missing_field: str) -> None:
    payload: dict[str, object] = {
        "sucesso": True,
        "mensagem": "Encontrada",
        "epc": "EPC-01",
    }
    del payload[missing_field]
    client = client_with(json_response(payload))

    with pytest.raises(TagLookupResponseError, match=missing_field):
        client.lookup("EPC-01")


def test_rejects_response_for_a_different_epc() -> None:
    client = client_with(
        json_response(
            {
                "body": {
                    "sucesso": True,
                    "mensagem": "Encontrada",
                    "epc": "OTHER-EPC",
                    "cliente": "Cliente incorreto",
                }
            }
        )
    )

    with pytest.raises(TagLookupResponseError, match="diverge"):
        client.lookup("EPC-01")
