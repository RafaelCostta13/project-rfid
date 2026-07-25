"""Modelo interno de uma leitura RFID."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(frozen=True, slots=True)
class TagRead:
    """Leitura normalizada sem dependência da biblioteca LLRP."""

    epc: str
    reader_id: str
    antenna_id: int | None
    read_at: datetime
    rssi: int | None = None
    seen_count: int | None = None

    def __post_init__(self) -> None:
        if not self.epc:
            raise ValueError("epc não pode estar vazio")
        if self.read_at.tzinfo is None or self.read_at.utcoffset() != UTC.utcoffset(self.read_at):
            raise ValueError("read_at deve estar em UTC")
