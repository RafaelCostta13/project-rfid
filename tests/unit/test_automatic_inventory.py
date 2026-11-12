import threading
from collections.abc import Callable

import pytest

from rfid_reader.domain import ConnectionKind, ConnectionStatus, InventoryStatus
from rfid_reader.integrations.waveshare_modbus import WaveshareConnectionError
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

    def resume(self) -> bool:
        return self.start()


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
        self.cycle_finished: list[str] = []
        self.previous_beams: tuple[bool, bool] | None = None
        self.controller = AutomaticInventoryController(
            self.inventory,
            self.timer,
            self.mode_events.append,
            self.cycle_finished.append,
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
        previous = self.previous_beams
        if previous is not None:
            if previous[0] and not entry and previous[1] == exit_ and exit_:
                self.controller.update((False, exit_, False, True, exit_), self.relay)
            elif previous[1] and not exit_ and previous[0] == entry:
                self.controller.update((entry, True, False, entry, False), self.relay)
        self.controller.update((entry, exit_, False, entry, exit_), self.relay)
        self.previous_beams = (entry, exit_)


class SequenceRig:
    """Altera cada entrada separadamente para preservar a ordem observada."""

    def __init__(self, clock: list[float]) -> None:
        self.rig = Rig()
        self.clock = clock
        self.inputs = [True, True, False, True, True]
        self.sample()
        self.sample()

    def sample(self) -> None:
        self.clock[0] += 0.1
        self.rig.controller.update(tuple(self.inputs), self.rig.relay)

    def set(self, channel: int, value: bool) -> None:
        self.inputs[channel - 1] = value
        self.sample()

    def enter(self) -> None:
        self.set(1, False)
        self.set(4, False)

    def exit(self) -> None:
        self.set(5, False)
        self.set(2, False)


def test_entry_requires_ordered_distinct_edges(monkeypatch: pytest.MonkeyPatch) -> None:
    clock = [0.0]
    monkeypatch.setattr("rfid_reader.services.automatic_inventory.time.monotonic", lambda: clock[0])
    seq = SequenceRig(clock)
    seq.set(4, False)
    seq.set(1, False)
    assert seq.rig.inventory.starts == 0 and not seq.rig.timers
    assert seq.rig.relays == {1: True, 2: False, 3: False}
    seq.set(4, True)
    seq.set(4, False)
    assert seq.rig.inventory.starts == 1 and seq.rig.timers[0].started
    assert seq.rig.relays == {1: False, 2: True, 3: False}
    seq.sample()
    assert seq.rig.inventory.starts == 1


@pytest.mark.parametrize("channel", [2, 5])
def test_exit_event_invalidates_incomplete_entry(
    channel: int, monkeypatch: pytest.MonkeyPatch
) -> None:
    clock = [0.0]
    monkeypatch.setattr("rfid_reader.services.automatic_inventory.time.monotonic", lambda: clock[0])
    seq = SequenceRig(clock)
    seq.set(1, False)
    seq.set(channel, False)
    seq.set(channel, True)
    seq.set(4, False)
    assert seq.rig.inventory.starts == 0 and not seq.rig.timers


def test_initially_interrupted_four_sensors_do_not_create_sequences() -> None:
    rig = Rig()
    rig.controller.update((False, False, False, False, False), rig.relay)
    rig.controller.update((False, False, False, False, False), rig.relay)
    assert rig.inventory.starts == rig.inventory.stops == 0
    assert not rig.timers
    rig.controller.update((True, True, False, True, True), rig.relay)
    rig.controller.update((False, True, False, True, True), rig.relay)
    rig.controller.update((False, True, False, False, True), rig.relay)
    assert rig.inventory.starts == 1


def test_incomplete_sample_is_reported_as_communication_failure() -> None:
    rig = Rig()
    with pytest.raises(WaveshareConnectionError, match="DI1 a DI5"):
        rig.controller.update((True, True, False, True), rig.relay)
    assert rig.inventory.starts == 0


def test_entry_and_exit_simultaneous_edges_do_not_imply_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clock = [0.0]
    monkeypatch.setattr("rfid_reader.services.automatic_inventory.time.monotonic", lambda: clock[0])
    seq = SequenceRig(clock)
    seq.inputs[0] = seq.inputs[3] = False
    seq.sample()
    assert seq.rig.inventory.starts == 0
    seq.inputs[0] = seq.inputs[3] = True
    seq.sample()
    seq.enter()
    seq.inputs[1] = seq.inputs[4] = False
    seq.sample()
    assert seq.rig.inventory.stops == 0
    seq.inputs[1] = seq.inputs[4] = True
    seq.sample()
    seq.exit()
    assert seq.rig.inventory.stops == 1
    assert seq.rig.cycle_finished == ["exit_sensor_interrupted"]


def test_repeated_di1_does_not_cancel_previously_armed_entry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clock = [0.0]
    monkeypatch.setattr("rfid_reader.services.automatic_inventory.time.monotonic", lambda: clock[0])
    seq = SequenceRig(clock)
    seq.set(1, False)
    assert seq.rig.inventory.starts == 0
    seq.set(1, True)
    seq.inputs[0] = seq.inputs[3] = False
    seq.sample()
    assert seq.rig.inventory.starts == 1
    assert len(seq.rig.timers) == 1 and seq.rig.timers[0].started
    seq.sample()
    assert seq.rig.inventory.starts == 1


def test_exit_requires_new_di2_edge_after_di5(monkeypatch: pytest.MonkeyPatch) -> None:
    clock = [0.0]
    monkeypatch.setattr("rfid_reader.services.automatic_inventory.time.monotonic", lambda: clock[0])
    seq = SequenceRig(clock)
    seq.enter()
    seq.set(2, False)
    seq.set(5, False)
    assert seq.rig.inventory.stops == 0
    assert seq.rig.relays == {1: False, 2: True, 3: False}
    seq.set(2, True)
    seq.set(2, False)
    assert seq.rig.inventory.stops == 1
    assert seq.rig.relays == {1: True, 2: False, 3: False}


@pytest.mark.parametrize("after_timeout", [False, True])
def test_repeated_di5_does_not_cancel_previously_armed_exit(
    monkeypatch: pytest.MonkeyPatch, after_timeout: bool
) -> None:
    clock = [0.0]
    monkeypatch.setattr("rfid_reader.services.automatic_inventory.time.monotonic", lambda: clock[0])
    seq = SequenceRig(clock)
    seq.enter()
    seq.set(5, False)
    seq.set(5, True)
    if after_timeout:
        seq.rig.timers[-1].callback()
    seq.inputs[1] = seq.inputs[4] = False
    seq.sample()
    assert seq.rig.inventory.stops == 1
    assert seq.rig.timers[0].cancelled
    assert seq.rig.cycle_finished == ["exit_sensor_interrupted"]
    assert seq.rig.relays == {1: True, 2: False, 3: False}
    seq.sample()
    assert seq.rig.cycle_finished == ["exit_sensor_interrupted"]


def test_armed_simultaneous_exit_has_priority_over_pedal(monkeypatch: pytest.MonkeyPatch) -> None:
    clock = [0.0]
    monkeypatch.setattr("rfid_reader.services.automatic_inventory.time.monotonic", lambda: clock[0])
    seq = SequenceRig(clock)
    seq.enter()
    seq.rig.timers[-1].callback()
    seq.set(5, False)
    seq.set(5, True)
    seq.set(3, True)
    seq.inputs[1] = seq.inputs[4] = False
    seq.sample()
    assert seq.rig.inventory.starts == 1
    assert seq.rig.cycle_finished == ["exit_sensor_interrupted"]


def test_timeout_reopen_invalidates_pending_exit_and_preserves_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clock = [0.0]
    monkeypatch.setattr("rfid_reader.services.automatic_inventory.time.monotonic", lambda: clock[0])
    seq = SequenceRig(clock)
    seq.enter()
    seq.set(5, False)
    seq.rig.timers[-1].callback()
    assert seq.rig.inventory.stops == 1 and seq.rig.cycle_finished == []
    seq.set(3, True)
    seq.sample()
    assert seq.rig.inventory.starts == 2 and len(seq.rig.timers) == 2
    seq.set(2, False)
    assert seq.rig.inventory.stops == 1
    seq.set(2, True)
    seq.set(5, True)
    seq.exit()
    assert seq.rig.inventory.stops == 2
    assert seq.rig.cycle_finished == ["exit_sensor_interrupted"]
    seq.set(3, False)
    seq.sample()
    seq.set(3, True)
    seq.sample()
    assert seq.rig.inventory.starts == 2


def test_timeout_valid_exit_and_stop_clear_pending_sequences(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clock = [0.0]
    monkeypatch.setattr("rfid_reader.services.automatic_inventory.time.monotonic", lambda: clock[0])
    seq = SequenceRig(clock)
    seq.enter()
    seq.rig.timers[-1].callback()
    seq.exit()
    assert seq.rig.inventory.stops == 1
    assert seq.rig.cycle_finished == ["exit_sensor_interrupted"]
    seq.set(3, True)
    seq.sample()
    assert seq.rig.inventory.starts == 1

    seq = SequenceRig(clock)
    seq.set(1, False)
    seq.rig.controller.disable()
    assert seq.rig.controller.enable()
    seq.sample()
    seq.set(4, False)
    assert seq.rig.inventory.starts == 0


def test_exit_started_before_timeout_finishes_after_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clock = [0.0]
    monkeypatch.setattr("rfid_reader.services.automatic_inventory.time.monotonic", lambda: clock[0])
    seq = SequenceRig(clock)
    seq.enter()
    seq.set(5, False)
    seq.rig.timers[-1].callback()
    seq.set(2, False)
    assert seq.rig.inventory.stops == 1
    assert seq.rig.cycle_finished == ["exit_sensor_interrupted"]
    seq.set(3, True)
    seq.sample()
    assert seq.rig.inventory.starts == 1


def test_completed_exit_wins_over_pedal_in_same_sample(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clock = [0.0]
    monkeypatch.setattr("rfid_reader.services.automatic_inventory.time.monotonic", lambda: clock[0])
    seq = SequenceRig(clock)
    seq.enter()
    seq.rig.timers[-1].callback()
    seq.set(5, False)
    seq.set(3, True)
    seq.set(2, False)
    assert seq.rig.inventory.starts == 1
    assert seq.rig.cycle_finished == ["exit_sensor_interrupted"]


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
    assert rig.cycle_finished == []
    rig.update(False, False)
    assert rig.relays[1]


def test_pedal_reopens_only_after_timeout_and_exit_has_priority(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clock = [0.0]
    monkeypatch.setattr("rfid_reader.services.automatic_inventory.time.monotonic", lambda: clock[0])
    rig = Rig()

    def sample(entry: bool, exit_: bool, pedal: bool, di4: bool, di5: bool) -> None:
        clock[0] += 0.1
        rig.controller.update((entry, exit_, pedal, di4, di5), rig.relay)

    sample(True, True, False, True, True)
    sample(True, True, False, True, True)
    sample(False, True, False, True, True)
    sample(False, True, False, False, True)
    rig.timers[-1].callback()
    sample(False, True, True, False, True)
    sample(False, True, True, False, True)
    assert rig.inventory.starts == 2
    assert rig.relays == {1: False, 2: True, 3: False}
    rig.timers[-1].callback()
    sample(False, True, True, False, True)
    assert rig.inventory.starts == 2
    sample(False, True, False, False, True)
    sample(False, True, False, False, True)
    sample(False, True, False, False, False)
    sample(False, False, True, False, False)
    sample(False, False, True, False, False)
    assert rig.inventory.starts == 2
    assert rig.cycle_finished == ["exit_sensor_interrupted"]
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
    assert rig.cycle_finished == ["automatic_disabled"]


def test_exit_sensor_announces_completion_but_operational_failure_does_not() -> None:
    rig = Rig()
    rig.update(True, True)
    rig.update(False, True)
    rig.update(False, False)
    assert rig.cycle_finished == ["exit_sensor_interrupted"]

    rig = Rig()
    rig.update(True, True)
    rig.update(False, True)
    rig.controller.update_connection_status(ConnectionKind.RFID, ConnectionStatus.ERROR)
    assert rig.cycle_finished == []


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

    rig.controller.update((False, True, False, True, True), rig.relay)
    thread = threading.Thread(
        target=lambda: rig.controller.update((False, True, False, False, True), relay)
    )
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
    controller.update((True, True, False, True, True), relay)

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
