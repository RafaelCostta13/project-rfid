"""Estados e eventos do inventário RFID manual."""

from dataclasses import dataclass
from enum import StrEnum

from rfid_reader.domain.tag_read import TagRead


class InventoryStatus(StrEnum):
    """Estados apresentados para a leitura manual."""

    STOPPED = "Parado"
    READING = "Lendo"
    ERROR = "Erro"


@dataclass(frozen=True, slots=True)
class InventoryCleared:
    """Solicita a limpeza da lista antes de uma nova leitura."""


@dataclass(frozen=True, slots=True)
class InventoryResumed:
    """Retoma a sessão existente sem limpar seus resultados."""


@dataclass(frozen=True, slots=True)
class InventoryStatusChanged:
    """Informa uma mudança do estado da leitura."""

    status: InventoryStatus


@dataclass(frozen=True, slots=True)
class InventorySessionCompleted:
    """Resume uma sessão encerrada normalmente após classificar suas etiquetas."""

    session_id: int
    reason: str
    found_count: int


@dataclass(frozen=True, slots=True)
class TagReceived:
    """Entrega uma etiqueta recebida durante o inventário atual."""

    tag: TagRead


InventoryEvent = InventoryCleared | InventoryResumed | InventoryStatusChanged | TagReceived
