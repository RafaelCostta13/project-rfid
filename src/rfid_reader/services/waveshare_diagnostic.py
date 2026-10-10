"""Diagnóstico manual da Waveshare em uma única thread de comunicação."""

from __future__ import annotations

import logging
import queue
import threading
from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

from rfid_reader.domain import ConnectionKind, ConnectionStatus, WaveshareConnectionSettings
from rfid_reader.integrations.waveshare_modbus import (
    WaveshareConnectionError,
    WaveshareDiagnosticPort,
    WavesharePortBusyError,
    WavesharePortOpenError,
    WaveshareSerialGate,
    WaveshareTimeoutError,
)
from rfid_reader.services.automatic_inventory import AutomaticInventoryController

LOGGER = logging.getLogger(__name__)
POLL_INTERVAL_SECONDS = 0.5
PORT_REQUIRED_MESSAGE = "Configure a porta COM da Waveshare antes de iniciar o teste."


class DiagnosticEventKind(StrEnum):
    AUTOMATIC = "automatic"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    INPUTS = "inputs"
    RELAYS = "relays"
    RELAY_ERROR = "relay_error"
    DISCONNECTED = "disconnected"


@dataclass(frozen=True, slots=True)
class DiagnosticEvent:
    kind: DiagnosticEventKind
    message: str = ""
    states: tuple[bool, ...] = ()
    channel: int = 0


class DiagnosticPort(Protocol):
    def connect(self) -> tuple[bool, ...]: ...

    def read_inputs(self) -> tuple[bool, ...]: ...

    def read_relays(self) -> tuple[bool, ...]: ...

    def set_relay(self, channel: int, enabled: bool) -> bool: ...

    def close(self) -> None: ...


class WaveshareConnectionTester(Protocol):
    def test(self, settings: WaveshareConnectionSettings) -> None: ...


