import threading
from datetime import UTC, datetime

from rfid_reader.domain import (
    InventoryCleared,
    InventoryEvent,
    InventoryStatus,
    InventoryStatusChanged,
    TagRead,
    TagReceived,
)
from rfid_reader.readers.base import DisconnectCallback, TagCallback
from rfid_reader.services.manual_inventory import ManualInventoryService


class FakeReader:
    def __init__(self, connected: bool = True) -> None:
        self.connected = connected
        self.inventorying = False
        self.tag_callback: TagCallback | None = None
        self.disconnect_callback: DisconnectCallback = lambda: None
        self.start_calls = 0
        self.stop_calls = 0
        self.disconnect_calls = 0
        self.operations: list[str] = []

    def connect(self) -> None:
        self.connected = True

    def disconnect(self) -> None:
        self.operations.append("disconnect")
        self.disconnect_calls += 1
        self.connected = False

    def is_connected(self) -> bool:
        return self.connected

    def start_inventory(self, callback: TagCallback) -> bool:
        if self.inventorying:
            return False
        self.operations.append("start")
        self.start_calls += 1
        self.inventorying = True
        self.tag_callback = callback
        return True

    def stop_inventory(self) -> bool:
        if not self.inventorying:
            return False
        self.operations.append("stop")
        self.stop_calls += 1
        self.inventorying = False
        return True

    def is_inventorying(self) -> bool:
        return self.inventorying

    def set_disconnect_callback(self, callback: DisconnectCallback) -> None:
        self.disconnect_callback = callback

    def emit(self, epc: str) -> None:
        assert self.tag_callback is not None
        self.tag_callback(
            TagRead(
                epc=epc,
                reader_id="fake",
                antenna_id=1,
                read_at=datetime.now(UTC),
            )
        )

    def lose_connection(self) -> None:
        self.connected = False
        self.inventorying = False
        self.disconnect_callback()


def test_starts_reader_clears_list_and_delivers_simulated_epc() -> None:
    reader = FakeReader()
    events: list[InventoryEvent] = []
    service = ManualInventoryService(reader, events.append)

    assert service.start()
    reader.emit("E28011700001")

    assert reader.start_calls == 1
    assert events[0] == InventoryCleared()
    assert events[1] == InventoryStatusChanged(InventoryStatus.READING)
    assert events[2] == TagReceived(events[2].tag)
    assert events[2].tag.epc == "E28011700001"


def test_does_not_start_two_inventories() -> None:
    reader = FakeReader()
    service = ManualInventoryService(reader, lambda event: None)

    assert service.start()
    assert not service.start()
    assert reader.start_calls == 1


def test_disconnected_reader_reports_error_without_starting() -> None:
    reader = FakeReader(connected=False)
    events: list[InventoryEvent] = []
    service = ManualInventoryService(reader, events.append)

    assert not service.start()

    assert reader.start_calls == 0
    assert events == [InventoryStatusChanged(InventoryStatus.ERROR)]


def test_stop_blocks_late_tags() -> None:
    reader = FakeReader()
    events: list[InventoryEvent] = []
    service = ManualInventoryService(reader, events.append)
    service.start()
    callback = reader.tag_callback

    assert service.stop()
    assert callback is not None
    callback(
        TagRead(
            epc="LATE",
            reader_id="fake",
            antenna_id=1,
            read_at=datetime.now(UTC),
        )
    )

    assert reader.stop_calls == 1
    assert not any(isinstance(event, TagReceived) and event.tag.epc == "LATE" for event in events)
    assert events[-1] == InventoryStatusChanged(InventoryStatus.STOPPED)


def test_stop_waits_for_accepted_tag_and_rejects_old_callback_after_restart() -> None:
    reader = FakeReader()
    entered, release, stopped = threading.Event(), threading.Event(), threading.Event()
    events: list[InventoryEvent] = []

    def listener(event: InventoryEvent) -> None:
        if isinstance(event, TagReceived):
            entered.set()
            assert release.wait(3)
        events.append(event)

    service = ManualInventoryService(reader, listener)
    assert service.start()
    old_callback = reader.tag_callback
    worker = threading.Thread(target=lambda: reader.emit("E28011700001"))
    worker.start()
    assert entered.wait(1)
    stopper = threading.Thread(target=lambda: (service.stop(), stopped.set()))
    stopper.start()
    try:
        assert not stopped.wait(0.05)
    finally:
        release.set()
        worker.join(2)
        stopper.join(2)
    assert stopped.is_set()
    assert service.start()
    assert old_callback is not None
    old_callback(TagRead("E28011700002", "fake", 1, datetime.now(UTC)))
    assert [event.tag.epc for event in events if isinstance(event, TagReceived)] == ["E28011700001"]


def test_connection_loss_interrupts_reading_with_error() -> None:
    reader = FakeReader()
    events: list[InventoryEvent] = []
    service = ManualInventoryService(reader, events.append)
    service.start()

    reader.lose_connection()

    assert service.status is InventoryStatus.ERROR
    assert events[-1] == InventoryStatusChanged(InventoryStatus.ERROR)


def test_new_reading_clears_previous_list_again() -> None:
    reader = FakeReader()
    events: list[InventoryEvent] = []
    service = ManualInventoryService(reader, events.append)

    service.start()
    service.stop()
    service.start()

    assert sum(isinstance(event, InventoryCleared) for event in events) == 2


def test_close_stops_inventory_before_disconnect() -> None:
    reader = FakeReader()
    service = ManualInventoryService(reader, lambda event: None)
    service.start()

    service.close()

    assert reader.operations == ["start", "stop", "disconnect"]


def test_unconfirmed_stop_reports_error_and_disconnects() -> None:
    reader = FakeReader()
    service = ManualInventoryService(reader, lambda event: None)
    service.start()
    reader.inventorying = False

    assert not service.stop()
    assert service.status is InventoryStatus.ERROR
    assert reader.disconnect_calls == 1
