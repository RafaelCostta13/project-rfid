"""Modelos independentes para consultas de etiquetas."""

from dataclasses import dataclass, field
from enum import StrEnum


class TagLookupStatus(StrEnum):
    """Estados apresentados para uma consulta individual."""

    WAITING = "Aguardando consulta"
    CONSULTING = "Consultando"
    FOUND = "Encontrada"
    NOT_FOUND = "Não encontrado"
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
    customer: str = ""
    invoice_number: str = ""
    order_number: str = ""
    volume: str = ""
    dock: str = ""
    record_status: str = ""


@dataclass(slots=True)
class TagLookupSessionSummary:
    """Mantém os resultados encontrados por EPC técnico na sessão atual."""

    _found_results: dict[str, TagLookupResult] = field(
        default_factory=dict,
        init=False,
        repr=False,
    )

    def update(self, result: TagLookupResult) -> bool:
        """Registra somente confirmações da base e informa se devem ser exibidas."""

        if result.status is not TagLookupStatus.FOUND:
            return False
        self._found_results[result.epc] = result
        return True

    def reset(self) -> None:
        """Descarta os resultados pertencentes à sessão anterior."""

        self._found_results.clear()

    @property
    def total(self) -> int:
        """Retorna o total de EPCs distintos confirmados pela base."""

        return len(self._found_results)


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
