"""Coordenação periódica e independente dos estados de conexão."""

from __future__ import annotations

import logging
import threading
from collections.abc import Callable, Mapping
from typing import Protocol

from rfid_reader.domain import ConnectionKind, ConnectionStatus

LOGGER = logging.getLogger(__name__)
StatusListener = Callable[[ConnectionKind, ConnectionStatus], None]


class ConnectionChecker(Protocol):
    def check(self) -> ConnectionStatus | Mapping[ConnectionKind, ConnectionStatus]: ...

    def close(self) -> None: ...


class ConnectionMonitor:
    """Executa cada verificador em sua própria thread e publica mudanças."""

    def __init__(
        self,
        checkers: Mapping[ConnectionKind, ConnectionChecker],
        interval_seconds: float,
        listener: StatusListener,
        *,
        additional_kinds: tuple[ConnectionKind, ...] = (),
    ) -> None:
        self._checkers = dict(checkers)
        self._interval_seconds = interval_seconds
        self._listener = listener
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        kinds = (*self._checkers, *additional_kinds)
        self._states = {kind: ConnectionStatus.CHECKING for kind in kinds}
        self._threads: list[threading.Thread] = []
        self._started = False

    def start(self) -> None:
        """Publica os estados iniciais e inicia as verificações periódicas."""

        with self._lock:
            if self._started:
                return
            self._started = True

        for kind in self._checkers:
            self._notify(kind, ConnectionStatus.CHECKING)
            thread = threading.Thread(
                target=self._run_checker,
                args=(kind,),
                name=f"connection-monitor-{kind.value}",
                daemon=True,
            )
            self._threads.append(thread)
            thread.start()

    def _run_checker(self, kind: ConnectionKind) -> None:
        checker = self._checkers[kind]
        while not self._stop_event.is_set():
            try:
                result = checker.check()
            except Exception:
                LOGGER.exception("connection_check_failed connection=%s", kind.value)
                result = ConnectionStatus.ERROR
            if self._stop_event.is_set():
                return
            if isinstance(result, Mapping):
                for result_kind, status in result.items():
                    self._set_status(result_kind, status)
            else:
                self._set_status(kind, result)
            if self._stop_event.wait(self._interval_seconds):
                return

    def _set_status(self, kind: ConnectionKind, status: ConnectionStatus) -> None:
        with self._lock:
            previous = self._states[kind]
            if previous == status:
                return
            self._states[kind] = status
        LOGGER.info(
            "connection_status_changed connection=%s previous=%s current=%s",
            kind.value,
            previous.value,
            status.value,
        )
        self._notify(kind, status)

    def _notify(self, kind: ConnectionKind, status: ConnectionStatus) -> None:
        try:
            self._listener(kind, status)
        except Exception:
            LOGGER.exception("connection_status_listener_failed connection=%s", kind.value)

    def statuses(self) -> dict[ConnectionKind, ConnectionStatus]:
        """Retorna uma cópia consistente dos estados atuais."""

        with self._lock:
            return dict(self._states)

    def stop(self) -> None:
        """Cancela verificações, fecha recursos e aguarda as threads."""

        self._stop_event.set()
        for checker in self._checkers.values():
            try:
                checker.close()
            except Exception:
                LOGGER.exception("connection_checker_close_failed")
        for thread in self._threads:
            thread.join(timeout=max(1.0, self._interval_seconds))
            if thread.is_alive():
                LOGGER.warning("connection_monitor_thread_did_not_stop thread=%s", thread.name)
