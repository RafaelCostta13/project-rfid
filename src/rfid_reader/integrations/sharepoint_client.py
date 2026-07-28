"""Cliente HTTP para o fluxo de consulta no Power Automate."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from json import JSONDecodeError
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from rfid_reader.domain import TagLookupResult, TagLookupStatus


class TagLookupClientError(RuntimeError):
    """Falha esperada ao consultar ou interpretar o endpoint."""


class TagLookupTimeoutError(TagLookupClientError):
    """O endpoint não respondeu dentro do limite."""


class TagLookupHttpError(TagLookupClientError):
    """O endpoint respondeu com estado HTTP não aceito."""

    def __init__(self, status_code: int) -> None:
        super().__init__(f"resposta HTTP {status_code}")
        self.status_code = status_code


class TagLookupResponseError(TagLookupClientError):
    """A resposta não respeita o contrato esperado."""


class TagLookupClient(Protocol):
    """Contrato consumido pelo serviço de consultas."""

    def lookup(self, epc: str) -> TagLookupResult: ...


@dataclass(frozen=True, slots=True)
class HttpResponse:
    """Resposta mínima usada para isolar urllib nos testes."""

    status_code: int
    body: bytes


HttpTransport = Callable[[Request, float], HttpResponse]


def _urllib_transport(request: Request, timeout_seconds: float) -> HttpResponse:
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            return HttpResponse(
                status_code=response.getcode(),
                body=response.read(),
            )
    except HTTPError as error:
        raise TagLookupHttpError(error.code) from error
    except TimeoutError as error:
        raise TagLookupTimeoutError("timeout na consulta") from error
    except URLError as error:
        if isinstance(error.reason, TimeoutError):
            raise TagLookupTimeoutError("timeout na consulta") from error
        raise TagLookupClientError("falha de rede na consulta") from error
    except OSError as error:
        raise TagLookupClientError("falha de rede na consulta") from error


def _normalize_success(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        if value == 1:
            return True
        if value == 0:
            return False
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1"}:
            return True
        if normalized in {"false", "0"}:
            return False
    raise TagLookupResponseError("o campo 'sucesso' deve ser booleano")


def _lookup_payload(document: dict[str, object]) -> dict[str, object]:
    if "body" not in document:
        return document
    body = document["body"]
    if not isinstance(body, dict):
        raise TagLookupResponseError("o campo body deve ser um objeto JSON")
    return body


def _optional_text(payload: dict[str, object], field: str) -> str:
    value = payload.get(field)
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(value)
    raise TagLookupResponseError(f"o campo {field} deve ser texto, número ou nulo")


class SharePointLookupClient:
    """Envia EPCs ao gatilho HTTP sem revelar a URL nos logs."""

    def __init__(
        self,
        endpoint_url: str,
        timeout_seconds: float,
        *,
        transport: HttpTransport = _urllib_transport,
    ) -> None:
        self._endpoint_url = endpoint_url
        self._timeout_seconds = timeout_seconds
        self._transport = transport

    def lookup(self, epc: str) -> TagLookupResult:
        """Consulta um EPC e valida integralmente a resposta relacionada."""

        request = Request(
            self._endpoint_url,
            data=json.dumps({"epc": epc}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        response = self._transport(request, self._timeout_seconds)
        if not 200 <= response.status_code < 300:
            raise TagLookupHttpError(response.status_code)

        try:
            document = json.loads(response.body.decode("utf-8"))
        except (UnicodeDecodeError, JSONDecodeError) as error:
            raise TagLookupResponseError("resposta JSON inválida") from error
        if not isinstance(document, dict):
            raise TagLookupResponseError("a resposta JSON deve ser um objeto")
        payload = _lookup_payload(document)

        missing = {"sucesso", "mensagem", "epc"} - payload.keys()
        if missing:
            fields = ",".join(sorted(missing))
            raise TagLookupResponseError(f"campos obrigatórios ausentes: {fields}")

        response_epc = payload["epc"]
        message = payload["mensagem"]
        if not isinstance(response_epc, str) or not isinstance(message, str):
            raise TagLookupResponseError("epc e mensagem devem ser textos")
        if response_epc != epc:
            raise TagLookupResponseError("EPC retornado diverge do EPC consultado")

        found = _normalize_success(payload["sucesso"])
        return TagLookupResult(
            epc=epc,
            status=TagLookupStatus.FOUND if found else TagLookupStatus.NOT_FOUND,
            message=message,
            customer=_optional_text(payload, "cliente"),
            invoice_number=_optional_text(payload, "notaFiscal"),
            order_number=_optional_text(payload, "pedido"),
            volume=_optional_text(payload, "volume"),
            dock=_optional_text(payload, "doca"),
        )
