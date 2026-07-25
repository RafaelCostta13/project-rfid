"""Modelos independentes para consultas de etiquetas."""

from dataclasses import dataclass
from enum import StrEnum


class TagLookupStatus(StrEnum):
    """Estados apresentados para uma consulta individual."""

    WAITING = "Aguardando consulta"
    CONSULTING = "Consultando"
    FOUND = "Encontrada"
    NOT_FOUND = "Não encontrada"
    ERROR = "Erro"


@dataclass(frozen=True, slots=True)
class TagLookupKey:
    """Identifica uma etiqueta dentro de uma sessão de inventário."""

    reader_id: str
    antenna_id: int | None
    epc: str


@dataclass(frozen=True, slots=True)
class TagLookupResult:
    """Resultado normalizado sem expor detalhes do cliente HTTP."""

    epc: str
    status: TagLookupStatus
    message: str
    tag: str = ""
    customer: str = ""
    invoice_number: str = ""
    order_number: str = ""
    volume: str = ""
    dock: str = ""


@dataclass(frozen=True, slots=True)
class TagLookupSessionStarted:
    """Informa que eventos anteriores não pertencem mais à sessão ativa."""

    session_id: int


@dataclass(frozen=True, slots=True)
class TagLookupChanged:
    """Atualiza o estado de uma etiqueta na sessão indicada."""

    session_id: int
    key: TagLookupKey
    result: TagLookupResult


TagLookupEvent = TagLookupSessionStarted | TagLookupChanged
