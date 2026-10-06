"""Serviço de sincronização da fonte oficial para o SQLite local."""

from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import UTC, datetime

from rfid_reader.integrations.sharepoint_sync_client import (
    SyncClient,
    SyncClientError,
    SyncHttpError,
    SyncResponseError,
    SyncTimeoutError,
)
from rfid_reader.services.local_database import LocalDatabaseError, LocalTagRepository

LOGGER = logging.getLogger(__name__)


class TagSyncError(RuntimeError):
    """Falha esperada na sincronização da base local."""


class TagSyncRemoteError(TagSyncError):
    """Falha ao acionar ou validar o endpoint remoto de sincronização."""


class TagSyncLocalError(TagSyncError):
    """Falha local ao consultar cursor ou gravar o SQLite."""


class TagSyncService:
    """Coordena carga inicial, incremental e health check remoto leve."""

    def __init__(
        self,
        client: SyncClient,
        repository: LocalTagRepository,
        dock_getter: Callable[[], str],
    ) -> None:
        self._client = client
        self._repository = repository
        self._dock_getter = dock_getter

    def sync_current_dock(self) -> None:
        """Sincroniza a Doca atual usando cursor persistido por Doca."""

        dock = self._dock_getter()
        if not dock:
            raise TagSyncRemoteError("Doca da estação não configurada")
        try:
            control = self._repository.sync_control(dock)
        except LocalDatabaseError as error:
            LOGGER.warning("tag_sync_local_failed stage=cursor reason=%s", error)
            raise TagSyncLocalError("não foi possível consultar o cursor local") from error
        modified_since = control.last_sync if control is not None and control.initialized else ""
        initialized = bool(control is not None and control.initialized)
        try:
            payload = self._client.sync(dock, modified_since)
        except SyncClientError as error:
            self._log_sync_failure(error)
            raise TagSyncRemoteError("não foi possível consultar a sincronização remota") from error
        try:
            self._repository.apply_sync(
                dock,
                payload.items,
                payload.sync_until,
                full_sync=not initialized,
            )
        except LocalDatabaseError as error:
            LOGGER.warning("tag_sync_local_failed stage=apply reason=%s", error)
            raise TagSyncLocalError("não foi possível gravar a base local") from error
        LOGGER.info(
            "tag_sync_finished dock=%s items=%s initial=%s",
            dock,
            len(payload.items),
            not initialized,
        )

    def check_remote(self) -> bool:
        """Verifica o endpoint sem alterar SQLite nem avançar cursor."""

        dock = self._dock_getter()
        if not dock:
            return False
        try:
            control = self._repository.sync_control(dock)
        except LocalDatabaseError as error:
            LOGGER.warning("tag_sync_health_local_cursor_failed reason=%s", error)
            control = None
        modified_since = (
            control.last_sync
            if control is not None and control.last_sync
            else datetime.now(UTC).isoformat().replace("+00:00", "Z")
        )
        try:
            self._client.sync(dock, modified_since)
        except SyncClientError as error:
            self._log_sync_failure(error)
            return False
        return True

    @staticmethod
    def _log_sync_failure(error: Exception) -> None:
        http_status = error.status_code if isinstance(error, SyncHttpError) else None
        safe_type = type(error).__name__
        if isinstance(error, (SyncTimeoutError, SyncResponseError, SyncHttpError, SyncClientError)):
            LOGGER.warning(
                "tag_sync_failed error_type=%s http_status=%s reason=%s",
                safe_type,
                http_status,
                str(error),
            )
            return
        LOGGER.warning(
            "tag_sync_failed error_type=%s http_status=%s reason=%s",
            safe_type,
            http_status,
            str(error),
        )
