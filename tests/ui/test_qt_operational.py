import threading
import time
from collections.abc import Callable, Iterator
from pathlib import Path

import pytest

pytest.importorskip("PySide6")

from fakes_operational import EPC, Backend, Internet, Port, Reader, Timer
from fakes_operational import Tester as SerialTester
from PySide6.QtCore import QCoreApplication, QEvent, QObject, QThread, qInstallMessageHandler
from PySide6.QtQuick import QQuickItem
from PySide6.QtTest import QTest

from rfid_reader.config import load_config
from rfid_reader.domain import ConnectionKind, ConnectionStatus, InventoryStatus
from rfid_reader.integrations.backend_client import BackendRFIDClient
from rfid_reader.runtime import (
    ApplicationRuntime,
    CommandFinished,
    RuntimeDependencies,
    RuntimeEvent,
)
from rfid_reader.ui.qt.application import create_engine
from rfid_reader.ui.qt.configuration import ConfigurationBridge
from rfid_reader.ui.qt.mock_data import PrototypeTheme
from rfid_reader.ui.qt.operational import OperationalBridge
from rfid_reader.ui.qt.status_bridge import CONNECTION_LABELS, STATE_COLORS


def wait_for(predicate: Callable[[], bool]) -> None:
    for _ in range(600):
        QTest.qWait(5)
        if predicate():
            return
    raise AssertionError("O fluxo simulado não atingiu o estado esperado")


def visual_child(window: object, name: str) -> QObject:
    pending = list(window.contentItem().childItems())
    while pending:
        item = pending.pop()
        if item.objectName() == name:
            return item
        pending.extend(item.childItems())
    raise AssertionError(f"Controle QML ausente: {name}")


def connection_indicators(window: object) -> tuple[QQuickItem, list[QQuickItem]]:
    bar = window.findChild(QQuickItem, "connectionIndicators")
    assert bar is not None
    items = [item for item in bar.childItems() if item.property("label") is not None]
    return bar, sorted(items, key=lambda item: item.x())


class Rig:
    def __init__(self, path: Path) -> None:
        self.reader, self.port, self.backend = Reader(), Port(), Backend()
        self.timers: list[Timer] = []
        self.settings = load_config(
            {
                "WAVESHARE_SERIAL_PORT": "COM-SIMULADA",
                "RFID_BACKEND_BASE_URL": "https://backend.test",
                "RFID_STATUS_CHECK_INTERVAL_SECONDS": "0.01",
            }
        )
        self.runtime = ApplicationRuntime(
            self.settings,
            path,
            RuntimeDependencies(
                reader=self.reader,
                backend_factory=lambda url, timeout: BackendRFIDClient(
                    url, timeout, transport=self.backend.transport
                ),
                port_factory=lambda settings: self.port,
                tester_factory=lambda gate: SerialTester(gate, self.port),
                timer_factory=self.timer,
                checkers={ConnectionKind.INTERNET: Internet()},
            ),
        )
        self.bridge = OperationalBridge(self.runtime, PrototypeTheme.CORPORATE)
        self.configuration = ConfigurationBridge(self.settings, path, self.runtime)
        self.runtime.start()
        wait_for(lambda: self.bridge.startEnabled)

    def timer(self, seconds: float, callback: Callable[[], None]) -> Timer:
        timer = Timer(seconds, callback)
        self.timers.append(timer)
        return timer

    def start_cycle(self) -> None:
        timer_count = len(self.timers)
        if not self.runtime.automatic.enabled:
            self.bridge.requestStart()
            wait_for(lambda: self.bridge.automaticEnabled)
        self.port.inputs = (True, True, False, True, False)
        samples = self.port.samples
        wait_for(lambda: self.port.samples >= samples + 2)
        self.port.inputs = (False, True, False, True, False)
        wait_for(lambda: self.reader.reading)
        wait_for(lambda: self.bridge.operationState == "reading")
        wait_for(lambda: len(self.timers) == timer_count + 1 and self.timers[-1].started)

    def end_cycle(self) -> None:
        self.port.inputs = (False, False, False, True, False)
        wait_for(lambda: not self.reader.reading)
        wait_for(lambda: self.bridge.operationState == "ok")

    def close(self) -> None:
        self.backend.release.set()
        self.bridge.close()
        self.configuration.close()
        self.runtime.close()
        QCoreApplication.processEvents()


