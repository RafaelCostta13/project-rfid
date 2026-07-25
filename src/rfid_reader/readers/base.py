"""Contrato interno para readers RFID."""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol

from rfid_reader.domain import TagRead

TagCallback = Callable[[TagRead], None]
DisconnectCallback = Callable[[], None]


class RFIDReader(Protocol):
    """Operações necessárias para conexão e inventário manual."""

    def connect(self) -> None: ...

    def disconnect(self) -> None: ...

    def is_connected(self) -> bool: ...

    def start_inventory(self, callback: TagCallback) -> bool: ...

    def stop_inventory(self) -> bool: ...

    def is_inventorying(self) -> bool: ...

    def set_disconnect_callback(self, callback: DisconnectCallback) -> None: ...


class ReaderError(RuntimeError):
    """Erro conhecido ao operar um reader RFID."""


class ReaderConnectionError(ReaderError):
    """Falha de transporte ou timeout ao conectar."""


class ReaderProtocolError(ReaderError):
    """Falha na sessão ou em uma operação LLRP."""
