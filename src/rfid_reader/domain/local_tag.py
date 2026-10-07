"""Modelos de domínio para a réplica local de etiquetas."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LocalTagRecord:
    """Registro normalizado recebido da sincronização SharePoint."""

    sharepoint_id: int
    status: str
    customer: str
    invoice_number: str
    volume: str
    order_number: str
    dock: str
    epc: str
    sharepoint_modified: str


@dataclass(frozen=True, slots=True)
class SyncControl:
    """Cursor de sincronização por Doca."""

    dock: str
    last_sync: str
    last_full_sync: str
    last_success_at: str
    initialized: bool