@pytest.fixture
def rig(qt_application: object, tmp_path: Path) -> Iterator[Rig]:
    simulation = Rig(tmp_path / ".env")
    try:
        yield simulation
    finally:
        simulation.close()


def test_full_cycle_updates_qml_table_counter_and_preserves_relays(rig: Rig) -> None:
    assert rig.reader.starts == 0
    rig.bridge.requestStart()
    wait_for(lambda: rig.bridge.automaticEnabled)
    assert rig.reader.starts == 0
    rig.start_cycle()
    wait_for(lambda: rig.port.relays[:3] == [False, True, False])
    assert rig.timers[0].started
    thread_ids: list[QThread] = []
    rig.bridge.tagModel.rowsInserted.connect(
        lambda *args: thread_ids.append(QThread.currentThread())
    )
    rig.reader.emit()
    wait_for(lambda: rig.bridge.foundCount == 1)
    model = rig.bridge.tagModel
    assert [model.data(model.index(0, column)) for column in range(6)] == [
        "lido",
        "Cliente real do contrato",
        "00123",
        "2/4",
        "00042",
        "DOCA 35",
    ]
    assert thread_ids == [QCoreApplication.instance().thread()]
    rig.end_cycle()
    assert rig.timers[0].cancelled
    wait_for(lambda: rig.port.relays[:3] == [True, False, False])
    assert rig.reader.connections == 1 and rig.port.opens == 1
    assert rig.backend.count("GET") == rig.backend.count("POST") == 1
    assert all(channel <= 3 for channel, enabled in rig.port.writes)


@pytest.mark.parametrize("status", [404, 500, "timeout"])
def test_get_failure_or_missing_epc_never_posts_or_counts(rig: Rig, status: int | str) -> None:
    rig.backend.get_status = status
    rig.start_cycle()
    rig.reader.emit()
    wait_for(lambda: rig.backend.count("GET") == 1)
    QTest.qWait(50)
    assert rig.backend.count("POST") == rig.bridge.foundCount == 0
    rig.reader.emit()
    QTest.qWait(20)
    assert rig.backend.count("GET") == 1
    if status != 404:
        wait_for(lambda: "consultar" in rig.bridge.operationDescription)
    else:
        assert "consultar" not in rig.bridge.operationDescription


@pytest.mark.parametrize("status", [500, "timeout"])
def test_ambiguous_or_failed_post_is_not_retried(rig: Rig, status: int | str) -> None:
    rig.backend.post_status = status
    rig.start_cycle()
    rig.reader.emit()
    wait_for(lambda: "consultar" in rig.bridge.operationDescription)
    for _ in range(5):
        rig.reader.emit()
    QTest.qWait(40)
    assert rig.backend.count("GET") == rig.backend.count("POST") == 1
    assert rig.bridge.foundCount == 0


def test_duplicates_new_session_and_visual_updates_never_post(rig: Rig) -> None:
    rig.start_cycle()
    for _ in range(10):
        rig.reader.emit(" " + EPC.lower() + " ")
    wait_for(lambda: rig.bridge.foundCount == 1)
    for _ in range(5):
        rig.bridge.changed.emit()
        QCoreApplication.processEvents()
    assert rig.backend.count("POST") == 1
    rig.end_cycle()
    rig.start_cycle()
    assert rig.bridge.foundCount == 0
    rig.reader.emit()
    wait_for(lambda: rig.bridge.foundCount == 1)
    assert rig.backend.count("POST") == 2
    rig.timers[0].callback()
    assert rig.reader.reading


def test_old_post_response_does_not_update_new_session(rig: Rig) -> None:
    rig.backend.block = "POST"
    rig.start_cycle()
    rig.reader.emit()
    wait_for(rig.backend.entered.is_set)
    rig.end_cycle()
    rig.start_cycle()
    rig.backend.release.set()
    QTest.qWait(50)
    assert rig.bridge.foundCount == 0
    assert rig.backend.count("POST") == 1
    rig.reader.emit()
    wait_for(lambda: rig.bridge.foundCount == 1)
    assert rig.backend.count("POST") == 2