class WaveshareDiagnosticService:
    """Serializa leitura e escrita na COM, emitindo eventos para a UI."""

    def __init__(
        self,
        get_settings: Callable[[], WaveshareConnectionSettings],
        listener: Callable[[DiagnosticEvent], None],
        port_factory: Callable[
            [WaveshareConnectionSettings], DiagnosticPort
        ] = WaveshareDiagnosticPort,
        serial_gate: WaveshareSerialGate | None = None,
        automatic: AutomaticInventoryController | None = None,
    ) -> None:
        self._get_settings = get_settings
        self._listener = listener
        self._port_factory = port_factory
        self._serial_gate = serial_gate or WaveshareSerialGate()
        self._commands: queue.Queue[tuple[int, bool]] = queue.Queue()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._guard = threading.Lock()
        self._session_status = ConnectionStatus.DISCONNECTED
        self._automatic = automatic
        self._operational = False
        self._manual_control = False

    def connect_automatic(self) -> None:
        """Mantém a sessão operacional; habilitar RFID continua sendo ação da tela Start."""

        with self._guard:
            if self._thread is not None and self._thread.is_alive():
                return
            self._operational = True
            self._manual_control = False
        self._connect_worker()

    def resume_automatic(self) -> None:
        """Entrega CH1–CH3 ao controller, usando a sessão serial já aberta."""

        with self._guard:
            self._operational = True
            self._manual_control = False
        self.connect_automatic()
        self._listener(DiagnosticEvent(DiagnosticEventKind.AUTOMATIC))

    def probe_status(self, tester: WaveshareConnectionTester) -> ConnectionStatus:
        """Confirma resposta Modbus sem disputar uma sessão ativa."""

        settings = self._get_settings()
        if not settings.serial_port.strip():
            return ConnectionStatus.DISCONNECTED
        try:
            tester.test(settings)
        except WavesharePortBusyError:
            if not self._serial_gate.is_locked():
                return ConnectionStatus.DISCONNECTED
            with self._guard:
                return (
                    self._session_status
                    if self._session_status is not ConnectionStatus.DISCONNECTED
                    else ConnectionStatus.CHECKING
                )
        except (WavesharePortOpenError, WaveshareTimeoutError):
            return ConnectionStatus.DISCONNECTED
        except WaveshareConnectionError:
            LOGGER.exception("waveshare_status_protocol_error port=%s", settings.serial_port)
            return ConnectionStatus.ERROR
        return ConnectionStatus.CONNECTED

    def connect(self) -> None:
        with self._guard:
            if self._thread is not None and self._thread.is_alive():
                self._manual_control = not (self._automatic is not None and self._automatic.enabled)
                self._listener(DiagnosticEvent(DiagnosticEventKind.CONNECTED))
                if not self._manual_control:
                    self._listener(DiagnosticEvent(DiagnosticEventKind.AUTOMATIC))
                return
            self._operational = False
            self._manual_control = True
        self._connect_worker()

    def _connect_worker(self) -> None:
        with self._guard:
            settings = self._get_settings()
            if not settings.serial_port.strip():
                self._listener(
                    DiagnosticEvent(DiagnosticEventKind.DISCONNECTED, PORT_REQUIRED_MESSAGE)
                )
                return
            self._stop.clear()
            self._session_status = ConnectionStatus.CHECKING
            self._commands = queue.Queue()
            self._thread = threading.Thread(
                target=self._run,
                args=(settings,),
                name="waveshare-diagnostic",
                daemon=True,
            )
            self._listener(DiagnosticEvent(DiagnosticEventKind.CONNECTING))
            self._thread.start()

    def set_relay(self, channel: int, enabled: bool) -> None:
        if channel not in range(1, 9):
            raise ValueError("Canal de relé inválido.")
        if channel <= 3 and self._automatic is not None and self._automatic.enabled:
            return
        if channel <= 3 and self._operational and not self._manual_control:
            return
        if self._thread is not None and self._thread.is_alive() and not self._stop.is_set():
            self._commands.put((channel, enabled))

    def disconnect(self) -> None:
        with self._guard:
            if self._operational and self._automatic is not None and self._automatic.enabled:
                self._listener(
                    DiagnosticEvent(
                        DiagnosticEventKind.AUTOMATIC,
                        "Pare a leitura automática antes de desconectar a Waveshare.",
                    )
                )
                return
            if self._operational and self._manual_control:
                self._manual_control = False
                self._listener(DiagnosticEvent(DiagnosticEventKind.DISCONNECTED))
                return
        self._stop.set()

    def close(self) -> None:
        self._stop.set()
        thread = self._thread
        if thread is not None and thread.is_alive():
            thread.join()

    def _run(self, settings: WaveshareConnectionSettings) -> None:
        port: DiagnosticPort | None = None
        message = ""
        connected = False
        self._serial_gate.acquire()
        try:
            if self._stop.is_set():
                return
            port = self._port_factory(settings)
            inputs = port.connect()
            if self._stop.is_set():
                return
            connected = True
            with self._guard:
                self._session_status = ConnectionStatus.CONNECTED
                operational = self._operational
            self._listener(DiagnosticEvent(DiagnosticEventKind.CONNECTED))
            if self._automatic is not None:
                self._automatic.update_connection_status(
                    ConnectionKind.WAVESHARE, ConnectionStatus.CONNECTED
                )
            if operational:
                self._listener(DiagnosticEvent(DiagnosticEventKind.AUTOMATIC))
            self._listener(DiagnosticEvent(DiagnosticEventKind.INPUTS, states=inputs))
            try:
                relays = port.read_relays()
            except WaveshareConnectionError:
                LOGGER.exception("waveshare_relay_state_unavailable port=%s", settings.serial_port)
            else:
                self._listener(DiagnosticEvent(DiagnosticEventKind.RELAYS, states=relays))
            self._update_automatic(port, inputs)
            while not self._stop.is_set():
                with self._guard:
                    automatic = self._operational and not self._manual_control
                try:
                    channel, enabled = self._commands.get(
                        timeout=0.05 if automatic else POLL_INTERVAL_SECONDS
                    )
                except queue.Empty:
                    inputs = port.read_inputs()
                    self._listener(DiagnosticEvent(DiagnosticEventKind.INPUTS, states=inputs))
                    self._update_automatic(port, inputs)
                    continue
                if self._stop.is_set():
                    break
                if channel <= 3 and self._automatic is not None and self._automatic.enabled:
                    continue
                with self._guard:
                    automatic = self._operational and not self._manual_control
                if automatic:
                    inputs = port.read_inputs()
                    self._listener(DiagnosticEvent(DiagnosticEventKind.INPUTS, states=inputs))
                    self._update_automatic(port, inputs)
                    if channel <= 3:
                        continue
                try:
                    confirmed = port.set_relay(channel, enabled)
                    if confirmed != enabled:
                        raise WaveshareConnectionError("Estado do relé diferente do solicitado.")
                except WaveshareConnectionError:
                    LOGGER.exception("waveshare_relay_command_failed channel=%s", channel)
                    self._listener(
                        DiagnosticEvent(
                            DiagnosticEventKind.RELAY_ERROR,
                            f"Falha ao controlar CH{channel}. Verifique o dispositivo.",
                            channel=channel,
                        )
                    )
                else:
                    self._listener(
                        DiagnosticEvent(
                            DiagnosticEventKind.RELAYS,
                            states=(confirmed,),
                            channel=channel,
                        )
                    )
        except WaveshareConnectionError:
            LOGGER.exception(
                "waveshare_diagnostic_communication_failed port=%s", settings.serial_port
            )
            message = (
                "Comunicação com a Waveshare perdida."
                if connected
                else "Não foi possível conectar à Waveshare."
            )
        except OSError:
            LOGGER.exception("waveshare_diagnostic_port_failed port=%s", settings.serial_port)
            message = "Não foi possível conectar à Waveshare."
        except Exception:
            LOGGER.exception("waveshare_diagnostic_unexpected_failed port=%s", settings.serial_port)
            message = "Falha inesperada na comunicação com a Waveshare."
        finally:
            with self._guard:
                operational = self._operational
            if self._automatic is not None and operational:
                self._automatic.update_connection_status(
                    ConnectionKind.WAVESHARE, ConnectionStatus.DISCONNECTED
                )
                if port is not None and not message:
                    try:
                        for channel in (1, 2, 3):
                            if port.set_relay(channel, False):
                                raise WaveshareConnectionError(
                                    f"CH{channel} não confirmou o desligamento."
                                )
                    except WaveshareConnectionError:
                        LOGGER.exception("automatic_relay_cleanup_failed")
            if port is not None:
                try:
                    port.close()
                except OSError:
                    LOGGER.exception(
                        "waveshare_diagnostic_close_failed port=%s", settings.serial_port
                    )
            with self._guard:
                self._session_status = ConnectionStatus.DISCONNECTED
                self._operational = False
                self._manual_control = False
            self._serial_gate.release()
            self._listener(DiagnosticEvent(DiagnosticEventKind.DISCONNECTED, message))

    def _update_automatic(self, port: DiagnosticPort, inputs: tuple[bool, ...]) -> None:
        with self._guard:
            operational = self._operational and not self._manual_control
        if self._automatic is None or not operational:
            return

        def confirmed_relay(channel: int, enabled: bool) -> bool:
            confirmed = port.set_relay(channel, enabled)
            if confirmed != enabled:
                raise WaveshareConnectionError(f"CH{channel} não confirmou o comando.")
            self._listener(
                DiagnosticEvent(DiagnosticEventKind.RELAYS, states=(confirmed,), channel=channel)
            )
            return confirmed

        self._automatic.update(inputs, confirmed_relay)
