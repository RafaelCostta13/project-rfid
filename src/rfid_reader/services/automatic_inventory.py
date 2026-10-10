"""Orquestração do inventário automático acionado por DI1 e DI2."""

from __future__ import annotations

import logging
import threading
from collections.abc import Callable
from typing import Protocol

from rfid_reader.domain import ConnectionKind, ConnectionStatus, InventoryStatus
from rfid_reader.integrations.waveshare_modbus import WaveshareConnectionError

LOGGER = logging.getLogger(__name__)
READ_TIMEOUT_SECONDS = 60.0
OPERATIONAL_CONNECTIONS = (
    ConnectionKind.INTERNET,
    ConnectionKind.RFID,
    ConnectionKind.WAVESHARE,
    ConnectionKind.SYSTEM,
)


class InventoryPort(Protocol):
    @property
    def status(self) -> InventoryStatus: ...

    def start(self) -> bool: ...

    def stop(self) -> bool: ...


class CycleTimer(Protocol):
    def start(self) -> None: ...

    def cancel(self) -> None: ...


def create_timer(seconds: float, callback: Callable[[], None]) -> CycleTimer:
    timer = threading.Timer(seconds, callback)
    timer.daemon = True
    return timer


class AutomaticInventoryController:
    """Arbitra inventário manual/automático e invalida timers por geração.

    Somente o worker Modbus chama update e escreve relés. O timer pode parar
    RFID independentemente de uma leitura serial bloqueada.
    """

    def __init__(
        self,
        inventory: InventoryPort,
        timer_factory: Callable[[float, Callable[[], None]], CycleTimer] = create_timer,
        mode_listener: Callable[[bool], None] = lambda enabled: None,
    ) -> None:
        self._inventory = inventory
        self._timer_factory = timer_factory
        self._mode_listener = mode_listener
        self._lock = threading.RLock()
        self._statuses = {kind: ConnectionStatus.CHECKING for kind in ConnectionKind}
        self._backend_observed = False
        self._enabled = False
        self._closed = False
        self._previous: tuple[bool, bool] | None = None
        self._armed = False
        self._active = False
        self._generation = 0
        self._timer: CycleTimer | None = None
        self._relays: dict[int, bool] = {}

    @property
    def enabled(self) -> bool:
        with self._lock:
            return self._enabled

    @property
    def ready(self) -> bool:
        with self._lock:
            return self._is_ready()

    def update_connection_status(self, kind: ConnectionKind, status: ConnectionStatus) -> None:
        """Atualiza uma dependência e interrompe ciclos que perderam pré-condições."""

        mode_changed = False
        with self._lock:
            if kind is ConnectionKind.SYSTEM:
                self._backend_observed = True
            previous = self._statuses[kind]
            self._statuses[kind] = status
            if previous is status:
                return
            LOGGER.info(
                "automatic_dependency_status connection=%s status=%s",
                kind.value,
                status.value,
            )
            if kind in OPERATIONAL_CONNECTIONS and status is not ConnectionStatus.CONNECTED:
                self._previous = None
                self._armed = False
                self._finish(f"{kind.value}_unavailable")
                if kind is ConnectionKind.WAVESHARE and self._enabled:
                    self._enabled = False
                    mode_changed = True
        if mode_changed:
            self._notify_mode(False)

    def _is_ready(self) -> bool:
        required: tuple[ConnectionKind, ...] = OPERATIONAL_CONNECTIONS
        if not self._backend_observed:
            required = tuple(kind for kind in required if kind is not ConnectionKind.SYSTEM)
        return all(self._statuses[kind] is ConnectionStatus.CONNECTED for kind in required)

    def enable(self) -> bool:
        with self._lock:
            if (
                self._closed
                or self._enabled
                or not self._is_ready()
                or self._inventory.status is not InventoryStatus.STOPPED
            ):
                LOGGER.warning(
                    "automatic_inventory_enable_blocked ready=%s inventory=%s",
                    self._is_ready(),
                    self._inventory.status.value,
                )
                return False
            self._enabled = True
            self._previous = None
            self._armed = False
            self._relays.clear()
            LOGGER.info("automatic_inventory_enabled")
        self._notify_mode(True)
        return True

    def manual_start(self) -> bool:
        with self._lock:
            if self._enabled:
                LOGGER.warning("rfid_manual_start_blocked automatic=%s", self._enabled)
                return False
            return self._inventory.start()

    def manual_stop(self) -> bool:
        with self._lock:
            if self._enabled:
                return self._finish("manual_stop")
            return self._inventory.stop()

    def disable(self) -> bool:
        with self._lock:
            was_enabled = self._enabled
            self._enabled = False
            self._previous = None
            self._armed = False
            stopped = self._finish("automatic_disabled")
            if was_enabled:
                LOGGER.info("automatic_inventory_disabled")
        if was_enabled:
            self._notify_mode(False)
        return stopped

    def _notify_mode(self, enabled: bool) -> None:
        try:
            self._mode_listener(enabled)
        except Exception:
            LOGGER.exception("automatic_mode_listener_failed enabled=%s", enabled)

    def close(self) -> None:
        """Impede que um comando concorrente habilite novos ciclos no encerramento."""

        with self._lock:
            self._closed = True
        self.disable()

    def _finish(self, reason: str) -> bool:
        self._generation += 1
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None
        self._armed = False
        if not self._active:
            return False
        self._active = False
        LOGGER.info("automatic_inventory_stop reason=%s", reason)
        stopped = self._inventory.stop()
        if not stopped:
            LOGGER.error("automatic_inventory_stop_failed reason=%s", reason)
        return stopped

    def _expire(self, generation: int) -> None:
        with self._lock:
            if generation == self._generation and self._enabled and self._active:
                LOGGER.warning("automatic_inventory_timeout seconds=%s", READ_TIMEOUT_SECONDS)
                self._finish("timeout_60_seconds")

    def update(self, inputs: tuple[bool, ...], set_relay: Callable[[int, bool], bool]) -> None:
        """Consome uma amostra e confirma relés sem tocar em CH4–CH8."""
        with self._lock:
            if self._closed:
                return
            if len(inputs) < 2:
                raise WaveshareConnectionError("Amostra sem DI1/DI2.")
            entry_clear, exit_clear = inputs[:2]
            previous = self._previous
            current = (entry_clear, exit_clear)
            self._previous = current
            if previous != current:
                LOGGER.info("automatic_beams di1_clear=%s di2_clear=%s", *current)
                if previous is not None:
                    for channel, (before, after) in enumerate(
                        zip(previous, current, strict=True), 1
                    ):
                        if before != after:
                            LOGGER.info(
                                "DI%s: %s -> %s",
                                channel,
                                "ATIVA" if before else "DESATIVADA",
                                "ATIVA" if after else "DESATIVADA",
                            )
            if self._active and self._inventory.status is not InventoryStatus.READING:
                self._finish("rfid_unavailable")
            if self._enabled and self._is_ready():
                if previous is None:
                    self._armed = all(current)
                else:
                    entry_interrupted = previous[0] and not entry_clear
                    exit_interrupted = previous[1] and not exit_clear
                    if self._active and exit_interrupted:
                        LOGGER.info("automatic_exit_sensor_interrupted")
                        self._finish("exit_sensor_interrupted")
                    elif entry_interrupted and exit_clear and self._armed and not self._active:
                        self._armed = False
                        LOGGER.info("automatic_entry_sensor_interrupted")
                        if self._inventory.start():
                            self._active = True
                            self._generation += 1
                            generation = self._generation
                            self._timer = self._timer_factory(
                                READ_TIMEOUT_SECONDS,
                                lambda: self._expire(generation),
                            )
                            self._timer.start()
                            LOGGER.info(
                                "automatic_inventory_started cycle=%s timeout_seconds=%s",
                                generation,
                                READ_TIMEOUT_SECONDS,
                            )
                        else:
                            LOGGER.error("automatic_inventory_start_failed")
                    elif not self._active and all(current):
                        self._armed = True
        # Não segurar o lock durante I/O serial: o timer deve parar o RFID
        # mesmo quando uma confirmação Modbus estiver bloqueada.
        self._sync_relays(set_relay)

    def _desired_relays(self) -> tuple[bool, bool, bool] | None:
        with self._lock:
            if self._statuses[ConnectionKind.WAVESHARE] is not ConnectionStatus.CONNECTED:
                return None
            if not self._is_ready():
                return False, False, True
            if self._active and self._inventory.status is InventoryStatus.READING:
                return False, True, False
            return True, False, False

    def _sync_relays(self, set_relay: Callable[[int, bool], bool]) -> None:
        desired = self._desired_relays()
        if desired is None:
            return
        self._write_relays(desired, set_relay)
        # Um Stop/timeout pode ter ocorrido durante a confirmação serial.
        latest = self._desired_relays()
        if latest is not None and latest != desired:
            self._write_relays(latest, set_relay)

    def _write_relays(
        self, desired: tuple[bool, bool, bool], set_relay: Callable[[int, bool], bool]
    ) -> None:
        # Desliga antes de ligar: nunca sobrepor os indicadores operacionais.
        for enabled in (False, True):
            for channel, state in enumerate(desired, 1):
                if state != enabled or self._relays.get(channel) == state:
                    continue
                if set_relay(channel, state) != state:
                    raise WaveshareConnectionError(f"CH{channel} não confirmou o comando.")
                self._relays[channel] = state
                LOGGER.info("automatic_relay_confirmed channel=%s enabled=%s", channel, state)
