"""Carregamento e validação da configuração operacional."""

from __future__ import annotations

import logging
import math
import os
import re
from collections.abc import Mapping
from dataclasses import dataclass, replace
from ipaddress import IPv4Address
from pathlib import Path
from urllib.parse import urlsplit

from rfid_reader.domain import ReaderConnectionSettings, WaveshareConnectionSettings

DEFAULT_READER_HOST = "192.168.0.214"
DEFAULT_READER_PORT = 5084
DEFAULT_READER_NAME = "fx9600-01"
DEFAULT_ANTENNAS = (1,)
DEFAULT_DEDUPLICATION_WINDOW_SECONDS = 2.0
DEFAULT_CONNECTION_TIMEOUT_SECONDS = 3.0
DEFAULT_STATUS_CHECK_INTERVAL_SECONDS = 5.0
DEFAULT_SHAREPOINT_SYNC_TIMEOUT_SECONDS = 10.0
DEFAULT_TAG_LOOKUP_QUEUE_SIZE = 100
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_WAVESHARE_SERIAL_PORT = ""
DEFAULT_WAVESHARE_BAUD_RATE = 9600
DEFAULT_WAVESHARE_DATA_BITS = 8
DEFAULT_WAVESHARE_PARITY = "None"
DEFAULT_WAVESHARE_STOP_BITS = 1
DEFAULT_WAVESHARE_DEVICE_ID = 1
DEFAULT_SYNC_CHECK_INTERVAL_SECONDS = 60.0
DEFAULT_LOCAL_DATABASE_FILENAME = "rfid-reader.sqlite3"
DEFAULT_BACKEND_BASE_URL = ""
STATION_DOCK_SUGGESTIONS = ("D01", "D02", "D03", "D04", "D05")
KNOWN_LOG_LEVELS = frozenset(logging.getLevelNamesMapping())
HOSTNAME_LABEL = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?$")
WAVESHARE_PARITIES = {
    "none": "None",
    "n": "None",
    "even": "Even",
    "e": "Even",
    "odd": "Odd",
    "o": "Odd",
    "mark": "Mark",
    "m": "Mark",
    "space": "Space",
    "s": "Space",
}


class ConfigurationError(ValueError):
    """Indica uma variável de ambiente ausente ou inválida."""


class ReaderConfigurationValidationError(ValueError):
    """Indica um campo inválido no formulário de conexão."""

    def __init__(self, variable: str, message: str) -> None:
        super().__init__(message)
        self.variable = variable


class WaveshareConfigurationValidationError(ValueError):
    """Indica um campo inválido no formulário da Waveshare."""

    def __init__(self, variable: str, message: str) -> None:
        super().__init__(message)
        self.variable = variable


@dataclass(frozen=True, slots=True)
class Settings:
    """Configurações validadas da aplicação."""

    reader_host: str
    reader_port: int
    reader_name: str
    antennas: tuple[int, ...]
    deduplication_window_seconds: float
    connection_timeout_seconds: float
    status_check_interval_seconds: float
    sharepoint_sync_url: str
    sharepoint_sync_timeout_seconds: float
    tag_lookup_queue_size: int
    local_database_path: Path
    log_level: str
    waveshare_serial_port: str = DEFAULT_WAVESHARE_SERIAL_PORT
    waveshare_baud_rate: int = DEFAULT_WAVESHARE_BAUD_RATE
    waveshare_data_bits: int = DEFAULT_WAVESHARE_DATA_BITS
    waveshare_parity: str = DEFAULT_WAVESHARE_PARITY
    waveshare_stop_bits: int = DEFAULT_WAVESHARE_STOP_BITS
    waveshare_device_id: int = DEFAULT_WAVESHARE_DEVICE_ID
    station_dock: str = ""
    sync_check_interval_seconds: float = DEFAULT_SYNC_CHECK_INTERVAL_SECONDS
    backend_base_url: str = DEFAULT_BACKEND_BASE_URL

    @property
    def reader_connection(self) -> ReaderConnectionSettings:
        """Retorna somente os valores editáveis na interface."""

        return ReaderConnectionSettings(
            name=self.reader_name,
            host=self.reader_host,
            port=self.reader_port,
        )

    def with_reader_connection(self, connection: ReaderConnectionSettings) -> Settings:
        """Cria uma configuração atualizada sem alterar os demais valores."""

        return replace(
            self,
            reader_name=connection.name,
            reader_host=connection.host,
            reader_port=connection.port,
        )

    @property
    def waveshare_connection(self) -> WaveshareConnectionSettings:
        """Retorna os valores editáveis da comunicação Modbus RTU."""

        return WaveshareConnectionSettings(
            serial_port=self.waveshare_serial_port,
            baud_rate=self.waveshare_baud_rate,
            data_bits=self.waveshare_data_bits,
            parity=self.waveshare_parity,
            stop_bits=self.waveshare_stop_bits,
            device_id=self.waveshare_device_id,
        )

    def with_waveshare_connection(self, connection: WaveshareConnectionSettings) -> Settings:
        """Cria uma configuração atualizada sem alterar os demais valores."""

        return replace(
            self,
            waveshare_serial_port=connection.serial_port,
            waveshare_baud_rate=connection.baud_rate,
            waveshare_data_bits=connection.data_bits,
            waveshare_parity=connection.parity,
            waveshare_stop_bits=connection.stop_bits,
            waveshare_device_id=connection.device_id,
        )


