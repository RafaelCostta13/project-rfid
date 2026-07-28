"""Fila controlada para consultas de etiquetas fora do callback LLRP."""

from __future__ import annotations

import logging
import queue
import threading
from collections.abc import Callable
from dataclasses import dataclass

from rfid_reader.domain import (
    TagLookupChanged,
    TagLookupEvent,
    TagLookupKey,
    TagLookupResult,
    TagLookupSessionStarted,
    TagLookupStatus,
    TagRead,
)
from rfid_reader.integrations.sharepoint_client import (
    TagLookupClient,
    TagLookupClientError,
    TagLookupHttpError,
    TagLookupResponseError,
    TagLookupTimeoutError,
)
from rfid_reader.services.tag_validation import is_valid_epc

LOGGER = logging.getLogger(__name__)
FRIENDLY_ERROR_MESSAGE = "Não foi possível consultar a etiqueta."
TagLookupListener = Callable[[TagLookupEvent], None]


@dataclass(frozen=True, slots=True)
class _LookupTask:
    session_id: int
    key: TagLookupKey


class TagLookupService:
    """Deduplica EPCs por sessão e os processa em um único worker."""

    def __init__(
        self,
        client: TagLookupClient,
        queue_size: int,
        listener: TagLookupListener,
    ) -> None:
        self._client = client
        self._listener = listener
        self._queue: queue.Queue[_LookupTask] = queue.Queue(maxsize=queue_size)
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._session_id = 0
        self._accepting = False
        self._closed = False
        self._seen: set[TagLookupKey] = set()
        self._worker = threading.Thread(
            target=self._run,
            name="tag-lookup-worker",
            daemon=True,
        )
        self._worker.start()

    def start_session(self) -> int:
        """Reinicia a deduplicação e invalida resultados da sessão anterior."""

        with self._lock:
            if self._closed:
                return self._session_id
            self._session_id += 1
            session_id = self._session_id
            self._seen.clear()
            self._accepting = True
        self._emit(TagLookupSessionStarted(session_id))
        return session_id

    def stop_accepting(self) -> None:
        """Impede a criação de consultas sem cancelar resultados válidos em curso."""

        with self._lock:
            self._accepting = False

    def submit(self, tag: TagRead) -> bool:
        """Agenda uma consulta sem bloquear a thread que entregou a leitura."""

        if not is_valid_epc(tag.epc):
            LOGGER.warning(
                "tag_lookup_invalid_epc_ignored reader_id=%s antenna=%s epc=%s",
                tag.reader_id,
                tag.antenna_id,
                tag.epc,
            )
            return False

        key = TagLookupKey(tag.reader_id, tag.antenna_id, tag.epc)
        with self._lock:
            if self._closed or not self._accepting or key in self._seen:
                return False
            self._seen.add(key)
            session_id = self._session_id

        self._emit_changed(
            session_id,
            key,
            TagLookupStatus.CONSULTING,
            "",
        )
        try:
            self._queue.put_nowait(_LookupTask(session_id, key))
        except queue.Full:
            LOGGER.error(
                "tag_lookup_queue_full reader_id=%s antenna=%s epc=%s",
                key.reader_id,
                key.antenna_id,
                key.epc,
            )
            self._emit_error(session_id, key)
            return False
        return True

    def _run(self) -> None:
        while not self._stop_event.is_set():
            try:
                task = self._queue.get(timeout=0.1)
            except queue.Empty:
                continue
            try:
                if self._is_current_session(task.session_id):
                    self._process(task)
            finally:
                self._queue.task_done()

    def _process(self, task: _LookupTask) -> None:
        LOGGER.debug(
            "tag_lookup_started reader_id=%s antenna=%s epc=%s",
            task.key.reader_id,
            task.key.antenna_id,
            task.key.epc,
        )
        try:
            result = self._client.lookup(task.key.epc)
        except TagLookupTimeoutError:
            LOGGER.warning("tag_lookup_timeout epc=%s", task.key.epc)
            self._emit_error_if_current(task)
            return
        except TagLookupHttpError as error:
            LOGGER.warning(
                "tag_lookup_http_error epc=%s status_code=%s",
                task.key.epc,
                error.status_code,
            )
            self._emit_error_if_current(task)
            return
        except TagLookupResponseError as error:
            LOGGER.warning("tag_lookup_invalid_response epc=%s error=%s", task.key.epc, error)
            self._emit_error_if_current(task)
            return
        except TagLookupClientError as error:
            LOGGER.warning("tag_lookup_network_error epc=%s error=%s", task.key.epc, error)
            self._emit_error_if_current(task)
            return
        except Exception:
            LOGGER.exception("tag_lookup_unexpected_error epc=%s", task.key.epc)
            self._emit_error_if_current(task)
            return

        if not self._is_current_session(task.session_id):
            LOGGER.debug("tag_lookup_stale_result_ignored epc=%s", task.key.epc)
            return
        LOGGER.info(
            "tag_lookup_finished epc=%s status=%s",
            task.key.epc,
            result.status.value,
        )
        self._emit(
            TagLookupChanged(
                task.session_id,
                task.key,
                result,
            )
        )

    def _emit_error_if_current(self, task: _LookupTask) -> None:
        if self._is_current_session(task.session_id):
            self._emit_error(task.session_id, task.key)

    def _emit_error(self, session_id: int, key: TagLookupKey) -> None:
        self._emit_changed(
            session_id,
            key,
            TagLookupStatus.ERROR,
            FRIENDLY_ERROR_MESSAGE,
        )

    def _emit_changed(
        self,
        session_id: int,
        key: TagLookupKey,
        status: TagLookupStatus,
        message: str,
    ) -> None:
        self._emit(
            TagLookupChanged(
                session_id,
                key,
                TagLookupResult(key.epc, status, message),
            )
        )

    def _is_current_session(self, session_id: int) -> bool:
        with self._lock:
            return not self._closed and session_id == self._session_id

    def _emit(self, event: TagLookupEvent) -> None:
        try:
            self._listener(event)
        except Exception:
            LOGGER.exception("tag_lookup_listener_failed")

    def close(self) -> None:
        """Interrompe o worker depois de aguardar a chamada corrente terminar."""

        with self._lock:
            if self._closed:
                return
            self._closed = True
            self._accepting = False
        self._stop_event.set()
        self._worker.join()
