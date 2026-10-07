import threading
from collections.abc import Callable

import pytest

from rfid_reader.domain import ConnectionKind, ConnectionStatus, InventoryStatus
from rfid_reader.services.automatic_inventory import AutomaticInventoryController


class Inventory:
    def __init__(self) -> None:
        self.status = InventoryStatus.STOPPED
        self.starts = 0
        self.stops = 0
        self.fail_start = False
        self.fail_stop = False

    def start(self) -> bool:
        self.starts += 1
        self.status = InventoryStatus.ERROR if self.fail_start else InventoryStatus.READING
        return not self.fail_start

    def stop(self) -> bool:
        self.stops += 1
        self.status = InventoryStatus.ERROR if self.fail_stop else InventoryStatus.STOPPED
        return not self.fail_stop


class Timer:
    def __init__(self, seconds: float, callback: Callable[[], None]) -> None:
        assert seconds == 60
        self.callback = callback
        self.started = False
        self.cancelled = False

    def start(self) -> None:
        self.started = True

    def cancel(self) -> None:
        self.cancelled = True


class Rig:
    def __init__(self) -> None:
        self.inventory = Inventory()
        self.timers: list[Timer] = []
        self.relays = {channel: False for channel in range(1, 4)}
        self.calls: list[tuple[int, bool]] = []
        self.mode_events: list[bool] = []
        self.controller = AutomaticInventoryController(
            self.inventory, self.timer, self.mode_events.append
        )
        self.set_all_statuses(ConnectionStatus.CONNECTED)
        assert self.controller.enable()

    def set_all_statuses(self, status: ConnectionStatus) -> None:
        for kind in ConnectionKind:
            self.controller.update_connection_status(kind, status)

    def timer(self, seconds: float, callback: Callable[[], None]) -> Timer:
        timer = Timer(seconds, callback)
        self.timers.append(timer)
        return timer

    def relay(self, channel: int, state: bool) -> bool:
        assert channel in (1, 2, 3)
        self.calls.append((channel, state))
        self.relays[channel] = state
        assert sum(self.relays.values()) <= 1
        return state

    def update(self, entry: bool, exit_: bool) -> None:
        self.controller.update((entry, exit_, False, True, False), self.relay)


def test_full_cycle_repeated_samples_and_old_timer() -> None:
    rig = Rig()
    rig.update(True, True)
    assert rig.relays == {1: True, 2: False, 3: False}
    assert rig.inventory.starts == 0
    rig.update(False, True)
    for _ in range(5):
        rig.update(False, True)
    assert rig.inventory.starts == 1
    assert len(rig.timers) == 1 and rig.timers[0].started
    assert rig.relays == {1: False, 2: True, 3: False}
    rig.update(False, False)
    assert rig.inventory.stops == 1
    assert rig.timers[0].cancelled
    assert rig.relays == {1: True, 2: False, 3: False}
    rig.update(False, True)
    assert rig.inventory.starts == 1
    rig.update(True, True)
    rig.update(False, True)
    rig.timers[0].callback()
    assert rig.inventory.starts == 2
    assert rig.inventory.stops == 1
    assert rig.inventory.status is InventoryStatus.READING


@pytest.mark.parametrize("initial", [(False, True), (False, False), (True, False)])
def test_initial_sample_is_not_an_edge(initial: tuple[bool, bool]) -> None:
    rig = Rig()
    rig.update(*initial)
    rig.update(False, True)
    assert rig.inventory.starts == 0
    rig.update(True, True)
    rig.update(False, True)
    assert rig.inventory.starts == 1


def test_timeout_stops_and_requires_clear_beams() -> None:
    rig = Rig()
    rig.update(True, True)
    rig.update(False, True)
    rig.timers[0].callback()
    rig.update(False, True)
    assert rig.inventory.stops == 1
    assert rig.relays == {1: True, 2: False, 3: False}
    assert rig.timers[0].cancelled
    rig.update(False, False)
    assert rig.relays[1]
    rig.update(True, True)
    assert rig.relays[1]


@pytest.mark.parametrize("failure", ["start", "stop", "disconnect"])
def test_zebra_failures_never_leave_yellow_indicator_on(failure: str) -> None:
    rig = Rig()
    rig.inventory.fail_start = failure == "start"
    rig.inventory.fail_stop = failure == "stop"
    rig.update(True, True)
    rig.update(False, True)
    if failure == "disconnect":
        rig.inventory.status = InventoryStatus.ERROR
    rig.update(False, False)
    assert not rig.relays[2]


def test_manual_controls_and_waveshare_shutdown_cancel_cycle() -> None:
    rig = Rig()
    assert not rig.controller.manual_start()
    rig.update(True, True)
    rig.update(False, True)
    assert rig.controller.disable()
    assert rig.timers[0].cancelled
    rig.update(False, True)
    assert not rig.relays[2]
    rig.update(True, True)
    rig.update(False, True)
    assert rig.inventory.stops == 1
    assert rig.mode_events == [True, False]


