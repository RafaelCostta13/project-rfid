"""Orquestração do inventário pelas sequências de sensores do portal."""

from __future__ import annotations

import logging
import threading
import time
from collections.abc import Callable
from typing import Protocol

from rfid_reader.domain import ConnectionKind, ConnectionStatus, InventoryStatus
from rfid_reader.integrations.waveshare_modbus import WaveshareConnectionError

LOGGER = logging.getLogger(__name__)
READ_TIMEOUT_SECONDS = 60.0
PEDAL_ACTIVE_LEVEL = True
PEDAL_DEBOUNCE_SECONDS = 0.05
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

    def resume(self) -> bool: ...

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
        cycle_finished_listener: Callable[[str], None] = lambda reason: None,
    ) -> None:
        self._inventory = inventory
        self._timer_factory = timer_factory
        self._mode_listener = mode_listener
        self._cycle_finished_listener = cycle_finished_listener
        self._lock = threading.RLock()
        self._statuses = {kind: ConnectionStatus.CHECKING for kind in ConnectionKind}
        self._backend_observed = False
        self._enabled = False
        self._closed = False
        self._previous: tuple[bool, bool, bool, bool] | None = None
        self._armed = False
        self._entry_pending = False
        self._exit_pending = False
        self._active = False
        self._awaiting_completion = False
        self._pedal_candidate: bool | None = None
        self._pedal_stable: bool | None = None
        self._pedal_changed_at = 0.0
        self._pedal_released_after_timeout = False
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
                self._awaiting_completion = False
                self._previous = None
                self._armed = False
                self._entry_pending = False
                self._exit_pending = False
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
            self._entry_pending = False
            self._exit_pending = False
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
                self._awaiting_completion = False
                self._entry_pending = False
                self._exit_pending = False
                return self._finish("manual_stop")
            return self._inventory.stop()

    def disable(self) -> bool:
        with self._lock:
            was_enabled = self._enabled
            self._enabled = False
            awaiting = self._awaiting_completion
            self._awaiting_completion = False
            self._previous = None
            self._armed = False
            self._entry_pending = False
            self._exit_pending = False
            stopped = self._finish("automatic_disabled")
            if awaiting and not self._closed:
                self._cycle_finished_listener("automatic_disabled")
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
        self._entry_pending = False
        if reason != "timeout_60_seconds":
            self._exit_pending = False
        if not self._active:
            return False
        self._active = False
        LOGGER.info("automatic_inventory_stop reason=%s", reason)
        stopped = self._inventory.stop()
        if not stopped:
            self._exit_pending = False
            LOGGER.error("automatic_inventory_stop_failed reason=%s", reason)
        elif not self._closed and reason in {
            "automatic_disabled",
            "exit_sensor_interrupted",
        }:
            self._cycle_finished_listener(reason)
        return stopped

    def _expire(self, generation: int) -> None:
        with self._lock:
            if generation == self._generation and self._enabled and self._active:
                LOGGER.warning("automatic_inventory_timeout seconds=%s", READ_TIMEOUT_SECONDS)
                self._awaiting_completion = self._finish("timeout_60_seconds")
                self._pedal_released_after_timeout = (
                    self._pedal_stable is False and self._pedal_candidate is False
                )

    def _start_cycle(self, *, resume: bool) -> None:
        self._exit_pending = False
        started = self._inventory.resume() if resume else self._inventory.start()
        if not started:
            LOGGER.error("automatic_inventory_start_failed")
            return
        self._awaiting_completion = False
        self._active = True
        self._generation += 1
        generation = self._generation
        self._timer = self._timer_factory(READ_TIMEOUT_SECONDS, lambda: self._expire(generation))
        self._timer.start()

    def _pedal_pressed(self, inputs: tuple[bool, ...]) -> bool:
        if len(inputs) < 3:
            return False
        active = inputs[2] == PEDAL_ACTIVE_LEVEL
        now = time.monotonic()
        if active != self._pedal_candidate:
            self._pedal_candidate = active
            self._pedal_changed_at = now
            return False
        if now - self._pedal_changed_at < PEDAL_DEBOUNCE_SECONDS:
            return False
        previous = self._pedal_stable
        self._pedal_stable = active
        if self._awaiting_completion and not active:
            self._pedal_released_after_timeout = True
        return previous is False and active and self._pedal_released_after_timeout

    def update(self, inputs: tuple[bool, ...], set_relay: Callable[[int, bool], bool]) -> None:
        """Consome uma amostra e confirma relés sem tocar em CH4–CH8."""
        with self._lock:
            if self._closed:
                return
            if len(inputs) < 5:
                raise WaveshareConnectionError("Amostra incompleta: são necessárias DI1 a DI5.")
            entry_clear, exit_clear, entry_second_clear, exit_first_clear = (
                inputs[0],
                inputs[1],
                inputs[3],
                inputs[4],
            )
            pedal_pressed = self._pedal_pressed(inputs)
            previous = self._previous
            current = (entry_clear, exit_clear, entry_second_clear, exit_first_clear)
            self._previous = current
            if previous != current:
                LOGGER.info(
                    "automatic_beams di1_clear=%s di2_clear=%s di4_clear=%s di5_clear=%s",
                    *current,
                )
                if previous is not None:
                    for channel, (before, after) in zip(
                        (1, 2, 4, 5), zip(previous, current, strict=True), strict=True
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
                    di1 = previous[0] and not entry_clear
                    di2 = previous[1] and not exit_clear
                    di4 = previous[2] and not entry_second_clear
                    di5 = previous[3] and not exit_first_clear
                    passage = self._active or self._awaiting_completion
                    if passage and di2 and self._exit_pending:
                        self._exit_pending = False
                        LOGGER.info("automatic_exit_sequence_complete")
                        if self._awaiting_completion:
                            self._awaiting_completion = False
                            self._cycle_finished_listener("exit_sensor_interrupted")
                        else:
                            self._finish("exit_sensor_interrupted")
                    elif self._awaiting_completion and pedal_pressed and exit_clear:
                        self._start_cycle(resume=True)
                    elif passage and di5 and di2:
                        self._exit_pending = False
                        LOGGER.info("automatic_exit_order_unknown")
                    elif passage and di5:
                        self._exit_pending = True
                        LOGGER.info("automatic_exit_first_sensor_interrupted")
                    elif not passage and (di2 or di5):
                        self._entry_pending = False
                        self._armed = False
                    elif not passage and di1 and di4 and not self._entry_pending:
                        self._entry_pending = False
                        LOGGER.info("automatic_entry_order_unknown")
                    elif not passage and di1 and exit_clear and self._armed:
                        self._entry_pending = True
                        self._armed = False
                        LOGGER.info("automatic_entry_first_sensor_interrupted")
                    elif not passage and di4 and exit_clear and self._entry_pending:
                        self._entry_pending = False
                        LOGGER.info("automatic_entry_sequence_complete")
                        self._start_cycle(resume=False)
                    elif not passage and all(current) and not self._entry_pending:
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
