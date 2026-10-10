"""Adaptador dos serviços de configuração; um único worker de gravação local."""

from __future__ import annotations

import logging
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import Property, QObject, Qt, Signal, Slot

from rfid_reader.config import STATION_DOCK_SUGGESTIONS, Settings
from rfid_reader.domain import (
    ReaderConfigurationFeedback,
    ReaderConfigurationOutcome,
    WaveshareConfigurationFeedback,
    WaveshareConfigurationOutcome,
)
from rfid_reader.services.backend import BackendConfigurationService
from rfid_reader.services.reader_configuration import (
    DotEnvReaderConfigurationStore,
    ReaderConfigurationService,
)
from rfid_reader.services.station_configuration import StationConfigurationService
from rfid_reader.services.waveshare_configuration import (
    DotEnvWaveshareConfigurationStore,
    WaveshareConfigurationService,
)

LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from rfid_reader.runtime import ApplicationRuntime


@dataclass(frozen=True, slots=True)
class ConfigurationFeedback:
    section: str
    success: bool
    message: str


class ConfigurationBridge(QObject):
    """Não cria reader, tester, monitor, cliente HTTP ou conexão serial."""

    changed = Signal()
    finished = Signal(str, bool, arguments=["section", "success"])
    feedbackReceived = Signal(object)

    def __init__(
        self, settings: Settings, path: Path, runtime: ApplicationRuntime | None = None
    ) -> None:
        super().__init__()
        self._busy = False
        self._closed = False
        self._feedback: dict[str, dict[str, str]] = {}
        self._runtime = runtime
        self._unsubscribe: Callable[[], None] = lambda: None
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="qt-configuration")
        if runtime is None:
            store = DotEnvReaderConfigurationStore(path)
            self._reader = ReaderConfigurationService(
                settings, store, None, None, lambda: False, self._reader_feedback
            )
            self._waveshare = WaveshareConfigurationService(
                settings, DotEnvWaveshareConfigurationStore(path), None, self._waveshare_feedback
            )
            self._station = StationConfigurationService(settings, store)
            self._backend = BackendConfigurationService(settings, store)
        else:
            self._reader = runtime.reader_configuration
            self._waveshare = runtime.waveshare_configuration
            self._station = runtime.station_configuration
            self._backend = runtime.backend_configuration
            self._unsubscribe = runtime.subscribe(self._runtime_feedback)
        self.feedbackReceived.connect(self._apply_feedback, Qt.ConnectionType.QueuedConnection)

    def _get_fields(self) -> dict[str, str]:
        reader, waveshare = self._reader.current(), self._waveshare.current()
        return {
            "reader_name": reader.name,
            "reader_host": reader.host,
            "reader_port": str(reader.port),
            "serial_port": waveshare.serial_port,
            "baud_rate": str(waveshare.baud_rate),
            "data_bits": str(waveshare.data_bits),
            "parity": waveshare.parity,
            "stop_bits": str(waveshare.stop_bits),
            "device_id": str(waveshare.device_id),
            "station_dock": self._station.current(),
            "backend_url": self._backend.current(),
        }

    def _get_busy(self) -> bool:
        return self._busy or self._closed

    def _get_feedback(self) -> dict[str, dict[str, str]]:
        return {section: dict(value) for section, value in self._feedback.items()}

    fields = Property(dict, _get_fields, notify=changed)
    busy = Property(bool, _get_busy, notify=changed)
    feedback = Property(dict, _get_feedback, notify=changed)
    dockSuggestions = Property(list, lambda self: ["", *STATION_DOCK_SUGGESTIONS], constant=True)
    testsAvailable = Property(bool, lambda self: self._runtime is not None, constant=True)

    def _runtime_feedback(self, event: object) -> None:
        from rfid_reader.runtime import RuntimeEvent

        if not isinstance(event, RuntimeEvent):
            return
        if isinstance(event.value, ReaderConfigurationFeedback):
            self._reader_feedback(event.value)
        elif isinstance(event.value, WaveshareConfigurationFeedback):
            self._waveshare_feedback(event.value)

    def _reader_feedback(self, event: ReaderConfigurationFeedback) -> None:
        self.feedbackReceived.emit(
            ConfigurationFeedback(
                "reader",
                event.outcome is ReaderConfigurationOutcome.SUCCESS,
                event.message,
            )
        )

    def _waveshare_feedback(self, event: WaveshareConfigurationFeedback) -> None:
        self.feedbackReceived.emit(
            ConfigurationFeedback(
                "waveshare",
                event.outcome is WaveshareConfigurationOutcome.SUCCESS,
                event.message,
            )
        )

    @Slot(object)
    def _apply_feedback(self, event: object) -> None:
        if self._closed or not isinstance(event, ConfigurationFeedback):
            return
        self._busy = False
        self._feedback[event.section] = {
            "state": "ok" if event.success else "error",
            "message": event.message,
        }
        self.changed.emit()
        self.finished.emit(event.section, event.success)

    def _submit(self, section: str, values: tuple[str, ...]) -> bool:
        if self._closed or self._busy:
            return False
        self._busy = True
        self._feedback[section] = {"state": "checking", "message": "Salvando configurações..."}
        self.changed.emit()
        if self._runtime is None:
            self._executor.submit(self._save, section, values)
        elif not self._runtime.submit("save_" + section, lambda: self._save(section, values)):
            self._busy = False
            self.changed.emit()
            return False
        return True

    def _save(self, section: str, values: tuple[str, ...]) -> None:
        try:
            if section == "reader":
                self._reader.save(values[0], values[1], values[2])
            elif section == "waveshare":
                self._waveshare.save(*values)
            elif section == "station":
                result = self._station.save(values[0])
                self.feedbackReceived.emit(
                    ConfigurationFeedback(section, result.success, result.message)
                )
            elif section == "backend":
                success = self._backend.save(values[0])
                self.feedbackReceived.emit(
                    ConfigurationFeedback(
                        section,
                        success,
                        "URL do Backend salva com sucesso."
                        if success
                        else "Não foi possível salvar a URL.",
                    )
                )
        except Exception as error:
            # Fronteira worker/UI: evita Future silencioso e nunca registra valores do formulário.
            LOGGER.error(
                "qt_configuration_save_failed section=%s error_type=%s",
                section,
                type(error).__name__,
            )
            self.feedbackReceived.emit(
                ConfigurationFeedback(section, False, "Não foi possível salvar as configurações.")
            )

    @Slot(str, str, str, result=bool)
    def saveReader(self, name: str, host: str, port: str) -> bool:
        return self._submit("reader", (name, host, port))

    @Slot(str, str, str, str, str, str, result=bool)
    def saveWaveshare(
        self,
        port: str,
        baud: str,
        bits: str,
        parity: str,
        stop: str,
        device: str,
    ) -> bool:
        return self._submit("waveshare", (port, baud, bits, parity, stop, device))

    @Slot(str, result=bool)
    def saveStation(self, dock: str) -> bool:
        return self._submit("station", (dock,))

    @Slot(str, result=bool)
    def saveBackend(self, url: str) -> bool:
        return self._submit("backend", (url,))

    def _submit_test(self, section: str, values: tuple[str, ...]) -> bool:
        if self._closed or self._busy or self._runtime is None:
            return False
        self._busy = True
        self._feedback[section] = {"state": "checking", "message": "Testando conexão..."}
        self.changed.emit()
        if not self._runtime.submit("test_" + section, lambda: self._test(section, values)):
            self._busy = False
            self.changed.emit()
            return False
        return True

    def _test(self, section: str, values: tuple[str, ...]) -> None:
        if self._runtime is None:
            return
        try:
            if section == "reader":
                success = self._runtime.test_reader(*values)
            elif section == "waveshare":
                success = self._runtime.test_waveshare(values)
            else:
                success = self._runtime.test_backend(values[0])
            message = (
                "Conexão realizada com sucesso."
                if success
                else "Conexão indisponível. Pare a leitura antes de testar equipamentos."
            )
        except Exception as error:
            LOGGER.warning(
                "qt_configuration_test_failed section=%s error_type=%s",
                section,
                type(error).__name__,
            )
            success, message = False, "Não foi possível testar a conexão. Verifique os parâmetros."
        self.feedbackReceived.emit(ConfigurationFeedback(section, success, message))

    @Slot(str, str, str, result=bool)
    def testReader(self, name: str, host: str, port: str) -> bool:
        return self._submit_test("reader", (name, host, port))

    @Slot(str, str, str, str, str, str, result=bool)
    def testWaveshare(
        self, port: str, baud: str, bits: str, parity: str, stop: str, device: str
    ) -> bool:
        return self._submit_test("waveshare", (port, baud, bits, parity, stop, device))

    @Slot(str, result=bool)
    def testBackend(self, url: str) -> bool:
        return self._submit_test("backend", (url,))

    @Slot()
    def beginClose(self) -> None:
        self._closed = True
        self._unsubscribe()

    def close(self) -> None:
        """Aguarda a escrita atômica após sair do event loop, sem deixar worker órfão."""

        self.beginClose()
        self._executor.shutdown(wait=True, cancel_futures=True)
        if self._runtime is None:
            self._reader.close()
            self._waveshare.close()