def test_post_finishing_after_stop_updates_only_current_session(rig: Rig) -> None:
    rig.backend.block = "POST"
    rig.start_cycle()
    rig.reader.emit()
    wait_for(rig.backend.entered.is_set)
    rig.bridge.requestStop()
    wait_for(lambda: not rig.bridge.automaticEnabled)
    assert not rig.reader.reading and rig.timers[0].cancelled
    rig.backend.release.set()
    wait_for(lambda: rig.bridge.foundCount == 1)
    assert rig.backend.count("POST") == 1


def test_timeout_and_backend_loss_stop_inventory(rig: Rig) -> None:
    rig.start_cycle()
    rig.timers[0].callback()
    wait_for(lambda: not rig.reader.reading)
    assert rig.timers[0].cancelled
    rig.start_cycle()
    rig.backend.system = "error"
    wait_for(lambda: not rig.reader.reading)
    wait_for(lambda: rig.bridge.operationState == "error")
    rig.backend.system = "ok"
    wait_for(lambda: rig.bridge.operationState == "ok")


def test_database_monitoring_remains_internal_without_changing_readiness(rig: Rig) -> None:
    rig.backend.database = "unavailable"
    wait_for(lambda: rig.runtime.statuses().get(ConnectionKind.DATABASE) is ConnectionStatus.ERROR)
    assert [row["label"] for row in rig.bridge.connections] == [
        "RFID",
        "Internet",
        "Comandos",
        "Sistema",
    ]
    assert rig.bridge.connections[-1]["state"] == "ok"
    assert rig.runtime.automatic.ready
    rig.backend.database = "ok"
    wait_for(
        lambda: rig.runtime.statuses().get(ConnectionKind.DATABASE) is ConnectionStatus.CONNECTED
    )
    assert rig.bridge.connections[-1]["state"] == "ok"


def test_postgresql_health_failure_updates_system_and_preserves_readiness(rig: Rig) -> None:
    rig.backend.system = "error"
    rig.backend.database = "unavailable"
    wait_for(lambda: rig.runtime.statuses().get(ConnectionKind.DATABASE) is ConnectionStatus.ERROR)
    wait_for(lambda: rig.bridge.connections[-1]["state"] == "error")
    assert rig.runtime.statuses()[ConnectionKind.SYSTEM] is ConnectionStatus.ERROR
    assert not rig.runtime.automatic.ready and not rig.bridge.startEnabled
    assert [row["label"] for row in rig.bridge.connections] == [
        "RFID",
        "Internet",
        "Comandos",
        "Sistema",
    ]
    rig.backend.system = rig.backend.database = "ok"
    wait_for(lambda: rig.bridge.startEnabled)
    wait_for(
        lambda: rig.runtime.statuses().get(ConnectionKind.DATABASE) is ConnectionStatus.CONNECTED
    )
    assert rig.bridge.connections[-1]["state"] == "ok"


@pytest.mark.parametrize("size", [(910, 512), (1366, 768), (1920, 1080)])
def test_start_has_only_four_balanced_connection_indicators(
    rig: Rig, size: tuple[int, int], tmp_path: Path
) -> None:
    messages: list[str] = []
    handler = qInstallMessageHandler(lambda kind, context, message: messages.append(message))
    engine, window = create_engine(rig.bridge, rig.configuration, diagnostic_bridge=rig.bridge)
    try:
        window.resize(*size)
        window.show()
        QTest.qWait(80)
        assert window.property("currentPage") == "start"
        bar, items = connection_indicators(window)
        assert [item.property("label") for item in items] == [
            "RFID",
            "Internet",
            "Comandos",
            "Sistema",
        ]
        assert len(items) == 4 and all(item.isVisible() for item in items)
        assert max(item.width() for item in items) - min(item.width() for item in items) <= 1
        assert max(item.y() for item in items) - min(item.y() for item in items) <= 1
        assert items[0].x() == pytest.approx(0, abs=1)
        assert items[-1].x() + items[-1].width() == pytest.approx(bar.width(), abs=1)
        for left, right in zip(items, items[1:], strict=False):
            assert left.x() + left.width() < right.x()
        capture = window.grabWindow()
        assert not capture.isNull() and capture.save(str(tmp_path / "start-aj01.png"))
        assert not messages, "\n".join(messages)
    finally:
        window.close()
        engine.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        qInstallMessageHandler(handler)


