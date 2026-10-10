"""Validação, persistência e teste temporário da conexão RFID."""

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
    ReaderConfigurationValidationError,
    Settings,
    validate_reader_connection,
)
from rfid_reader.domain import (
    ReaderConfigurationAction,
    ReaderConfigurationFeedback,
    ReaderConfigurationOutcome,
    ReaderConnectionSettings,
)
from rfid_reader.readers.base import (
    ReaderConnectionError,
    ReaderError,
    ReaderTimeoutError,
    RFIDReader,
)

LOGGER = logging.getLogger(__name__)
TESTING_MESSAGE = "Testando conexão..."
TEST_SUCCESS_MESSAGE = "Conexão realizada com sucesso."
TEST_FAILURE_MESSAGE = "Não foi possível conectar ao reader informado."
TEST_TIMEOUT_MESSAGE = "Tempo limite de conexão excedido."
INVENTORY_ACTIVE_MESSAGE = "Pare a leitura RFID antes de testar uma nova configuração."
SAVE_SUCCESS_MESSAGE = (
    "Configurações salvas com sucesso. Os novos dados serão usados na próxima conexão."
)
SAVE_FAILURE_MESSAGE = "Não foi possível salvar as configurações."
ReaderConfigurationListener = Callable[[ReaderConfigurationFeedback], None]
TemporaryReaderFactory = Callable[[ReaderConnectionSettings], RFIDReader]


class ReaderConfigurationWriteError(OSError):
    """Falha ao preservar ou substituir o arquivo de configuração."""


class ReaderConnectionConfigurer(Protocol):
    """Permite preparar o reader compartilhado para uma conexão futura."""

    def configure_connection(self, host: str, port: int, reader_id: str) -> None: ...


class ReaderConfigurationStore(Protocol):
    """Persistência restrita aos campos editáveis do reader."""

    def save(self, settings: ReaderConnectionSettings) -> None: ...


