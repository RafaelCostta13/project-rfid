"""Verificadores de disponibilidade da base local e da sincronização remota."""

from __future__ import annotations

import logging
import threading
import time
from collections.abc import Callable

from rfid_reader.domain import ConnectionStatus
from rfid_reader.services.local_database import LocalTagRepository
from rfid_reader.services.tag_sync import TagSyncService

LOGGER = logging.getLogger(__name__)


class LocalDatabaseConnectionChecker:
    """Representa a disponibilidade operacional do SQLite local."""

    def __init__(
        self,
        repository: LocalTagRepository,
        dock_getter: Callable[[], str],
    ) -> None:
        self._repository = repository
        self._dock_getter = dock_getter
        self._closed = threading.Event()

    def check(self) -> ConnectionStatus:
        if self._closed.is_set():
            return ConnectionStatus.DISCONNECTED
        return (
            ConnectionStatus.CONNECTED
            if self._repository.is_operational(self._dock_getter())
            else ConnectionStatus.ERROR
        )

    def close(self) -> None:
        self._closed.set()


class SyncConnectionChecker:
    """Sondagem leve do endpoint de sincronização sem alterar cursor."""

    def __init__(
        self,
        sync_service: TagSyncService,
        internet_status: Callable[[], ConnectionStatus],
        interval_seconds: float,
        *,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._sync_service = sync_service
        self._internet_status = internet_status
        self._interval_seconds = interval_seconds
        self._clock = clock
        self._next_check = 0.0
        self._status = ConnectionStatus.CHECKING
        self._lock = threading.Lock()
        self._closed = threading.Event()

    def check(self) -> ConnectionStatus:
        with self._lock:
            if self._closed.is_set():
                return ConnectionStatus.DISCONNECTED
            internet = self._internet_status()
            if internet is not ConnectionStatus.CONNECTED:
                self._next_check = 0.0
                self._status = (
                    ConnectionStatus.CHECKING
                    if internet is ConnectionStatus.CHECKING
                    else ConnectionStatus.DISCONNECTED
                )
                return self._status
            if self._clock() < self._next_check:
                return self._status
            self._status = (
                ConnectionStatus.CONNECTED
                if self._sync_service.check_remote()
                else ConnectionStatus.ERROR
            )
            self._next_check = self._clock() + self._interval_seconds
            return self._status

    def close(self) -> None:
        self._closed.set()
        with self._lock:
            pass
