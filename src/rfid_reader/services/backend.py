"""Configuração e monitoramento do Backend RFID."""

from __future__ import annotations

import logging
import threading
from collections.abc import Callable, Mapping
from dataclasses import replace
from typing import Protocol

from rfid_reader.config import Settings
from rfid_reader.domain import ConnectionKind, ConnectionStatus
from rfid_reader.integrations.backend_client import BackendClientError, BackendRFIDClient

LOGGER = logging.getLogger(__name__)
TEST_IN_PROGRESS = "Testando conexão com o Backend RFID..."
TEST_SUCCESS = "Backend conectado com sucesso.\nSistema: OK"
TEST_FAILURE = "Backend indisponível.\nSistema: NOK"


class BackendConfigurationStore(Protocol):
    def save_values(self, values: dict[str, str]) -> None: ...


class BackendConfigurationService:
    def __init__(self, settings: Settings, store: BackendConfigurationStore) -> None:
        self._settings = settings
        self._store = store
        self._timeout_seconds = settings.connection_timeout_seconds
        self._lock = threading.Lock()
        self._testing = False

    def current(self) -> str:
        with self._lock:
            return self._settings.backend_base_url

    def save(self, base_url: str) -> bool:
        value = base_url.strip()
        try:
            self._store.save_values({"RFID_BACKEND_BASE_URL": _dotenv_value(value)})
        except OSError:
            LOGGER.exception("backend_configuration_save_failed")
            return False
        with self._lock:
            self._settings = replace(self._settings, backend_base_url=value)
        return True

    def test_connection(self, base_url: str, listener: Callable[[str], None]) -> bool:
        value = base_url.strip()
        with self._lock:
            if self._testing:
                return False
            self._testing = True
        listener(TEST_IN_PROGRESS)

        def run() -> None:
            try:
                health = BackendRFIDClient(value, self._timeout_seconds).health()
                listener(TEST_SUCCESS if health.system_ok else TEST_FAILURE)
            except BackendClientError:
                LOGGER.warning("backend_connection_test_failed", exc_info=True)
                listener(TEST_FAILURE)
            finally:
                with self._lock:
                    self._testing = False

        threading.Thread(target=run, name="backend-configuration-test", daemon=True).start()
        return True


def _dotenv_value(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


class BackendHealthChecker:
    def __init__(self, client_factory: Callable[[], BackendRFIDClient]) -> None:
        self._client_factory = client_factory
        self._closed = threading.Event()

    def check(self) -> Mapping[ConnectionKind, ConnectionStatus]:
        if self._closed.is_set():
            status = ConnectionStatus.DISCONNECTED
            return {ConnectionKind.SYSTEM: status}
        try:
            health = self._client_factory().health()
        except BackendClientError:
            LOGGER.warning("backend_health_unavailable", exc_info=True)
            return {ConnectionKind.SYSTEM: ConnectionStatus.ERROR}
        return {
            ConnectionKind.SYSTEM: (
                ConnectionStatus.CONNECTED if health.system_ok else ConnectionStatus.ERROR
            )
        }

    def close(self) -> None:
        self._closed.set()
