"""Coordenação do inventário manual sem dependência da interface."""

from __future__ import annotations

import logging
import threading
from collections.abc import Callable

from rfid_reader.domain import (
    InventoryCleared,
    InventoryEvent,
    InventoryStatus,
    InventoryStatusChanged,
    TagRead,
    TagReceived,
)
from rfid_reader.readers.base import ReaderError, RFIDReader

LOGGER = logging.getLogger(__name__)
InventoryListener = Callable[[InventoryEvent], None]


class ManualInventoryService:
    """Aplica as regras de início, parada e entrega de EPCs."""

    def __init__(self, reader: RFIDReader, listener: InventoryListener) -> None:
        self._reader = reader
        self._listener = listener
        self._lock = threading.Lock()
        self._status = InventoryStatus.STOPPED
        self._accept_tags = False
        self._closed = False
        self._reader.set_disconnect_callback(self._on_disconnected)

    @property
    def status(self) -> InventoryStatus:
        with self._lock:
            return self._status

    def start(self) -> bool:
        """Inicia uma única leitura quando o reader está conectado."""

        with self._lock:
            if self._closed or self._status is InventoryStatus.READING:
                return False
            if not self._reader.is_connected():
                self._status = InventoryStatus.ERROR
                status = self._status
                should_start = False
            else:
                self._status = InventoryStatus.READING
                self._accept_tags = False
                status = self._status
                should_start = True

        if not should_start:
            self._emit(InventoryStatusChanged(status))
            return False

        try:
            started = self._reader.start_inventory(self._on_tag)
        except ReaderError:
            LOGGER.exception("manual_inventory_start_failed")
            started = False

        if not started:
            with self._lock:
                self._status = InventoryStatus.ERROR
                self._accept_tags = False
                status = self._status
            self._emit(InventoryStatusChanged(status))
            return False

        with self._lock:
            self._accept_tags = True
        self._emit(InventoryCleared())
        self._emit(InventoryStatusChanged(InventoryStatus.READING))
        return True

    def stop(self) -> bool:
        """Bloqueia novas tags antes de solicitar a parada ao reader."""

        with self._lock:
            if self._status is not InventoryStatus.READING:
                return False
            self._accept_tags = False
            self._status = InventoryStatus.STOPPED

        try:
            if not self._reader.stop_inventory():
                raise ReaderError("O reader não confirmou a parada do inventário.")
        except ReaderError:
            LOGGER.exception("manual_inventory_stop_failed")
            self._reader.disconnect()
            with self._lock:
                self._status = InventoryStatus.ERROR
            self._emit(InventoryStatusChanged(InventoryStatus.ERROR))
            return False

        self._emit(InventoryStatusChanged(InventoryStatus.STOPPED))
        return True

    def _on_tag(self, tag: TagRead) -> None:
        with self._lock:
            if not self._accept_tags or self._status is not InventoryStatus.READING:
                return
        self._emit(TagReceived(tag))

    def _on_disconnected(self) -> None:
        with self._lock:
            was_reading = self._status is InventoryStatus.READING
            self._accept_tags = False
            if was_reading:
                self._status = InventoryStatus.ERROR
        if was_reading:
            self._emit(InventoryStatusChanged(InventoryStatus.ERROR))

    def _emit(self, event: InventoryEvent) -> None:
        try:
            self._listener(event)
        except Exception:
            LOGGER.exception("manual_inventory_listener_failed")

    def close(self) -> None:
        """Interrompe o inventário e encerra a única sessão do reader."""

        with self._lock:
            if self._closed:
                return
            self._closed = True
            reading = self._status is InventoryStatus.READING
            self._accept_tags = False
            self._status = InventoryStatus.STOPPED
        if reading:
            try:
                self._reader.stop_inventory()
            except ReaderError:
                LOGGER.exception("manual_inventory_stop_during_close_failed")
        self._reader.disconnect()
