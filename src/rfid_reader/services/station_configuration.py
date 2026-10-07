"""Configuração da estação no mesmo .env usado pelos dispositivos."""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
from typing import Protocol

from rfid_reader.config import Settings, validate_station_dock

LOGGER = logging.getLogger(__name__)


class ConfigurationValuesStore(Protocol):
    def save_values(self, values: dict[str, str]) -> None: ...


@dataclass(frozen=True, slots=True)
class StationConfigurationFeedback:
    success: bool
    message: str
    dock: str | None = None


class StationConfigurationService:
    """Mantém a única Doca atual, acessível por getter a futuras consultas."""

    def __init__(self, settings: Settings, store: ConfigurationValuesStore) -> None:
        self._dock = settings.station_dock
        self._store = store
        self._lock = threading.Lock()

    def current(self) -> str:
        """Obtém o valor salvo mais recente, inclusive ausência de configuração."""

        with self._lock:
            return self._dock

    def save(self, value: str) -> StationConfigurationFeedback:
        """Publica o novo valor somente depois da persistência bem-sucedida."""

        try:
            dock = validate_station_dock(value)
        except ValueError as error:
            return StationConfigurationFeedback(False, str(error))
        with self._lock:
            try:
                self._store.save_values({"RFID_STATION_DOCK": f'"{dock}"'})
            except OSError as error:
                LOGGER.error(
                    "station_configuration_save_failed error_type=%s", type(error).__name__
                )
                return StationConfigurationFeedback(False, "Não foi possível salvar a Doca.")
            previous = self._dock
            self._dock = dock
        LOGGER.info(
            "station_dock_saved previous=%s current=%s", previous or "unset", dock or "unset"
        )
        message = "Doca salva com sucesso." if dock else "Configure a Doca desta estação."
        return StationConfigurationFeedback(True, message, dock)
