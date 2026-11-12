"""Captura isolada de amostras para o mapa assistido de antenas."""

from __future__ import annotations

import logging
import threading
from collections.abc import Callable
from dataclasses import dataclass

from rfid_reader.domain import TagRead
from rfid_reader.readers.base import ReaderError, RFIDReader

LOGGER = logging.getLogger(__name__)
MAX_POINTS = 2000


@dataclass(frozen=True, slots=True)
class MappingPoint:
    antenna: int
    angle: int
    epc: str
    rssi: int
    timestamp: str


@dataclass(frozen=True, slots=True)
class MappingSnapshot:
    active: bool
    message: str
    points: tuple[MappingPoint, ...]


class AntennaMappingService:
    """Mantém o maior RSSI por antena, ângulo e EPC, sem passar pelo backend."""

    def __init__(self, reader: RFIDReader, listener: Callable[[MappingSnapshot], None]) -> None:
        self._reader = reader
        self._listener = listener
        self._lock = threading.Lock()
        self._active = False
        self._angle = 0
        self._points: dict[tuple[int, int, str], MappingPoint] = {}
        self._message = "Mapeamento parado."

    def snapshot(self) -> MappingSnapshot:
        with self._lock:
            return MappingSnapshot(self._active, self._message, tuple(self._points.values()))

    def _notify(self) -> None:
        self._listener(self.snapshot())

    def set_angle(self, angle: int) -> None:
        if not -180 <= angle <= 180:
            raise ValueError("O ângulo deve estar entre -180 e 180 graus.")
        with self._lock:
            self._angle = angle

    def clear(self) -> None:
        with self._lock:
            self._points.clear()
        self._notify()

    def start(self) -> bool:
        with self._lock:
            if self._active:
                return False
            self._active = True
            self._message = "Iniciando mapeamento..."
        self._notify()
        try:
            started = self._reader.is_connected() and self._reader.start_inventory(self._on_tag)
        except ReaderError:
            LOGGER.exception("antenna_mapping_start_failed")
            started = False
        with self._lock:
            interrupted = not self._active
            self._active = started and not interrupted
            self._message = (
                "Mapeamento ativo." if started else "Não foi possível iniciar o mapeamento RFID."
            )
        if started and interrupted:
            try:
                self._reader.stop_inventory()
            except ReaderError:
                LOGGER.warning("antenna_mapping_stop_after_disconnect_failed", exc_info=True)
            with self._lock:
                self._active = self._reader.is_inventorying()
                self._message = "Conexão RFID perdida. Verifique a parada do mapeamento."
            self._notify()
            return False
        self._notify()
        return started

    def stop(self) -> bool:
        reader_active = self._reader.is_inventorying()
        with self._lock:
            was_active = self._active or reader_active
            self._active = False
        success = True
        if was_active:
            try:
                success = self._reader.stop_inventory()
            except ReaderError:
                LOGGER.exception("antenna_mapping_stop_failed")
                success = False
            if not success:
                try:
                    self._reader.disconnect()
                except ReaderError:
                    LOGGER.exception("antenna_mapping_disconnect_failed")
        with self._lock:
            if not success and self._reader.is_connected():
                self._active = True
            self._message = "Mapeamento parado." if success else "Falha ao parar o mapeamento."
        self._notify()
        return success

    def connection_lost(self) -> None:
        with self._lock:
            if not self._active:
                return
            self._active = False
            self._message = "Conexão RFID perdida. Mapeamento interrompido."
        self._notify()

    def _on_tag(self, tag: TagRead) -> None:
        if tag.antenna_id is None or tag.rssi is None:
            with self._lock:
                if self._active:
                    self._message = "Leitura sem antena ou RSSI foi ignorada."
            return
        with self._lock:
            if not self._active:
                return
            key = (tag.antenna_id, self._angle, tag.epc)
            previous = self._points.get(key)
            if previous is not None and previous.rssi >= tag.rssi:
                return
            if previous is None and len(self._points) >= MAX_POINTS:
                self._message = "Limite de pontos atingido. Limpe o mapa para novas leituras."
                return
            self._points[key] = MappingPoint(
                tag.antenna_id, self._angle, tag.epc, tag.rssi, tag.read_at.isoformat()
            )
