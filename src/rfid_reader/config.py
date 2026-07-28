"""Carregamento e validação da configuração operacional."""

from __future__ import annotations

import logging
import math
import os
import re
from collections.abc import Mapping
from dataclasses import dataclass, replace
from ipaddress import IPv4Address
from urllib.parse import urlsplit

from rfid_reader.domain import ReaderConnectionSettings

DEFAULT_READER_HOST = "192.168.0.214"
DEFAULT_READER_PORT = 5084
DEFAULT_READER_NAME = "fx9600-01"
DEFAULT_ANTENNAS = (1,)
DEFAULT_DEDUPLICATION_WINDOW_SECONDS = 2.0
DEFAULT_CONNECTION_TIMEOUT_SECONDS = 3.0
DEFAULT_STATUS_CHECK_INTERVAL_SECONDS = 5.0
DEFAULT_SHAREPOINT_LOOKUP_TIMEOUT_SECONDS = 10.0
DEFAULT_SHAREPOINT_LOOKUP_QUEUE_SIZE = 100
DEFAULT_LOG_LEVEL = "INFO"
KNOWN_LOG_LEVELS = frozenset(logging.getLevelNamesMapping())
HOSTNAME_LABEL = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?$")


class ConfigurationError(ValueError):
    """Indica uma variável de ambiente ausente ou inválida."""


class ReaderConfigurationValidationError(ValueError):
    """Indica um campo inválido no formulário de conexão."""

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
    sharepoint_lookup_url: str
    sharepoint_lookup_timeout_seconds: float
    sharepoint_lookup_queue_size: int
    log_level: str

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


def _reader_connection(environment: Mapping[str, str]) -> ReaderConnectionSettings:
    try:
        return validate_reader_connection(
            environment.get("RFID_READER_NAME", DEFAULT_READER_NAME),
            environment.get("RFID_READER_HOST", DEFAULT_READER_HOST),
            environment.get("RFID_READER_PORT", str(DEFAULT_READER_PORT)),
        )
    except ReaderConfigurationValidationError as error:
        raise ConfigurationError(f"{error.variable}: {error}") from error


def _required_https_url(environment: Mapping[str, str], variable: str) -> str:
    value = _required_text(environment, variable)
    parsed = urlsplit(value)
    if parsed.scheme.lower() != "https" or not parsed.netloc:
        raise ConfigurationError(f"{variable} deve conter uma URL HTTPS válida")
    return value


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
        sharepoint_lookup_url=_required_https_url(source, "SHAREPOINT_LOOKUP_URL"),
        sharepoint_lookup_timeout_seconds=_positive_float(
            source,
            "SHAREPOINT_LOOKUP_TIMEOUT_SECONDS",
            DEFAULT_SHAREPOINT_LOOKUP_TIMEOUT_SECONDS,
        ),
        sharepoint_lookup_queue_size=_positive_integer(
            source,
            "SHAREPOINT_LOOKUP_QUEUE_SIZE",
            DEFAULT_SHAREPOINT_LOOKUP_QUEUE_SIZE,
        ),
        log_level=_log_level(source),
    )
