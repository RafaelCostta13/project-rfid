"""Teste pontual de comunicação com a Waveshare por Modbus RTU."""

from __future__ import annotations

import errno
import threading
from collections.abc import Callable
from typing import Protocol, cast

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


class WaveshareSerialGate:
    """Impede que testes temporários disputem a COM com o diagnóstico."""

    def __init__(self) -> None:
        self._lock = threading.Lock()

    def try_acquire(self) -> bool:
        return self._lock.acquire(blocking=False)

    def acquire(self) -> None:
        self._lock.acquire()

    def release(self) -> None:
        self._lock.release()

    def is_locked(self) -> bool:
        return self._lock.locked()


class ModbusResponse(Protocol):
    """Parte da resposta necessária para validar a operação de leitura."""

    def isError(self) -> bool: ...  # noqa: N802 - API do PyModbus


class ModbusBitsResponse(ModbusResponse, Protocol):
    bits: list[bool]


class WaveshareModbusClient(Protocol):
    """Contrato mínimo do cliente usado no teste de conexão."""

    def connect(self) -> bool: ...

    def read_discrete_inputs(
        self,
        address: int,
        *,
        count: int,
        device_id: int,
    ) -> ModbusBitsResponse: ...

    def read_coils(self, address: int, *, count: int, device_id: int) -> ModbusBitsResponse: ...

    def write_coil(self, address: int, value: bool, *, device_id: int) -> ModbusResponse: ...

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

    return cast(
        WaveshareModbusClient,
        ModbusSerialClient(
            port=settings.serial_port,
            baudrate=settings.baud_rate,
            bytesize=settings.data_bits,
            parity=PARITY_CODES[settings.parity],
            stopbits=settings.stop_bits,
            timeout=timeout_seconds,
            retries=0,
        ),
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
        serial_gate: WaveshareSerialGate | None = None,
    ) -> None:
        self._client_factory = client_factory
        self._timeout_seconds = timeout_seconds
        self._serial_gate = serial_gate

    def test(self, settings: WaveshareConnectionSettings) -> None:
        """Abre, lê DI1/DI2 uma vez e sempre fecha a conexão temporária."""

        gate = self._serial_gate
        if gate is not None and not gate.try_acquire():
            raise WavesharePortBusyError("A porta COM está em uso.")
        try:
            self._test_with_port(settings)
        finally:
            if gate is not None:
                gate.release()

    def _test_with_port(self, settings: WaveshareConnectionSettings) -> None:
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


class WaveshareDiagnosticPort:
    """Uma sessão Modbus usada exclusivamente pelo worker de diagnóstico."""

    def __init__(
        self,
        settings: WaveshareConnectionSettings,
        client_factory: WaveshareModbusClientFactory = create_modbus_client,
    ) -> None:
        self._settings = settings
        self._client = client_factory(settings, DEFAULT_WAVESHARE_TIMEOUT_SECONDS)

    def connect(self) -> tuple[bool, ...]:
        try:
            if not self._client.connect():
                raise WavesharePortOpenError("Não foi possível abrir a porta COM.")
        except OSError as error:
            if _port_is_busy(error):
                raise WavesharePortBusyError from error
            raise WavesharePortOpenError from error
        except ModbusException as error:
            raise WaveshareProtocolError("Falha ao abrir a sessão Modbus.") from error
        return self.read_inputs()

    def read_inputs(self) -> tuple[bool, ...]:
        return self._read_bits(self._client.read_discrete_inputs, 0, 5)

    def read_relays(self) -> tuple[bool, ...]:
        return self._read_bits(self._client.read_coils, 0, 8)

    def set_relay(self, channel: int, enabled: bool) -> bool:
        if channel not in range(1, 9):
            raise ValueError("Canal de relé inválido.")
        try:
            response = self._client.write_coil(
                channel - 1, enabled, device_id=self._settings.device_id
            )
            self._check(response)
            return self._read_bits(self._client.read_coils, channel - 1, 1)[0]
        except (OSError, ModbusException) as error:
            raise WaveshareProtocolError("Falha no comando do relé.") from error

    def close(self) -> None:
        self._client.close()

    def _read_bits(
        self,
        read: Callable[..., ModbusBitsResponse],
        address: int,
        count: int,
    ) -> tuple[bool, ...]:
        try:
            response = read(address, count=count, device_id=self._settings.device_id)
        except (OSError, ModbusIOException) as error:
            raise WaveshareTimeoutError("A Waveshare não respondeu.") from error
        except ModbusException as error:
            raise WaveshareProtocolError("Resposta Modbus inválida.") from error
        self._check(response)
        if len(response.bits) < count:
            raise WaveshareProtocolError("Resposta Modbus incompleta.")
        return tuple(bool(bit) for bit in response.bits[:count])

    @staticmethod
    def _check(response: ModbusResponse) -> None:
        if isinstance(response, ModbusIOException):
            raise WaveshareTimeoutError("A Waveshare não respondeu.")
        if response.isError():
            raise WaveshareProtocolError("A Waveshare retornou um erro Modbus.")
