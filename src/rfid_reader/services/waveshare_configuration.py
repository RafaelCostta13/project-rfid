"""Validação, persistência e teste temporário da Waveshare."""

from __future__ import annotations

import logging
import os
import re
import tempfile
import threading
from collections.abc import Callable
from pathlib import Path
from typing import Protocol

from rfid_reader.config import (
    Settings,
    WaveshareConfigurationValidationError,
    validate_waveshare_connection,
)
from rfid_reader.domain import (
    WaveshareConfigurationAction,
    WaveshareConfigurationFeedback,
    WaveshareConfigurationOutcome,
    WaveshareConnectionSettings,
)
from rfid_reader.integrations.waveshare_modbus import (
    WavesharePortBusyError,
    WavesharePortOpenError,
    WaveshareTimeoutError,
)

LOGGER = logging.getLogger(__name__)
TESTING_MESSAGE = "Testando conexão com a Waveshare..."
TEST_SUCCESS_MESSAGE = "Conexão com a Waveshare realizada com sucesso."
TEST_FAILURE_MESSAGE = "Não foi possível conectar à Waveshare."
PORT_REQUIRED_MESSAGE = "Informe a porta COM da Waveshare."
PORT_OPEN_FAILURE_MESSAGE = "Não foi possível abrir a porta COM informada."
PORT_BUSY_MESSAGE = "A porta COM está sendo utilizada por outro processo."
SAVE_SUCCESS_MESSAGE = "Configurações da Waveshare salvas com sucesso."
SAVE_FAILURE_MESSAGE = "Não foi possível salvar as configurações da Waveshare."
WAVESHARE_ENV_VARIABLES = (
    "WAVESHARE_SERIAL_PORT",
    "WAVESHARE_BAUD_RATE",
    "WAVESHARE_DATA_BITS",
    "WAVESHARE_PARITY",
    "WAVESHARE_STOP_BITS",
    "WAVESHARE_DEVICE_ID",
)
WaveshareConfigurationListener = Callable[[WaveshareConfigurationFeedback], None]


class WaveshareConfigurationWriteError(OSError):
    """Falha ao preservar ou substituir o arquivo de configuração."""


class WaveshareConfigurationStore(Protocol):
    """Persistência restrita aos parâmetros da Waveshare."""

    def save(self, settings: WaveshareConnectionSettings) -> None: ...


class WaveshareConnectionTester(Protocol):
    """Executa uma operação Modbus de leitura e encerra sua conexão."""

    def test(self, settings: WaveshareConnectionSettings) -> None: ...


