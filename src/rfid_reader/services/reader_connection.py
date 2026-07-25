"""Adaptador do reader compartilhado para o monitor de conexões."""

from __future__ import annotations

import logging

from rfid_reader.domain import ConnectionStatus
from rfid_reader.readers.base import (
    ReaderConnectionError,
    ReaderError,
    RFIDReader,
)

LOGGER = logging.getLogger(__name__)


class ReaderConnectionChecker:
    """Mantém e consulta a mesma sessão utilizada pelo inventário."""

    def __init__(self, reader: RFIDReader) -> None:
        self._reader = reader

    def check(self) -> ConnectionStatus:
        if self._reader.is_connected():
            return ConnectionStatus.CONNECTED
        try:
            self._reader.connect()
        except ReaderConnectionError as error:
            LOGGER.debug("reader_connection_unavailable error=%s", error)
            return ConnectionStatus.DISCONNECTED
        except ReaderError:
            LOGGER.exception("reader_connection_protocol_error")
            return ConnectionStatus.ERROR
        return (
            ConnectionStatus.CONNECTED
            if self._reader.is_connected()
            else ConnectionStatus.DISCONNECTED
        )

    def close(self) -> None:
        """O ciclo da sessão pertence ao serviço de inventário compartilhado."""
