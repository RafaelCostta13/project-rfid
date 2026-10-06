"""Cliente HTTP para sincronização Power Automate/SharePoint."""

from __future__ import annotations

import json
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from json import JSONDecodeError
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from rfid_reader.domain import LocalTagRecord


class SyncClientError(RuntimeError):
    """Falha esperada ao sincronizar ou interpretar o endpoint."""


class SyncTimeoutError(SyncClientError):
    """O endpoint não respondeu dentro do limite."""


class SyncHttpError(SyncClientError):
    """O endpoint respondeu com estado HTTP não aceito."""

    def __init__(self, status_code: int) -> None:
        super().__init__(f"resposta HTTP {status_code}")
        self.status_code = status_code


class SyncResponseError(SyncClientError):
    """A resposta não respeita o contrato esperado."""


class SyncClient(Protocol):
    """Contrato do endpoint remoto de sincronização."""

    def sync(self, dock: str, modified_since: str) -> SyncPayload: ...


@dataclass(frozen=True, slots=True)
class HttpResponse:
    """Resposta mínima usada para isolar urllib nos testes."""

    status_code: int
    body: bytes


@dataclass(frozen=True, slots=True)
class SyncPayload:
    """Resposta remota validada antes de qualquer gravação local."""

    sync_until: str
    items: Sequence[LocalTagRecord]


HttpTransport = Callable[[Request, float], HttpResponse]


def _urllib_transport(request: Request, timeout_seconds: float) -> HttpResponse:
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            return HttpResponse(
                status_code=response.getcode(),
                body=response.read(),
            )
    except HTTPError as error:
        raise SyncHttpError(error.code) from error
    except TimeoutError as error:
        raise SyncTimeoutError("timeout na sincronização") from error
    except URLError as error:
        if isinstance(error.reason, TimeoutError):
            raise SyncTimeoutError("timeout na sincronização") from error
        raise SyncClientError("falha de rede na sincronização") from error
    except OSError as error:
        raise SyncClientError("falha de rede na sincronização") from error


def _payload_document(document: dict[str, object]) -> dict[str, object]:
    if "body" not in document:
        return document
    body = document["body"]
    if isinstance(body, str):
        try:
            decoded = json.loads(body)
        except JSONDecodeError as error:
            raise SyncResponseError("o campo body deve ser JSON válido") from error
        body = decoded
    if not isinstance(body, dict):
        raise SyncResponseError("o campo body deve ser um objeto JSON")
    return body


def _payload_from_document(document: object) -> dict[str, object]:
    if isinstance(document, list):
        return {
            "success": True,
            "syncUntil": _sync_until_from_items(document),
            "count": len(document),
            "items": document,
        }
    if not isinstance(document, dict):
        raise SyncResponseError("a resposta JSON deve ser um objeto ou lista")
    payload = _payload_document(document)
    if "success" not in payload and "items" not in payload and "body" not in payload:
        return {
            "success": True,
            "syncUntil": _sync_until_from_items([payload]),
            "count": 1,
            "items": [payload],
        }
    return payload


def _sync_until_from_items(items: Sequence[object]) -> str:
    modified_values = [
        modified
        for item in items
        if isinstance(item, dict) and isinstance((modified := item.get("modified")), str)
    ]
    if modified_values:
        return max(modified_values)
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _required_text(payload: dict[str, object], field: str) -> str:
    value = payload.get(field)
    if isinstance(value, str):
        return value
    raise SyncResponseError(f"o campo {field} deve ser texto")


def _optional_text(payload: dict[str, object], field: str) -> str:
    value = payload.get(field)
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(value)
    raise SyncResponseError(f"o campo {field} deve ser texto, número ou nulo")


def _optional_text_any(payload: dict[str, object], *fields: str) -> str:
    for field in fields:
        if field in payload:
            return _optional_text(payload, field)
    return ""


def _required_int(payload: dict[str, object], field: str) -> int:
    value = payload.get(field)
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value)
    raise SyncResponseError(f"o campo {field} deve ser inteiro")


def _required_true(payload: dict[str, object]) -> None:
    value = payload.get("success")
    if value is True:
        return
    if isinstance(value, int) and not isinstance(value, bool) and value == 1:
        return
    if isinstance(value, str) and value.strip().lower() in {"true", "1"}:
        return
    raise SyncResponseError("o campo success deve ser true")


def _items(payload: dict[str, object]) -> list[object]:
    value = payload.get("items")
    if isinstance(value, str):
        try:
            decoded = json.loads(value)
        except JSONDecodeError as error:
            raise SyncResponseError("o campo items deve ser JSON válido") from error
        value = decoded
    if isinstance(value, list):
        return value
    raise SyncResponseError("o campo items deve ser uma lista")


def _record(item: object) -> LocalTagRecord:
    if not isinstance(item, dict):
        raise SyncResponseError("cada item deve ser um objeto JSON")
    return LocalTagRecord(
        sharepoint_id=_required_int(item, "sharepointId"),
        status=_required_text(item, "status"),
        customer=_optional_text(item, "cliente"),
        invoice_number=_optional_text_any(item, "notaFiscal", "notafiscal"),
        volume=_optional_text(item, "volume"),
        order_number=_optional_text(item, "pedido"),
        dock=_required_text(item, "doca"),
        epc=_required_text(item, "epc"),
        sharepoint_modified=_required_text(item, "modified"),
    )


class PowerAutomateSyncClient:
    """Envia somente Doca e cursor ao endpoint de sincronização."""

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

    def sync(self, dock: str, modified_since: str) -> SyncPayload:
        """Executa o POST de sincronização e valida a resposta completa."""

        request = Request(
            self._endpoint_url,
            data=json.dumps({"doca": dock, "modifiedSince": modified_since}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        response = self._transport(request, self._timeout_seconds)
        if not 200 <= response.status_code < 300:
            raise SyncHttpError(response.status_code)

        try:
            document = json.loads(response.body.decode("utf-8"))
        except (UnicodeDecodeError, JSONDecodeError) as error:
            raise SyncResponseError("resposta JSON inválida") from error
        payload = _payload_from_document(document)

        _required_true(payload)
        sync_until = _required_text(payload, "syncUntil")
        count = _required_int(payload, "count")
        raw_items = _items(payload)
        if count != len(raw_items):
            raise SyncResponseError("count diverge do total de items")
        items = tuple(_record(item) for item in raw_items)
        return SyncPayload(sync_until=sync_until, items=items)
