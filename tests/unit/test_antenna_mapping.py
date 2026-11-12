from datetime import UTC, datetime

from rfid_reader.domain import TagRead
from rfid_reader.services.antenna_mapping import AntennaMappingService


class Reader:
    def __init__(self) -> None:
        self.connected = True
        self.reading = False

    def is_connected(self) -> bool:
        return self.connected

    def is_inventorying(self) -> bool:
        return self.reading

    def start_inventory(self, callback: object) -> bool:
        self.reading = True
        self.callback = callback
        return True

    def stop_inventory(self) -> bool:
        self.reading = False
        return True

    def disconnect(self) -> None:
        self.connected = False


def test_aggregation_angle_antenna_clear_and_stop() -> None:
    reader = Reader()
    events = []
    service = AntennaMappingService(reader, events.append)  # type: ignore[arg-type]
    assert service.start()
    service.set_angle(30)

    def sample(antenna: int | None, rssi: int | None) -> None:
        service._on_tag(TagRead("ABC", "reader", antenna, datetime.now(UTC), rssi))

    sample(2, -70)
    sample(2, -80)
    sample(2, -60)
    sample(1, -55)
    sample(1, None)
    sample(None, -50)
    assert "RSSI" in service.snapshot().message
    points = service.snapshot().points
    assert [(p.antenna, p.angle, p.rssi) for p in points] == [(2, 30, -60), (1, 30, -55)]
    service.set_angle(-30)
    sample(2, -75)
    assert len(service.snapshot().points) == 3
    service.clear()
    assert service.snapshot().points == ()
    assert service.stop()
    sample(2, -30)
    assert not service.snapshot().points and not reader.reading
    assert events


def test_connection_loss_stops_capture_and_keeps_existing_points() -> None:
    reader = Reader()
    service = AntennaMappingService(reader, lambda event: None)  # type: ignore[arg-type]
    assert service.start()
    service._on_tag(TagRead("ABC", "reader", 1, datetime.now(UTC), -60))
    reader.connected = False
    service.connection_lost()
    service._on_tag(TagRead("DEF", "reader", 1, datetime.now(UTC), -40))
    snapshot = service.snapshot()
    assert not snapshot.active
    assert len(snapshot.points) == 1
    assert "perdida" in snapshot.message


def test_failed_stop_keeps_capture_reserved_if_reader_stays_connected() -> None:
    class FailingReader(Reader):
        def stop_inventory(self) -> bool:
            return False

        def disconnect(self) -> None:
            pass

    reader = FailingReader()
    service = AntennaMappingService(reader, lambda event: None)  # type: ignore[arg-type]
    assert service.start()
    assert not service.stop()
    assert service.snapshot().active
    assert reader.connected
