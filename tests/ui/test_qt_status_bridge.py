import threading

import pytest

pytest.importorskip("PySide6")

from PySide6.QtCore import QCoreApplication
from PySide6.QtTest import QTest

from rfid_reader.domain import ConnectionKind, ConnectionStatus
from rfid_reader.services.connection_monitor import ConnectionMonitor
from rfid_reader.ui.qt.status_bridge import ConnectionBridge


def test_initial_states_are_unknown_not_simulated(qt_application: object) -> None:
    bridge = ConnectionBridge()
    connections = bridge.property("connections")
    assert [row["label"] for row in connections] == ["RFID", "Internet", "Comandos", "Sistema"]
    assert all(
        row["state"] == "unknown" and row["description"] == "Desconhecido" for row in connections
    )
    assert not bridge.property("simulated")
    assert bridge.property("foundCount") == 0
    assert bridge.property("tagModel").rowCount() == 0
    assert not bridge.property("startEnabled")
    assert not bridge.property("stopEnabled")
    bridge.requestStart()
    bridge.requestStop()
    assert not bridge.selectScenario("reading")
    assert bridge.property("operationState") == "unknown"
    connections[0]["state"] = "ok"
    assert bridge.property("connections")[0]["state"] == "unknown"


@pytest.mark.parametrize("status", list(ConnectionStatus))
def test_all_connection_states_project_existing_events(
    status: ConnectionStatus, qt_application: object
) -> None:
    bridge = ConnectionBridge()
    bridge.observe_snapshot({kind: status for kind in ConnectionKind})
    QCoreApplication.processEvents()
    expected = (
        "ok"
        if status is ConnectionStatus.CONNECTED
        else "checking"
        if status is ConnectionStatus.CHECKING
        else "error"
    )
    assert len(bridge.property("connections")) == 4
    assert all(
        row["state"] == expected and row["description"] == status.value
        for row in bridge.property("connections")
    )


def test_worker_callback_is_queued_and_closed_bridge_ignores_events(qt_application: object) -> None:
    bridge = ConnectionBridge()
    notifications: list[int] = []
    bridge.changed.connect(lambda: notifications.append(threading.get_ident()))
    thread = threading.Thread(
        target=lambda: bridge.receive_status(ConnectionKind.RFID, ConnectionStatus.CONNECTED)
    )
    thread.start()
    thread.join()
    assert notifications == []
    QCoreApplication.processEvents()
    assert notifications == [threading.get_ident()]
    bridge.receive_status(ConnectionKind.RFID, ConnectionStatus.CONNECTED)
    bridge.statusReceived.emit("RFID", "Conectado")
    bridge.statusReceived.emit(ConnectionKind.RFID, "invalid")
    QCoreApplication.processEvents()
    assert len(notifications) == 1
    bridge.close()
    bridge.receive_status(ConnectionKind.RFID, ConnectionStatus.ERROR)
    QCoreApplication.processEvents()
    assert len(notifications) == 1


def test_existing_monitor_callbacks_and_snapshot_need_no_new_poller(qt_application: object) -> None:
    class FakeChecker:
        def __init__(self) -> None:
            self.closed = False

        def check(self) -> ConnectionStatus:
            return ConnectionStatus.CONNECTED

        def close(self) -> None:
            self.closed = True

    checker = FakeChecker()
    bridge = ConnectionBridge()
    monitor = ConnectionMonitor({ConnectionKind.RFID: checker}, 0.05, bridge.receive_status)
    try:
        bridge.observe_snapshot(monitor.statuses())
        monitor.start()
        for _ in range(100):
            QTest.qWait(5)
            if bridge.property("connections")[0]["state"] == "ok":
                break
        assert bridge.property("connections")[0]["state"] == "ok"
        assert bridge.property("connections")[1]["state"] == "unknown"
    finally:
        monitor.stop()
        bridge.close()
    assert checker.closed


def test_theme_remains_selectable_without_operational_commands(qt_application: object) -> None:
    bridge = ConnectionBridge()
    assert bridge.selectTheme("navy")
    assert bridge.property("theme") == "navy"
    assert not bridge.selectTheme("invalid")
    assert not bridge.property("startEnabled")