def test_exit_without_cycle_and_simultaneous_beams_do_not_start() -> None:
    rig = Rig()
    rig.update(True, True)
    rig.update(True, False)
    rig.update(False, False)
    assert rig.inventory.starts == rig.inventory.stops == 0
    assert rig.relays[1]


def test_timer_stops_rfid_while_relay_confirmation_is_blocked() -> None:
    rig = Rig()
    rig.update(True, True)
    waiting = threading.Event()
    release = threading.Event()

    def relay(channel: int, state: bool) -> bool:
        if channel == 2 and state:
            waiting.set()
            assert release.wait(2)
        return rig.relay(channel, state)

    thread = threading.Thread(target=lambda: rig.controller.update((False, True), relay))
    thread.start()
    try:
        assert waiting.wait(2)
        rig.timers[0].callback()
        assert rig.inventory.stops == 1
    finally:
        release.set()
        thread.join(2)
    assert not thread.is_alive()
    assert not rig.relays[2]


@pytest.mark.parametrize(
    "kind", [ConnectionKind.INTERNET, ConnectionKind.RFID, ConnectionKind.SYSTEM]
)
def test_unavailable_dependency_stops_cycle_and_selects_red(kind: ConnectionKind) -> None:
    rig = Rig()
    rig.update(True, True)
    rig.update(False, True)

    rig.controller.update_connection_status(kind, ConnectionStatus.DISCONNECTED)
    rig.update(False, True)

    assert rig.inventory.stops == 1
    assert rig.timers[0].cancelled
    assert rig.relays == {1: False, 2: False, 3: True}
    rig.controller.update_connection_status(kind, ConnectionStatus.CONNECTED)
    rig.update(False, True)
    assert rig.relays == {1: True, 2: False, 3: False}
    assert rig.inventory.starts == 1


def test_waveshare_loss_disables_mode_without_claiming_relay_state() -> None:
    rig = Rig()
    rig.update(True, True)
    calls_before_loss = list(rig.calls)

    rig.controller.update_connection_status(ConnectionKind.WAVESHARE, ConnectionStatus.DISCONNECTED)
    rig.update(True, True)

    assert not rig.controller.enabled
    assert rig.calls == calls_before_loss
    assert rig.mode_events == [True, False]


def test_enable_requires_all_dependencies_and_does_not_start_rfid() -> None:
    inventory = Inventory()
    controller = AutomaticInventoryController(inventory)
    for kind in ConnectionKind:
        controller.update_connection_status(kind, ConnectionStatus.CONNECTED)
    controller.update_connection_status(ConnectionKind.INTERNET, ConnectionStatus.ERROR)

    assert not controller.enable()
    assert inventory.starts == 0

    controller.update_connection_status(ConnectionKind.INTERNET, ConnectionStatus.CONNECTED)
    assert controller.enable()
    assert inventory.starts == 0


def test_ready_indicator_is_independent_from_automatic_mode() -> None:
    inventory = Inventory()
    controller = AutomaticInventoryController(inventory)
    relays = {channel: False for channel in range(1, 4)}

    def relay(channel: int, state: bool) -> bool:
        relays[channel] = state
        assert sum(relays.values()) <= 1
        return state

    for kind in ConnectionKind:
        controller.update_connection_status(kind, ConnectionStatus.CONNECTED)
    controller.update((True, True), relay)

    assert relays == {1: True, 2: False, 3: False}
    assert inventory.starts == 0


@pytest.mark.parametrize("status", [ConnectionStatus.ERROR, ConnectionStatus.CHECKING])
def test_system_not_ready_blocks_enable_and_sensor_cycles(status: ConnectionStatus) -> None:
    rig = Rig()
    rig.controller.disable()
    rig.controller.update_connection_status(ConnectionKind.SYSTEM, status)

    assert not rig.controller.ready
    assert not rig.controller.enable()
    rig.update(True, True)
    rig.update(False, True)

    assert rig.inventory.starts == 0
    assert rig.relays == {1: False, 2: False, 3: True}
    rig.controller.update_connection_status(ConnectionKind.SYSTEM, ConnectionStatus.CONNECTED)
    rig.update(True, True)
    assert rig.controller.ready
    assert rig.relays == {1: True, 2: False, 3: False}


def test_sync_status_does_not_block_ready_or_stop_active_cycle() -> None:
    rig = Rig()
    rig.update(True, True)
    rig.update(False, True)

    rig.controller.update_connection_status(ConnectionKind.SYNC, ConnectionStatus.ERROR)
    rig.update(False, True)

    assert rig.controller.ready
    assert rig.inventory.status is InventoryStatus.READING
    assert rig.inventory.stops == 0
    assert rig.relays == {1: False, 2: True, 3: False}