def _dotenv_value(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _line_ending(line: str) -> str:
    if line.endswith("\r\n"):
        return "\r\n"
    if line.endswith(("\n", "\r")):
        return line[-1]
    return ""


class DotEnvReaderConfigurationStore:
    """Salva o reader e permite reutilizar a escrita atômica de chaves validadas."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def save(self, settings: ReaderConnectionSettings) -> None:
        self.save_values(
            {
                "RFID_READER_NAME": _dotenv_value(settings.name),
                "RFID_READER_HOST": _dotenv_value(settings.host),
                "RFID_READER_PORT": str(settings.port),
            }
        )

    def save_values(self, values: dict[str, str]) -> None:
        """Reutiliza a escrita atômica para chaves validadas de configuração."""

        try:
            current = self._read_current()
            updated = self._update_values(current, values)
            self._replace(updated)
        except ReaderConfigurationWriteError:
            raise
        except (OSError, UnicodeError) as error:
            raise ReaderConfigurationWriteError(
                f"não foi possível atualizar {self._path.name}"
            ) from error

    def _read_current(self) -> str:
        try:
            with self._path.open("r", encoding="utf-8", newline="") as file:
                return file.read()
        except FileNotFoundError:
            return ""

    @staticmethod
    def _update_values(current: str, values: dict[str, str]) -> str:
        patterns = {
            variable: re.compile(rf"^(?P<prefix>\s*(?:export\s+)?{re.escape(variable)}\s*=).*$")
            for variable in values
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
        missing = [variable for variable in values if variable not in found]
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
            raise ReaderConfigurationWriteError(
                f"não foi possível substituir {self._path.name}"
            ) from error


class ReaderConfigurationService:
    """Coordena formulário, arquivo, estado em memória e conexão temporária."""

    def __init__(
        self,
        settings: Settings,
        store: ReaderConfigurationStore,
        reader: ReaderConnectionConfigurer | None,
        temporary_reader_factory: TemporaryReaderFactory | None,
        inventory_is_active: Callable[[], bool],
        listener: ReaderConfigurationListener,
    ) -> None:
        self._settings = settings
        self._store = store
        self._reader = reader
        self._temporary_reader_factory = temporary_reader_factory
        self._inventory_is_active = inventory_is_active
        self._listener = listener
        self._lock = threading.Lock()
        self._testing = False
        self._closed = False
        self._test_thread: threading.Thread | None = None

    def current(self) -> ReaderConnectionSettings:
        """Retorna uma cópia imutável dos valores atuais em memória."""

        with self._lock:
            return self._settings.reader_connection

    def save(self, name: str, host: str, port: str) -> bool:
        """Valida, persiste e prepara os valores para a próxima conexão."""

        with self._lock:
            if self._closed:
                return False
        try:
            connection = validate_reader_connection(name, host, port)
        except ReaderConfigurationValidationError as error:
            self._emit_error(ReaderConfigurationAction.SAVE, str(error))
            return False
        try:
            self._store.save(connection)
        except OSError:
            LOGGER.exception("reader_configuration_save_failed")
            self._emit_error(ReaderConfigurationAction.SAVE, SAVE_FAILURE_MESSAGE)
            return False

        with self._lock:
            self._settings = self._settings.with_reader_connection(connection)
        if self._reader is not None:
            self._reader.configure_connection(connection.host, connection.port, connection.name)
        LOGGER.info(
            "reader_configuration_saved reader_id=%s reader_host=%s reader_port=%s",
            connection.name,
            connection.host,
            connection.port,
        )
        self._emit(
            ReaderConfigurationFeedback(
                ReaderConfigurationAction.SAVE,
                ReaderConfigurationOutcome.SUCCESS,
                SAVE_SUCCESS_MESSAGE,
                connection,
            )
        )
        return True

    def test_connection(self, name: str, host: str, port: str) -> bool:
        """Inicia um teste temporário sem bloquear ou persistir o formulário."""

        if self._temporary_reader_factory is None:
            self._emit_error(
                ReaderConfigurationAction.TEST, "Teste RFID não integrado nesta etapa."
            )
            return False
        try:
            connection = validate_reader_connection(name, host, port)
        except ReaderConfigurationValidationError as error:
            self._emit_error(ReaderConfigurationAction.TEST, str(error))
            return False

        with self._lock:
            if self._closed or self._testing:
                return False
            inventory_active = self._inventory_is_active()
            if not inventory_active:
                self._testing = True
                thread = threading.Thread(
                    target=self._run_test,
                    args=(connection,),
                    name="reader-configuration-test",
                    daemon=True,
                )
                self._test_thread = thread
        if inventory_active:
            self._emit_error(ReaderConfigurationAction.TEST, INVENTORY_ACTIVE_MESSAGE)
            return False
        self._emit(
            ReaderConfigurationFeedback(
                ReaderConfigurationAction.TEST,
                ReaderConfigurationOutcome.IN_PROGRESS,
                TESTING_MESSAGE,
            )
        )
        thread.start()
        return True

    def _run_test(self, connection: ReaderConnectionSettings) -> None:
        temporary_reader: RFIDReader | None = None
        outcome = ReaderConfigurationOutcome.ERROR
        message = TEST_FAILURE_MESSAGE
        try:
            if self._temporary_reader_factory is None:
                raise ReaderConnectionError("Teste RFID não integrado nesta etapa.")
            temporary_reader = self._temporary_reader_factory(connection)
            temporary_reader.connect()
            if temporary_reader.is_connected():
                outcome = ReaderConfigurationOutcome.SUCCESS
                message = TEST_SUCCESS_MESSAGE
        except ReaderTimeoutError:
            LOGGER.info(
                "reader_configuration_test_timeout reader_id=%s reader_host=%s reader_port=%s",
                connection.name,
                connection.host,
                connection.port,
            )
            message = TEST_TIMEOUT_MESSAGE
        except ReaderConnectionError:
            LOGGER.info(
                "reader_configuration_test_unavailable reader_id=%s reader_host=%s reader_port=%s",
                connection.name,
                connection.host,
                connection.port,
            )
        except ReaderError:
            LOGGER.exception(
                "reader_configuration_test_protocol_error reader_id=%s reader_host=%s",
                connection.name,
                connection.host,
            )
        except Exception:
            LOGGER.exception(
                "reader_configuration_test_unexpected_error reader_id=%s reader_host=%s",
                connection.name,
                connection.host,
            )
        finally:
            if temporary_reader is not None:
                try:
                    temporary_reader.disconnect()
                except Exception:
                    LOGGER.exception(
                        "reader_configuration_test_disconnect_failed reader_id=%s",
                        connection.name,
                    )
                    outcome = ReaderConfigurationOutcome.ERROR
                    message = TEST_FAILURE_MESSAGE
            with self._lock:
                self._testing = False
                self._test_thread = None
            self._emit(
                ReaderConfigurationFeedback(
                    ReaderConfigurationAction.TEST,
                    outcome,
                    message,
                )
            )

    def _emit_error(self, action: ReaderConfigurationAction, message: str) -> None:
        self._emit(
            ReaderConfigurationFeedback(
                action,
                ReaderConfigurationOutcome.ERROR,
                message,
            )
        )

    def _emit(self, event: ReaderConfigurationFeedback) -> None:
        try:
            self._listener(event)
        except Exception:
            LOGGER.exception("reader_configuration_listener_failed")

    def close(self) -> None:
        """Aguarda o teste limitado por timeout antes de encerrar."""

        with self._lock:
            if self._closed:
                return
            self._closed = True
            thread = self._test_thread
        if thread is not None:
            thread.join()
