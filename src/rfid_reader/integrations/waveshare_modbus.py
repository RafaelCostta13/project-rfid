"""Teste pontual de comunicação com a Waveshare por Modbus RTU."""

from __future__ import annotations

import errno
from collections.abc import Callable
from typing import Protocol

from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusException, ModbusIOException

from rfid_reader.domain import WaveshareConnectionSettings

DEFAULT_WAVESHARE_TIMEOUT_SECONDS = 2.0
PARITY_CODES = {
    "None": "N",
    "Even": "E",
    "Odd": "O",
    "Mark": "M",
    "Space": "S",
}


class WaveshareConnectionError(RuntimeError):
    """Falha conhecida durante o teste temporário da Waveshare."""


class WavesharePortOpenError(WaveshareConnectionError):
    """A porta serial informada não pôde ser aberta."""


class WavesharePortBusyError(WavesharePortOpenError):
    """A porta serial está ocupada ou sem permissão de acesso."""


class WaveshareTimeoutError(WaveshareConnectionError):
    """A placa não respondeu dentro do timeout configurado."""


class WaveshareProtocolError(WaveshareConnectionError):
    """A placa respondeu com erro ou resposta Modbus inválida."""


class ModbusResponse(Protocol):
    """Parte da resposta necessária para validar a operação de leitura."""

    def isError(self) -> bool: ...  # noqa: N802 - API do PyModbus


class WaveshareModbusClient(Protocol):
    """Contrato mínimo do cliente usado no teste de conexão."""

    def connect(self) -> bool: ...

    def read_discrete_inputs(
        self,
        address: int,
        *,
        count: int,
        device_id: int,
    ) -> ModbusResponse: ...

    def close(self) -> None: ...


WaveshareModbusClientFactory = Callable[
    [WaveshareConnectionSettings, float],
    WaveshareModbusClient,
]


def create_modbus_client(
    settings: WaveshareConnectionSettings,
    timeout_seconds: float,
) -> WaveshareModbusClient:
    """Cria o cliente síncrono com os parâmetros validados do formulário."""

    return ModbusSerialClient(
        port=settings.serial_port,
        baudrate=settings.baud_rate,
        bytesize=settings.data_bits,
        parity=PARITY_CODES[settings.parity],
        stopbits=settings.stop_bits,
        timeout=timeout_seconds,
        retries=0,
    )


def _port_is_busy(error: BaseException) -> bool:
    error_number = getattr(error, "errno", None)
    if error_number in {errno.EACCES, errno.EBUSY}:
        return True
    message = str(error).lower()
    return any(
        marker in message
        for marker in (
            "access is denied",
            "acesso negado",
            "permission denied",
            "resource busy",
            "device or resource busy",
        )
    )


class PymodbusWaveshareConnectionTester:
    """Valida uma resposta real da placa sem escrever em coils."""

    def __init__(
        self,
        client_factory: WaveshareModbusClientFactory = create_modbus_client,
        timeout_seconds: float = DEFAULT_WAVESHARE_TIMEOUT_SECONDS,
    ) -> None:
        self._client_factory = client_factory
        self._timeout_seconds = timeout_seconds

    def test(self, settings: WaveshareConnectionSettings) -> None:
        """Abre, lê DI1/DI2 uma vez e sempre fecha a conexão temporária."""

        client = self._client_factory(settings, self._timeout_seconds)
        try:
            try:
                connected = client.connect()
            except OSError as error:
                if _port_is_busy(error):
                    raise WavesharePortBusyError from error
                raise WavesharePortOpenError from error
            if not connected:
                raise WavesharePortOpenError

            try:
                response = client.read_discrete_inputs(
                    address=0,
                    count=2,
                    device_id=settings.device_id,
                )
            except ModbusIOException as error:
                raise WaveshareTimeoutError from error
            except ModbusException as error:
                raise WaveshareProtocolError from error

            if isinstance(response, ModbusIOException):
                raise WaveshareTimeoutError
            if response.isError():
                raise WaveshareProtocolError
        finally:
            client.close()