def validate_station_dock(value: str) -> str:
    """Aceita ausência explícita ou código de estação, sem inventar uma Doca."""

    dock = value.strip().upper()
    if dock and re.fullmatch(r"[A-Z0-9][A-Z0-9_-]{0,31}", dock) is None:
        raise ConfigurationError(
            "RFID_STATION_DOCK: use até 32 letras, números, hífen ou sublinhado."
        )
    return dock


def _sync_check_interval(environment: Mapping[str, str]) -> float:
    variable = "SYNC_CHECK_INTERVAL_SECONDS"
    interval = _positive_float(environment, variable, DEFAULT_SYNC_CHECK_INTERVAL_SECONDS)
    if interval < 30:
        raise ConfigurationError(f"{variable} deve ser maior ou igual a 30 segundos")
    return interval


def _default_local_database_path(environment: Mapping[str, str]) -> Path:
    configured = environment.get("RFID_LOCAL_DATABASE_PATH", "").strip()
    if configured:
        return Path(configured).expanduser()
    local_app_data = environment.get("LOCALAPPDATA", "").strip()
    if local_app_data:
        return Path(local_app_data) / "rfid-reader" / DEFAULT_LOCAL_DATABASE_FILENAME
    return Path.home() / "AppData" / "Local" / "rfid-reader" / DEFAULT_LOCAL_DATABASE_FILENAME


def _required_text(environment: Mapping[str, str], variable: str) -> str:
    value = environment.get(variable, "").strip()
    if not value:
        raise ConfigurationError(f"{variable} é obrigatória e não pode estar vazia")
    return value


def _integer(environment: Mapping[str, str], variable: str, default: int) -> int:
    raw_value = environment.get(variable, str(default)).strip()
    try:
        return int(raw_value)
    except ValueError as error:
        raise ConfigurationError(f"{variable} deve ser um número inteiro") from error


def _is_valid_hostname(host: str) -> bool:
    candidate = host[:-1] if host.endswith(".") else host
    if not candidate or len(candidate) > 253:
        return False
    return all(HOSTNAME_LABEL.fullmatch(label) for label in candidate.split("."))


def validate_reader_connection(
    name: str,
    host: str,
    port: str,
) -> ReaderConnectionSettings:
    """Normaliza e valida os campos editáveis da conexão."""

    normalized_name = name.strip()
    if not normalized_name:
        raise ReaderConfigurationValidationError(
            "RFID_READER_NAME",
            "Informe o nome do reader.",
        )
    if any(character in normalized_name for character in ("\r", "\n", "\0")) or (
        "${" in normalized_name
    ):
        raise ReaderConfigurationValidationError(
            "RFID_READER_NAME",
            "O nome do reader contém caracteres inválidos.",
        )

    normalized_host = host.strip()
    if not normalized_host:
        raise ReaderConfigurationValidationError(
            "RFID_READER_HOST",
            "Informe o endereço IP do reader.",
        )
    try:
        IPv4Address(normalized_host)
    except ValueError:
        numeric_ipv4_candidate = all(
            character.isdigit() or character == "." for character in normalized_host
        )
        if numeric_ipv4_candidate or not _is_valid_hostname(normalized_host):
            raise ReaderConfigurationValidationError(
                "RFID_READER_HOST",
                "Endereço IP ou hostname inválido.",
            ) from None

    normalized_port = port.strip()
    try:
        parsed_port = int(normalized_port)
    except ValueError as error:
        raise ReaderConfigurationValidationError(
            "RFID_READER_PORT",
            "A porta deve ser um número inteiro.",
        ) from error
    if not 1 <= parsed_port <= 65535:
        raise ReaderConfigurationValidationError(
            "RFID_READER_PORT",
            "A porta deve estar entre 1 e 65535.",
        )
    return ReaderConnectionSettings(
        name=normalized_name,
        host=normalized_host,
        port=parsed_port,
    )


def _waveshare_integer(value: str, variable: str, label: str) -> int:
    try:
        return int(value.strip())
    except ValueError as error:
        raise WaveshareConfigurationValidationError(
            variable,
            f"{label} deve ser um número inteiro.",
        ) from error