def test_four_operational_indicators_receive_existing_worker_events(
    qt_application: object, tmp_path: Path
) -> None:
    runtime = ApplicationRuntime(
        load_config({}), tmp_path / ".env", RuntimeDependencies(reader=Reader())
    )
    bridge = OperationalBridge(runtime, PrototypeTheme.CORPORATE)
    engine, window = create_engine(bridge, diagnostic_bridge=bridge)
    try:
        window.show()
        QTest.qWait(40)
        _, items = connection_indicators(window)
        assert len(items) == 4 and all(item.property("state") == "unknown" for item in items)
        for status in ConnectionStatus:

            def publish(status: ConnectionStatus = status) -> None:
                for kind in ConnectionKind:
                    bridge.eventReceived.emit(RuntimeEvent("connection", (kind, status)))

            worker = threading.Thread(target=publish)
            worker.start()
            worker.join()
            QCoreApplication.processEvents()
            _, items = connection_indicators(window)
            assert [item.property("label") for item in items] == list(CONNECTION_LABELS.values())
            assert all(item.property("state") == STATE_COLORS[status] for item in items)
            assert all(item.property("description") == status.value for item in items)
    finally:
        window.close()
        engine.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        bridge.close()
        runtime.close()


def test_zebra_loss_and_waveshare_loss_stop_and_cancel_timer(rig: Rig) -> None:
    rig.start_cycle()
    rig.reader.fail_connect = True
    rig.reader.disconnect()
    wait_for(lambda: rig.bridge.operationState == "error")
    wait_for(lambda: rig.timers[0].cancelled)
    assert rig.runtime.inventory.status is InventoryStatus.ERROR
    rig.reader.fail_connect = False
    wait_for(lambda: rig.runtime.inventory.status is InventoryStatus.STOPPED)
    wait_for(lambda: rig.bridge.operationState == "ok")
    rig.start_cycle()
    assert rig.reader.starts == 2


def test_failure_starting_zebra_never_indicates_active_inventory(rig: Rig) -> None:
    rig.reader.fail_start = True
    rig.bridge.requestStart()
    wait_for(lambda: rig.bridge.automaticEnabled)
    samples = rig.port.samples
    wait_for(lambda: rig.port.samples >= samples + 2)
    rig.port.inputs = (False, True, False, True, False)
    wait_for(lambda: rig.reader.starts == 1)
    assert not rig.reader.reading
    assert not rig.timers
    assert rig.port.relays[1] is False
    rig.bridge.requestStop()
    wait_for(lambda: not rig.bridge.automaticEnabled)
    rig.reader.fail_start = False
    wait_for(lambda: rig.bridge.startEnabled)
    rig.start_cycle()
    assert rig.reader.reading and len(rig.timers) == 1


def test_waveshare_loss_disables_automatic_mode(rig: Rig) -> None:
    rig.start_cycle()
    rig.port.fail = True
    wait_for(lambda: not rig.bridge.automaticEnabled)
    assert not rig.reader.reading and rig.timers[0].cancelled
    wait_for(lambda: rig.port.closed)


@pytest.mark.parametrize("blocked_method", ["GET", "POST"])
def test_shutdown_during_http_waits_and_ignores_late_ui_events(
    rig: Rig, blocked_method: str
) -> None:
    rig.backend.block = blocked_method
    rig.start_cycle()
    rig.reader.emit()
    wait_for(rig.backend.entered.is_set)
    rig.bridge.beginClose()
    thread = threading.Thread(target=rig.runtime.close)
    thread.start()
    wait_for(lambda: not rig.reader.reading)
    assert thread.is_alive()
    rig.backend.release.set()
    thread.join(3)
    assert not thread.is_alive()
    QCoreApplication.processEvents()
    assert rig.bridge.foundCount == 0
    assert rig.backend.count("POST") == (1 if blocked_method == "POST" else 0)
    assert rig.port.closed and not rig.runtime.serial_gate.is_locked()


