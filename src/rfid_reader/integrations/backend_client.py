"""Cliente HTTP centralizado do Backend RFID."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from json import JSONDecodeError
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from rfid_reader.domain import RfidReadResult


class BackendClientError(RuntimeError):
    """Falha de rede, HTTP ou contrato do Backend."""


@dataclass(frozen=True, slots=True)
class BackendHealth:
    system_ok: bool
    database_ok: bool | None = None


@dataclass(frozen=True, slots=True)
class RfidRecordData:
    """Registro RFID normalizado a partir do contrato Rails."""

    datahora: str
    volume: str
    pedido: str
    notafiscal: str
    destinatario: str
    endereco: str
    numero: str
    cidade: str
    uf: str
    doca: str
    epc: str
    tag: str | None
    fornecedor: str
    status: str
    first_read_at: str | None
    last_read_at: str | None
    read_count: int


@dataclass(frozen=True, slots=True)
class HttpResponse:
    status_code: int
    body: bytes


HttpTransport = Callable[[Request, float], HttpResponse]


def _urllib_transport(request: Request, timeout_seconds: float) -> HttpResponse:
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            return HttpResponse(response.getcode(), response.read())
    except HTTPError as error:
        return HttpResponse(error.code, error.read())
    except TimeoutError as error:
        raise BackendClientError("timeout no Backend RFID") from error
    except URLError as error:
        raise BackendClientError("falha de rede no Backend RFID") from error
    except OSError as error:
        raise BackendClientError("falha de rede no Backend RFID") from error


class BackendRFIDClient:
    def __init__(
        self,
        base_url: str,
        timeout_seconds: float,
        *,
        transport: HttpTransport = _urllib_transport,
    ) -> None:
        self._base_url = base_url.strip().rstrip("/")
        self._timeout_seconds = timeout_seconds
        self._transport = transport

    def health(self) -> BackendHealth:
        if not self._base_url:
            return BackendHealth(False)
        try:
            request = Request(f"{self._base_url}/api/v1/health", method="GET")
        except ValueError as error:
            raise BackendClientError("URL do Backend inválida") from error
        try:
            response = self._transport(request, self._timeout_seconds)
        except BackendClientError:
            raise
        except (TimeoutError, OSError) as error:
            raise BackendClientError("falha de rede no Backend RFID") from error
        if response.status_code != 200:
            return BackendHealth(False)
        try:
            document = json.loads(response.body.decode("utf-8"))
        except (UnicodeDecodeError, JSONDecodeError) as error:
            raise BackendClientError("resposta health inválida") from error
        if not isinstance(document, dict):
            raise BackendClientError("resposta health inválida")
        status = document.get("status")
        if not isinstance(status, str):
            raise BackendClientError("resposta health inválida")
        database = document.get("database")
        return BackendHealth(
            status == "ok", database == "ok" if isinstance(database, str) else None
        )

    def get_rfid_record(self, epc: str) -> RfidRecordData | None:
        """Consulta um EPC sem registrar passagem ou alterar o Backend."""

        normalized_epc = epc.strip().upper()
        if not normalized_epc:
            raise BackendClientError("EPC vazio")
        if not self._base_url:
            raise BackendClientError("URL do Backend não configurada")
        try:
            request = Request(
                f"{self._base_url}/api/v1/rfid_records/{quote(normalized_epc, safe='')}",
                method="GET",
            )
        except ValueError as error:
            raise BackendClientError("URL do Backend inválida") from error
        try:
            response = self._transport(request, self._timeout_seconds)
        except BackendClientError:
            raise
        except (TimeoutError, OSError) as error:
            raise BackendClientError("falha de rede no Backend RFID") from error
        document = self._json_document(response.body, response.status_code)
        if response.status_code == 404:
            if document.get("found") is False and document.get("error") == "epc_not_found":
                return None
            raise BackendClientError("resposta 404 inválida para consulta de EPC")
        if response.status_code != 200:
            raise BackendClientError(f"resposta HTTP {response.status_code} na consulta de EPC")
        if document.get("found") is not True:
            raise BackendClientError("resposta EPC inválida: found")
        raw_data = document.get("data")
        if not isinstance(raw_data, dict):
            raise BackendClientError("resposta EPC inválida: data")
        return self._record_from_data(raw_data, normalized_epc)

    def create_rfid_read(self, epc: str) -> RfidReadResult:
        """Registra uma passagem usando somente o EPC normalizado."""

        normalized_epc = epc.strip().upper()
        if not normalized_epc:
            raise BackendClientError("EPC vazio")
        if not self._base_url:
            raise BackendClientError("URL do Backend não configurada")
        try:
            request = Request(
                f"{self._base_url}/api/v1/rfid_reads",
                data=json.dumps({"epc": normalized_epc}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
        except ValueError as error:
            raise BackendClientError("URL do Backend inválida") from error
        try:
            response = self._transport(request, self._timeout_seconds)
        except BackendClientError:
            raise
        except (TimeoutError, OSError) as error:
            raise BackendClientError("falha de rede no Backend RFID") from error
        document = self._json_document(response.body, response.status_code)
        if response.status_code != 200:
            error_code = document.get("error")
            raise BackendClientError(
                f"resposta HTTP {response.status_code} no registro de passagem"
                + (f": {error_code}" if isinstance(error_code, str) else "")
            )
        if document.get("success") is not True:
            raise BackendClientError("resposta de passagem inválida: success")
        return self._read_result_from_document(document, normalized_epc)

    def _json_document(self, body: bytes, status_code: int) -> dict[str, object]:
        try:
            document = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, JSONDecodeError) as error:
            raise BackendClientError(
                f"resposta JSON inválida na consulta de EPC (HTTP {status_code})"
            ) from error
        if not isinstance(document, dict):
            raise BackendClientError("resposta EPC inválida: objeto JSON esperado")
        return document

    @staticmethod
    def _required_text(data: dict[str, object], field: str) -> str:
        value = data.get(field)
        if not isinstance(value, str):
            raise BackendClientError(f"resposta EPC inválida: campo {field}")
        return value

    @staticmethod
    def _optional_text(data: dict[str, object], field: str) -> str | None:
        value = data.get(field)
        if value is None:
            return None
        if not isinstance(value, str):
            raise BackendClientError(f"resposta EPC inválida: campo {field}")
        return value

    def _record_from_data(
        self,
        data: dict[str, object],
        requested_epc: str,
    ) -> RfidRecordData:
        returned_epc = self._required_text(data, "epc").strip().upper()
        if returned_epc != requested_epc:
            raise BackendClientError("resposta EPC inválida: EPC divergente")
        raw_read_count = data.get("read_count")
        if (
            not isinstance(raw_read_count, int)
            or isinstance(raw_read_count, bool)
            or raw_read_count < 0
        ):
            raise BackendClientError("resposta EPC inválida: campo read_count")
        return RfidRecordData(
            datahora=self._required_text(data, "datahora"),
            volume=self._required_text(data, "volume"),
            pedido=self._required_text(data, "pedido"),
            notafiscal=self._required_text(data, "notafiscal"),
            destinatario=self._required_text(data, "destinatario"),
            endereco=self._required_text(data, "endereco"),
            numero=self._required_text(data, "numero"),
            cidade=self._required_text(data, "cidade"),
            uf=self._required_text(data, "uf"),
            doca=self._required_text(data, "doca"),
            epc=returned_epc,
            tag=self._optional_text(data, "tag"),
            fornecedor=self._required_text(data, "fornecedor"),
            status=self._required_text(data, "status"),
            first_read_at=self._optional_text(data, "first_read_at"),
            last_read_at=self._optional_text(data, "last_read_at"),
            read_count=raw_read_count,
        )

    def _read_result_from_document(
        self,
        document: dict[str, object],
        requested_epc: str,
    ) -> RfidReadResult:
        returned_epc = self._required_text(document, "epc").strip().upper()
        if returned_epc != requested_epc:
            raise BackendClientError("resposta de passagem inválida: EPC divergente")
        first_read = document.get("first_read")
        duplicate = document.get("duplicate")
        if not isinstance(first_read, bool) or not isinstance(duplicate, bool):
            raise BackendClientError("resposta de passagem inválida: flags")
        raw_read_count = document.get("read_count")
        if (
            not isinstance(raw_read_count, int)
            or isinstance(raw_read_count, bool)
            or raw_read_count < 0
        ):
            raise BackendClientError("resposta de passagem inválida: read_count")
        return RfidReadResult(
            success=True,
            epc=returned_epc,
            first_read=first_read,
            duplicate=duplicate,
            status=self._required_text(document, "status"),
            read_count=raw_read_count,
            first_read_at=self._optional_text(document, "first_read_at"),
            last_read_at=self._optional_text(document, "last_read_at"),
        )