def validate_waveshare_connection(
    serial_port: str,
    baud_rate: str,
    data_bits: str,
    parity: str,
    stop_bits: str,
    device_id: str,
    *,
    require_serial_port: bool = False,
) -> WaveshareConnectionSettings:
    """Normaliza e valida os campos editáveis da Waveshare."""

    normalized_port = serial_port.strip()
    if require_serial_port and not normalized_port:
        raise WaveshareConfigurationValidationError(
            "WAVESHARE_SERIAL_PORT",
            "Informe a porta COM da Waveshare.",
        )
    if any(character in normalized_port for character in ("\r", "\n", "\0")) or (
        "${" in normalized_port
    ):
        raise WaveshareConfigurationValidationError(
            "WAVESHARE_SERIAL_PORT",
            "A porta COM contém caracteres inválidos.",
        )

    parsed_baud_rate = _waveshare_integer(
        baud_rate,
        "WAVESHARE_BAUD_RATE",
        "Baud rate",
    )
    if parsed_baud_rate <= 0:
        raise WaveshareConfigurationValidationError(
            "WAVESHARE_BAUD_RATE",
            "Baud rate deve ser um número inteiro maior que zero.",
        )

    parsed_data_bits = _waveshare_integer(
        data_bits,
        "WAVESHARE_DATA_BITS",
        "Data bits",
    )
    if parsed_data_bits not in {5, 6, 7, 8}:
        raise WaveshareConfigurationValidationError(
            "WAVESHARE_DATA_BITS",
            "Data bits deve ser 5, 6, 7 ou 8.",
        )

    normalized_parity = WAVESHARE_PARITIES.get(parity.strip().lower())
    if normalized_parity is None:
        raise WaveshareConfigurationValidationError(
            "WAVESHARE_PARITY",
            "Paridade deve ser None, Even, Odd, Mark ou Space.",
        )

    parsed_stop_bits = _waveshare_integer(
        stop_bits,
        "WAVESHARE_STOP_BITS",
        "Stop bits",
    )
    if parsed_stop_bits not in {1, 2}:
        raise WaveshareConfigurationValidationError(
            "WAVESHARE_STOP_BITS",
            "Stop bits deve ser 1 ou 2.",
        )

    parsed_device_id = _waveshare_integer(
        device_id,
        "WAVESHARE_DEVICE_ID",
        "Device ID",
    )
    if not 1 <= parsed_device_id <= 247:
        raise WaveshareConfigurationValidationError(
            "WAVESHARE_DEVICE_ID",
            "Device ID deve estar entre 1 e 247.",
        )

    return WaveshareConnectionSettings(
        serial_port=normalized_port,
        baud_rate=parsed_baud_rate,
        data_bits=parsed_data_bits,
        parity=normalized_parity,
        stop_bits=parsed_stop_bits,
        device_id=parsed_device_id,
    )


def _reader_connection(environment: Mapping[str, str]) -> ReaderConnectionSettings:
    try:
        return validate_reader_connection(
            environment.get("RFID_READER_NAME", DEFAULT_READER_NAME),
            environment.get("RFID_READER_HOST", DEFAULT_READER_HOST),
            environment.get("RFID_READER_PORT", str(DEFAULT_READER_PORT)),
        )
    except ReaderConfigurationValidationError as error:
        raise ConfigurationError(f"{error.variable}: {error}") from error


def _waveshare_connection(environment: Mapping[str, str]) -> WaveshareConnectionSettings:
    try:
        return validate_waveshare_connection(
            environment.get("WAVESHARE_SERIAL_PORT", DEFAULT_WAVESHARE_SERIAL_PORT),
            environment.get("WAVESHARE_BAUD_RATE", str(DEFAULT_WAVESHARE_BAUD_RATE)),
            environment.get("WAVESHARE_DATA_BITS", str(DEFAULT_WAVESHARE_DATA_BITS)),
            environment.get("WAVESHARE_PARITY", DEFAULT_WAVESHARE_PARITY),
            environment.get("WAVESHARE_STOP_BITS", str(DEFAULT_WAVESHARE_STOP_BITS)),
            environment.get("WAVESHARE_DEVICE_ID", str(DEFAULT_WAVESHARE_DEVICE_ID)),
        )
    except WaveshareConfigurationValidationError as error:
        raise ConfigurationError(f"{error.variable}: {error}") from error


def _required_https_url(environment: Mapping[str, str], variable: str) -> str:
    value = _required_text(environment, variable)
    parsed = urlsplit(value)
    if parsed.scheme.lower() != "https" or not parsed.netloc:
        raise ConfigurationError(f"{variable} deve conter uma URL HTTPS válida")
    return value


def _optional_https_url(environment: Mapping[str, str], variable: str) -> str:
    value = environment.get(variable, "").strip()
    if not value:
        return ""
    return _required_https_url(environment, variable)