def test_qml_operational_buttons_diagnostic_and_configuration(rig: Rig) -> None:
    messages: list[str] = []
    handler = qInstallMessageHandler(lambda kind, context, message: messages.append(message))
    engine, window = create_engine(rig.bridge, rig.configuration, diagnostic_bridge=rig.bridge)
    try:
        window.show()
        QTest.qWait(50)
        assert window.findChild(QObject, "startButton").property("enabled")
        window.findChild(QObject, "startButton").clicked.emit()
        wait_for(lambda: rig.bridge.automaticEnabled)
        assert rig.reader.starts == 0
        rig.start_cycle()
        rig.reader.emit()
        wait_for(lambda: rig.bridge.foundCount == 1)
        assert window.findChild(QObject, "foundCount").property("text") == "1"
        window.findChild(QObject, "settingsNavigation").clicked.emit()
        window.findChild(QObject, "diagnosticButton").clicked.emit()
        assert window.property("currentPage") == "diagnostic"
        assert not visual_child(window, "relayOn1").property("enabled")
        for channel in (4, 6, 7, 8):
            control = visual_child(window, f"relayOn{channel}")
            assert control.property("enabled")
            control.clicked.emit()
            wait_for(lambda channel=channel: rig.port.relays[channel - 1])
            wait_for(lambda channel=channel: rig.bridge.diagnosticRelays[channel - 1] is True)
        window.findChild(QObject, "startNavigation").clicked.emit()
        window.findChild(QObject, "stopButton").clicked.emit()
        wait_for(lambda: not rig.bridge.automaticEnabled)
        rig.bridge.connectDiagnostic()
        QTest.qWait(50)
        rig.bridge.setRelay(8, False)
        wait_for(lambda: not rig.port.relays[7])
        assert rig.configuration._reader is rig.runtime.reader_configuration
        assert rig.configuration._waveshare is rig.runtime.waveshare_configuration
        assert rig.configuration.testBackend("https://backend.test")
        wait_for(lambda: not rig.configuration.busy)
        assert rig.configuration.feedback["backend"]["state"] == "ok"
        assert not messages, "\n".join(messages)
    finally:
        window.close()
        engine.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        qInstallMessageHandler(handler)


def test_slow_llrp_does_not_block_qt_slots_or_event_delivery(
    rig: Rig, monkeypatch: pytest.MonkeyPatch
) -> None:
    entered, release = threading.Event(), threading.Event()
    original_start = rig.reader.start_inventory

    def slow_start(callback: Callable[..., None]) -> bool:
        entered.set()
        assert release.wait(3)
        return original_start(callback)

    monkeypatch.setattr(rig.reader, "start_inventory", slow_start)
    rig.bridge.requestStart()
    wait_for(lambda: rig.bridge.automaticEnabled)
    samples = rig.port.samples
    wait_for(lambda: rig.port.samples >= samples + 2)
    rig.port.inputs = (False, True, False, True, False)
    wait_for(entered.is_set)
    # Uma resposta do executor pode chegar enquanto o controlador aguarda LLRP.
    rig.bridge.eventReceived.emit(RuntimeEvent("command", CommandFinished("start", True)))
    timeout = threading.Timer(1, release.set)
    timeout.start()
    try:
        started = time.monotonic()
        QCoreApplication.processEvents()
        rig.bridge.setRelay(4, True)
        rig.bridge.requestStop()
        assert time.monotonic() - started < 0.2
    finally:
        release.set()
        timeout.cancel()
        timeout.join()
    wait_for(lambda: not rig.bridge.automaticEnabled)
    assert not rig.reader.reading


def test_configuration_tests_reuse_live_services_and_refuse_reader_during_auto(rig: Rig) -> None:
    original_reader = rig.runtime.reader
    assert rig.configuration.testReader("Teste", "reader.test", "5084")
    wait_for(lambda: not rig.configuration.busy)
    assert rig.configuration.feedback["reader"]["state"] == "ok"
    assert rig.runtime.reader is original_reader and rig.reader.connected
    assert rig.reader.connections == 3
    assert rig.port.opens == 1
    fields = rig.configuration.fields
    assert rig.configuration.testWaveshare(
        fields["serial_port"],
        fields["baud_rate"],
        fields["data_bits"],
        fields["parity"],
        fields["stop_bits"],
        fields["device_id"],
    )
    wait_for(lambda: not rig.configuration.busy)
    assert rig.configuration.feedback["waveshare"]["state"] == "ok"
    assert rig.port.opens == 1
    rig.bridge.requestStart()
    wait_for(lambda: rig.bridge.automaticEnabled)
    assert rig.configuration.testReader("Teste", "reader.test", "5084")
    wait_for(lambda: not rig.configuration.busy)
    assert rig.configuration.feedback["reader"]["state"] == "error"
    assert rig.reader.connected and rig.reader.connections == 3
