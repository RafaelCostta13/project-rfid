"""Modelos independentes para configurar a Waveshare."""

from dataclasses import dataclass
from enum import StrEnum


@dataclass(frozen=True, slots=True)
class WaveshareConnectionSettings:
    """Parâmetros necessários para uma conexão Modbus RTU serial."""

    serial_port: str
    baud_rate: int
    data_bits: int
    parity: str
    stop_bits: int
    device_id: int


class WaveshareConfigurationAction(StrEnum):
    """Ações disponíveis para a configuração da Waveshare."""

    TEST = "test"
    SAVE = "save"


class WaveshareConfigurationOutcome(StrEnum):
    """Etapas e resultados apresentados pela interface."""

    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class WaveshareConfigurationFeedback:
    """Mensagem produzida pelo serviço para atualização segura da tela."""

    action: WaveshareConfigurationAction
    outcome: WaveshareConfigurationOutcome
    message: str
    settings: WaveshareConnectionSettings | None = None