def _dotenv_value(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _line_ending(line: str) -> str:
    if line.endswith("\r\n"):
        return "\r\n"
    if line.endswith(("\n", "\r")):
        return line[-1]
    return ""


class DotEnvWaveshareConfigurationStore:
    """Atualiza somente chaves da Waveshare por substituição atômica."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def save(self, settings: WaveshareConnectionSettings) -> None:
        try:
            current = self._read_current()
            updated = self._update_content(current, settings)
            self._replace(updated)
        except WaveshareConfigurationWriteError:
            raise
        except (OSError, UnicodeError) as error:
            raise WaveshareConfigurationWriteError(
                f"não foi possível atualizar {self._path.name}"
            ) from error

    def _read_current(self) -> str:
        try:
            with self._path.open("r", encoding="utf-8", newline="") as file:
                return file.read()
        except FileNotFoundError:
            return ""

    @staticmethod
    def _update_content(current: str, settings: WaveshareConnectionSettings) -> str:
        values = {
            "WAVESHARE_SERIAL_PORT": _dotenv_value(settings.serial_port),
            "WAVESHARE_BAUD_RATE": str(settings.baud_rate),
            "WAVESHARE_DATA_BITS": str(settings.data_bits),
            "WAVESHARE_PARITY": _dotenv_value(settings.parity),
            "WAVESHARE_STOP_BITS": str(settings.stop_bits),
            "WAVESHARE_DEVICE_ID": str(settings.device_id),
        }
        patterns = {
            variable: re.compile(rf"^(?P<prefix>\s*(?:export\s+)?{variable}\s*=).*$")
            for variable in WAVESHARE_ENV_VARIABLES
        }
        found: set[str] = set()
        lines: list[str] = []
        for original_line in current.splitlines(keepends=True):
            ending = _line_ending(original_line)
            content = original_line[: -len(ending)] if ending else original_line
            for variable, pattern in patterns.items():
                match = pattern.fullmatch(content)
                if match is not None:
                    content = f"{match.group('prefix')}{values[variable]}"
                    found.add(variable)
                    break
            lines.append(f"{content}{ending}")

        newline = "\r\n" if "\r\n" in current else "\n"
        missing = [variable for variable in WAVESHARE_ENV_VARIABLES if variable not in found]
        if missing and lines and not _line_ending(lines[-1]):
            lines[-1] = f"{lines[-1]}{newline}"
        lines.extend(f"{variable}={values[variable]}{newline}" for variable in missing)
        return "".join(lines)

    def _replace(self, content: str) -> None:
        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                newline="",
                dir=self._path.parent,
                prefix=f".{self._path.name}.",
                suffix=".tmp",
                delete=False,
            ) as temporary:
                temporary_path = Path(temporary.name)
                temporary.write(content)
                temporary.flush()
                os.fsync(temporary.fileno())
            os.replace(temporary_path, self._path)
        except OSError as error:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
            raise WaveshareConfigurationWriteError(
                f"não foi possível substituir {self._path.name}"
            ) from error


class WaveshareConfigurationService:
    """Coordena formulário, arquivo, memória e teste Modbus temporário."""

    def __init__(
        self,
        settings: Settings,
        store: WaveshareConfigurationStore,
        tester: WaveshareConnectionTester | None,
        listener: WaveshareConfigurationListener,
    ) -> None:
        self._settings = settings
        self._store = store
        self._tester = tester
        self._listener = listener
        self._lock = threading.Lock()
        self._testing = False
        self._closed = False
        self._test_thread: threading.Thread | None = None

    def current(self) -> WaveshareConnectionSettings:
        """Retorna uma cópia imutável dos valores atuais em memória."""

        with self._lock:
            return self._settings.waveshare_connection

    def save(
        self,
        serial_port: str,
        baud_rate: str,
        data_bits: str,
        parity: str,
        stop_bits: str,
        device_id: str,
    ) -> bool:
        """Valida e persiste os valores, permitindo porta serial vazia."""

        with self._lock:
            if self._closed:
                return False
        try:
            connection = validate_waveshare_connection(
                serial_port,
                baud_rate,
                data_bits,
                parity,
                stop_bits,
                device_id,
            )
        except WaveshareConfigurationValidationError as error:
            self._emit_error(WaveshareConfigurationAction.SAVE, str(error))
            return False
        try:
            self._store.save(connection)
        except OSError:
            LOGGER.exception("waveshare_configuration_save_failed")
            self._emit_error(WaveshareConfigurationAction.SAVE, SAVE_FAILURE_MESSAGE)
            return False

        with self._lock:
            self._settings = self._settings.with_waveshare_connection(connection)
        LOGGER.info(
            "waveshare_configuration_saved serial_port=%s device_id=%s",
            connection.serial_port or "not_configured",
            connection.device_id,
        )
        self._emit(
            WaveshareConfigurationFeedback(
                WaveshareConfigurationAction.SAVE,
                WaveshareConfigurationOutcome.SUCCESS,
                SAVE_SUCCESS_MESSAGE,
                connection,
            )
        )
        return True

    def test_connection(
        self,
        serial_port: str,
        baud_rate: str,
        data_bits: str,
        parity: str,
        stop_bits: str,
        device_id: str,
    ) -> bool:
        """Inicia uma leitura Modbus temporária sem bloquear nem persistir."""

        if self._tester is None:
            self._emit_error(
                WaveshareConfigurationAction.TEST, "Teste Waveshare não integrado nesta etapa."
            )
            return False
        try:
            connection = validate_waveshare_connection(
                serial_port,
                baud_rate,
                data_bits,
                parity,
                stop_bits,
                device_id,
                require_serial_port=True,
            )
        except WaveshareConfigurationValidationError as error:
            message = PORT_REQUIRED_MESSAGE if not serial_port.strip() else str(error)
            self._emit_error(WaveshareConfigurationAction.TEST, message)
            return False

        with self._lock:
            if self._closed or self._testing:
                return False
            self._testing = True
            thread = threading.Thread(
                target=self._run_test,
                args=(connection,),
                name="waveshare-configuration-test",
                daemon=True,
            )
            self._test_thread = thread
        self._emit(
            WaveshareConfigurationFeedback(
                WaveshareConfigurationAction.TEST,
                WaveshareConfigurationOutcome.IN_PROGRESS,
                TESTING_MESSAGE,
            )
        )
        thread.start()
        return True

    def _run_test(self, connection: WaveshareConnectionSettings) -> None:
        outcome = WaveshareConfigurationOutcome.ERROR
        message = TEST_FAILURE_MESSAGE
        try:
            if self._tester is None:
                return
            self._tester.test(connection)
            outcome = WaveshareConfigurationOutcome.SUCCESS
            message = TEST_SUCCESS_MESSAGE
        except WavesharePortBusyError:
            LOGGER.info(
                "waveshare_connection_test_port_busy serial_port=%s",
                connection.serial_port,
            )
            message = PORT_BUSY_MESSAGE
        except WavesharePortOpenError:
            LOGGER.info(
                "waveshare_connection_test_port_unavailable serial_port=%s",
                connection.serial_port,
            )
            message = PORT_OPEN_FAILURE_MESSAGE
        except WaveshareTimeoutError:
            LOGGER.info(
                "waveshare_connection_test_timeout serial_port=%s device_id=%s",
                connection.serial_port,
                connection.device_id,
            )
        except Exception:
            LOGGER.exception(
                "waveshare_connection_test_failed serial_port=%s device_id=%s",
                connection.serial_port,
                connection.device_id,
            )
        finally:
            with self._lock:
                self._testing = False
                self._test_thread = None
            self._emit(
                WaveshareConfigurationFeedback(
                    WaveshareConfigurationAction.TEST,
                    outcome,
                    message,
                )
            )

    def _emit_error(self, action: WaveshareConfigurationAction, message: str) -> None:
        self._emit(
            WaveshareConfigurationFeedback(
                action,
                WaveshareConfigurationOutcome.ERROR,
                message,
            )
        )

    def _emit(self, event: WaveshareConfigurationFeedback) -> None:
        try:
            self._listener(event)
        except Exception:
            LOGGER.exception("waveshare_configuration_listener_failed")

    def close(self) -> None:
        """Aguarda o teste limitado pelo timeout antes de encerrar."""

        with self._lock:
            if self._closed:
                return
            self._closed = True
            thread = self._test_thread
        if thread is not None:
            thread.join()
