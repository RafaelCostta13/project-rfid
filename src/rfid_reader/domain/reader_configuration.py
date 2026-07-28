"""Modelos independentes para configurar a conexão RFID."""

from dataclasses import dataclass
from enum import StrEnum


@dataclass(frozen=True, slots=True)
class ReaderConnectionSettings:
    """Valores necessários para identificar e conectar um reader."""

    name: str
    host: str
    port: int


class ReaderConfigurationAction(StrEnum):
    """Ações disponíveis na tela de configuração."""

    TEST = "test"
    SAVE = "save"


class ReaderConfigurationOutcome(StrEnum):
    """Etapas e resultados apresentados pela interface."""

    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class ReaderConfigurationFeedback:
    """Mensagem produzida pelo serviço para atualização segura da tela."""

    action: ReaderConfigurationAction
    outcome: ReaderConfigurationOutcome
    message: str
    settings: ReaderConnectionSettings | None = None
