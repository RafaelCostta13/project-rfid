import threading

import pytest

pytest.importorskip("PySide6")

from PySide6.QtCore import QCoreApplication
from PySide6.QtTest import QSignalSpy

from rfid_reader.ui.qt.bridge import PrototypeBridge
from rfid_reader.ui.qt.mock_data import PrototypeScenario


@pytest.mark.parametrize(
    ("scenario", "state", "title", "count"),
    [
        (PrototypeScenario.READY, "ok", "Aguardando", 5),
        (PrototypeScenario.READING, "warning", "Lendo", 5),
        (PrototypeScenario.FAILURE, "error", "Indisponível", 5),
        (PrototypeScenario.CHECKING, "checking", "Verificando", 5),
        (PrototypeScenario.EMPTY, "ok", "Aguardando", 0),
    ],
)
def test_five_visual_scenarios(
    scenario: PrototypeScenario,
    state: str,
    title: str,
    count: int,
    qt_application: object,
) -> None:
    bridge = PrototypeBridge(scenario=scenario)
    assert bridge.property("operationState") == state
    assert bridge.property("operationTitle") == title
    assert bridge.property("foundCount") == count
    assert [connection["label"] for connection in bridge.property("connections")] == [
        "RFID",
        "Internet",
        "Comandos",
        "Sistema",
    ]


def test_start_only_arms_simulation_and_stop_keeps_results(qt_application: object) -> None:
    bridge = PrototypeBridge()
    changed = QSignalSpy(bridge.changed)
    bridge.requestStart()
    assert bridge.property("operationTitle") == "Aguardando DI1"
    assert bridge.property("startEnabled") is False
    assert bridge.property("stopEnabled") is True
    bridge.requestStart()
    assert changed.count() == 1
    bridge.requestStop()
    bridge.requestStop()
    assert changed.count() == 2
    assert bridge.property("foundCount") == 5
    assert bridge.property("operationTitle") == "Aguardando"


@pytest.mark.parametrize("scenario", [PrototypeScenario.FAILURE, PrototypeScenario.CHECKING])
def test_unavailable_scenarios_do_not_arm(
    scenario: PrototypeScenario,
    qt_application: object,
) -> None:
    bridge = PrototypeBridge(scenario=scenario)
    bridge.requestStart()
    assert bridge.property("stopEnabled") is False
    assert bridge.property("startEnabled") is False


def test_stop_reading_changes_only_visual_state(qt_application: object) -> None:
    bridge = PrototypeBridge(scenario=PrototypeScenario.READING)
    bridge.requestStop()
    assert bridge.property("scenario") == "ready"
    assert bridge.property("foundCount") == 5


def test_theme_and_scenario_only_notify_real_changes(qt_application: object) -> None:
    bridge = PrototypeBridge()
    changed = QSignalSpy(bridge.changed)
    assert bridge.selectTheme("corporate")
    assert bridge.selectScenario("ready")
    assert changed.count() == 0
    assert bridge.selectTheme("navy")
    assert bridge.selectScenario("empty")
    assert bridge.property("foundCount") == 0
    assert bridge.selectScenario("ready")
    assert bridge.property("foundCount") == 5
    assert changed.count() == 3
    assert not bridge.selectTheme("invalid")
    assert not bridge.selectScenario("invalid")
    assert changed.count() == 3


def test_worker_scenario_is_applied_on_gui_thread(qt_application: object) -> None:
    bridge = PrototypeBridge()
    gui_thread = threading.get_ident()
    notifications: list[int] = []
    bridge.changed.connect(lambda: notifications.append(threading.get_ident()))
    worker = threading.Thread(target=bridge.queue_scenario, args=("failure",))
    worker.start()
    worker.join(timeout=2)
    assert not worker.is_alive()
    assert bridge.property("scenario") == "ready"
    QCoreApplication.processEvents()
    assert bridge.property("scenario") == "failure"
    assert notifications == [gui_thread]