def _positive_integer(environment: Mapping[str, str], variable: str, default: int) -> int:
    value = _integer(environment, variable, default)
    if value <= 0:
        raise ConfigurationError(f"{variable} deve ser um número inteiro maior que zero")
    return value


def _antennas(environment: Mapping[str, str]) -> tuple[int, ...]:
    variable = "RFID_ANTENNAS"
    raw_value = environment.get(variable, ",".join(map(str, DEFAULT_ANTENNAS))).strip()
    if not raw_value:
        raise ConfigurationError(f"{variable} deve conter ao menos uma antena")

    antennas: list[int] = []
    for raw_antenna in raw_value.split(","):
        try:
            antenna = int(raw_antenna.strip())
        except ValueError as error:
            raise ConfigurationError(
                f"{variable} deve ser uma lista de números inteiros separados por vírgula"
            ) from error
        if antenna <= 0:
            raise ConfigurationError(f"{variable} deve conter apenas inteiros positivos")
        if antenna not in antennas:
            antennas.append(antenna)
    return tuple(antennas)


def _deduplication_window(environment: Mapping[str, str]) -> float:
    variable = "RFID_DEDUPLICATION_WINDOW_SECONDS"
    raw_value = environment.get(variable, str(DEFAULT_DEDUPLICATION_WINDOW_SECONDS)).strip()
    try:
        window = float(raw_value)
    except ValueError as error:
        raise ConfigurationError(f"{variable} deve ser um número") from error
    if not math.isfinite(window) or window < 0:
        raise ConfigurationError(f"{variable} deve ser um número finito maior ou igual a zero")
    return window


def _positive_float(environment: Mapping[str, str], variable: str, default: float) -> float:
    raw_value = environment.get(variable, str(default)).strip()
    try:
        value = float(raw_value)
    except ValueError as error:
        raise ConfigurationError(f"{variable} deve ser um número") from error
    if not math.isfinite(value) or value <= 0:
        raise ConfigurationError(f"{variable} deve ser um número finito maior que zero")
    return value


def _log_level(environment: Mapping[str, str]) -> str:
    variable = "RFID_LOG_LEVEL"
    level = environment.get(variable, DEFAULT_LOG_LEVEL).strip().upper()
    if level not in KNOWN_LOG_LEVELS:
        known_levels = ", ".join(sorted(KNOWN_LOG_LEVELS))
        raise ConfigurationError(f"{variable} deve ser um destes níveis: {known_levels}")
    return level


def load_config(environment: Mapping[str, str] | None = None) -> Settings:
    """Carrega e valida configurações de um mapeamento ou do ambiente do processo."""

    source = os.environ if environment is None else environment
    reader_connection = _reader_connection(source)
    waveshare_connection = _waveshare_connection(source)
    return Settings(
        reader_host=reader_connection.host,
        reader_port=reader_connection.port,
        reader_name=reader_connection.name,
        antennas=_antennas(source),
        deduplication_window_seconds=_deduplication_window(source),
        connection_timeout_seconds=_positive_float(
            source,
            "RFID_CONNECTION_TIMEOUT_SECONDS",
            DEFAULT_CONNECTION_TIMEOUT_SECONDS,
        ),
        status_check_interval_seconds=_positive_float(
            source,
            "RFID_STATUS_CHECK_INTERVAL_SECONDS",
            DEFAULT_STATUS_CHECK_INTERVAL_SECONDS,
        ),
        sharepoint_sync_url=_optional_https_url(source, "SHAREPOINT_SYNC_URL"),
        sharepoint_sync_timeout_seconds=_positive_float(
            source,
            "SHAREPOINT_SYNC_TIMEOUT_SECONDS",
            DEFAULT_SHAREPOINT_SYNC_TIMEOUT_SECONDS,
        ),
        tag_lookup_queue_size=_positive_integer(
            source,
            "TAG_LOOKUP_QUEUE_SIZE",
            DEFAULT_TAG_LOOKUP_QUEUE_SIZE,
        ),
        local_database_path=_default_local_database_path(source),
        log_level=_log_level(source),
        waveshare_serial_port=waveshare_connection.serial_port,
        waveshare_baud_rate=waveshare_connection.baud_rate,
        waveshare_data_bits=waveshare_connection.data_bits,
        waveshare_parity=waveshare_connection.parity,
        waveshare_stop_bits=waveshare_connection.stop_bits,
        waveshare_device_id=waveshare_connection.device_id,
        station_dock=validate_station_dock(source.get("RFID_STATION_DOCK", "")),
        sync_check_interval_seconds=_sync_check_interval(source),
        backend_base_url=source.get("RFID_BACKEND_BASE_URL", "").strip(),
    )
