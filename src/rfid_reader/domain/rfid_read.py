"""Resultado normalizado do registro de uma passagem RFID."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RfidReadResult:
    """Resposta confirmada pelo Backend após o POST da passagem."""

    success: bool
    epc: str
    first_read: bool
    duplicate: bool
    status: str
    read_count: int
    first_read_at: str | None
    last_read_at: str | None
