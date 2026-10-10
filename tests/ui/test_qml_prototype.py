import math
import os
import subprocess
import sys
from pathlib import Path

import pytest

pytest.importorskip("PySide6")

from PySide6.QtCore import QCoreApplication, QEvent, QObject, Qt, qInstallMessageHandler
from PySide6.QtGui import QImage
from PySide6.QtQuick import QQuickItem
from PySide6.QtTest import QTest

from rfid_reader.ui.qt.application import QML_PATH, create_engine
from rfid_reader.ui.qt.bridge import PrototypeBridge
from rfid_reader.ui.qt.mock_data import PrototypeScenario, PrototypeTheme


@pytest.mark.parametrize("theme", list(PrototypeTheme))
@pytest.mark.parametrize(("width", "height"), [(1366, 768), (1600, 900), (1920, 1080), (910, 512)])
def test_qml_loads_assets_bindings_and_layout(
    theme: PrototypeTheme,
    width: int,
    height: int,
    qt_application: object,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)
    messages: list[str] = []
    old_handler = qInstallMessageHandler(lambda kind, context, message: messages.append(message))
    bridge = PrototypeBridge(theme=theme)
    engine, window = create_engine(bridge)
    try:
        window.resize(width, height)
        window.show()
        QTest.qWait(80)
        logo = window.findChild(QObject, "brandLogo")
        assert logo is not None
        assert logo.property("ready") is True
        assert "dsv_logo.svg" in logo.property("source").toString()
        assert window.findChild(QObject, "foundCount").property("text") == "5"
        assert window.findChild(QObject, "tagTable").property("rows") == 5
        assert not window.findChild(QObject, "settingsNavigation").property("enabled")
        start = window.findChild(QQuickItem, "startButton")
        assert start is not None
        assert start.width() >= 140
        assert start.height() >= 38
        assert window.grabWindow().isNull() is False
        assert not messages, "\n".join(messages)
    finally:
        window.close()
        engine.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        qInstallMessageHandler(old_handler)


def test_qml_updates_scenarios_and_simulated_buttons(qt_application: object) -> None:
    bridge = PrototypeBridge()
    engine, window = create_engine(bridge)
    try:
        window.show()
        QTest.qWait(60)
        start = window.findChild(QObject, "startButton")
        stop = window.findChild(QObject, "stopButton")
        start.clicked.emit()
        assert not start.property("enabled")
        assert stop.property("enabled")
        stop.clicked.emit()
        assert start.property("enabled")
        assert not stop.property("enabled")
        window.findChild(QObject, "themeSelector").activated.emit(1)
        assert bridge.property("theme") == "navy"
        window.findChild(QObject, "scenarioSelector").activated.emit(1)
        assert bridge.property("scenario") == "reading"
        bridge.selectScenario("empty")
        QTest.qWait(30)
        assert window.findChild(QObject, "foundCount").property("text") == "0"
        assert window.findChild(QObject, "emptyState").property("visible")
        for scenario in PrototypeScenario:
            bridge.selectScenario(scenario.value)
            QTest.qWait(10)
            assert window.findChild(QObject, "operationIndicator").property("state") == (
                bridge.property("operationState")
            )
        indicator = window.findChild(QObject, "operationIndicator")
        indicator.setProperty("state", "unknown")
        indicator.setProperty("description", "Desconhecido")
        label = indicator.findChild(QObject, "statusLabel")
        assert label.property("text") == "Desconhecido"
        assert label.property("color").name() == "#96a1ae"
    finally:
        window.close()
        engine.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)


def test_preview_does_not_import_operational_composition_or_access_network() -> None:
    script = """
import builtins
import socket
import urllib.request
original_import = builtins.__import__
blocked = ('rfid_reader.runtime', 'rfid_reader.services', 'rfid_reader.readers',
           'rfid_reader.integrations', 'tkinter', 'serial', 'sllurp')
def guarded_import(name, *args, **kwargs):
    if any(name == item or name.startswith(item + '.') for item in blocked):
        raise AssertionError('Importação operacional indevida: ' + name)
    return original_import(name, *args, **kwargs)
def forbidden(*args, **kwargs):
    raise AssertionError('Acesso à rede proibido no protótipo')
builtins.__import__ = guarded_import
socket.create_connection = forbidden
urllib.request.urlopen = forbidden
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from rfid_reader.ui.qt.application import create_engine
from rfid_reader.ui.qt.bridge import PrototypeBridge
QQuickStyle.setStyle('Basic')
app = QGuiApplication([])
bridge = PrototypeBridge()
engine, window = create_engine(bridge)
bridge.requestStart()
bridge.selectScenario('reading')
bridge.requestStop()
window.close()
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        env={
            **os.environ,
            "QT_QPA_PLATFORM": "offscreen",
            "QT_QUICK_BACKEND": "software",
            "RFID_READER_HOST": "",
            "RFID_BACKEND_BASE_URL": "invalid",
        },
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_theme_popup_supports_keyboard_without_qml_errors(qt_application: object) -> None:
    messages: list[str] = []
    old_handler = qInstallMessageHandler(lambda kind, context, message: messages.append(message))
    bridge = PrototypeBridge()
    engine, window = create_engine(bridge)
    try:
        window.show()
        QTest.qWait(30)
        selector = window.findChild(QQuickItem, "themeSelector")
        selector.forceActiveFocus()
        QTest.keyClick(window, Qt.Key.Key_Space)
        QTest.qWait(20)
        QTest.keyClick(window, Qt.Key.Key_Down)
        QTest.keyClick(window, Qt.Key.Key_Return)
        QTest.qWait(20)
        assert bridge.property("theme") == "navy"
        assert not messages, "\n".join(messages)
    finally:
        window.close()
        engine.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        qInstallMessageHandler(old_handler)


def test_qml_source_has_no_network_or_hardware_calls() -> None:
    for path in QML_PATH.parent.rglob("*.qml"):
        source = path.read_text(encoding="utf-8")
        assert "XMLHttpRequest" not in source
        assert "http://" not in source
        assert "https://" not in source


@pytest.mark.parametrize(("width", "height"), [(1366, 768), (1600, 900), (1920, 1080)])
@pytest.mark.parametrize("scale", [1.0, 1.25, 1.5])
def test_capture_at_windows_resolution_and_dpi(
    width: int,
    height: int,
    scale: float,
    tmp_path: Path,
    qt_application: object,
) -> None:
    path = tmp_path / "dpi.png"
    logical_width, logical_height = math.ceil(width / scale), math.ceil(height / scale)
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "rfid_reader.cli_qt",
            "--preview",
            "--size",
            str(logical_width),
            str(logical_height),
            "--screenshot",
            str(path),
        ],
        env={
            **os.environ,
            "QT_QPA_PLATFORM": "offscreen",
            "QT_QUICK_BACKEND": "software",
            "QT_SCALE_FACTOR": str(scale),
        },
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stderr == ""
    image = QImage(str(path))
    assert not image.isNull()
    assert abs(image.width() - width) <= 2
    assert abs(image.height() - height) <= 2


def test_capture_io_failure_exits_without_background_process(
    tmp_path: Path,
    qt_application: object,
) -> None:
    blocked = tmp_path / "not-a-directory"
    blocked.write_text("arquivo", encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "rfid_reader.cli_qt",
            "--preview",
            "--screenshot",
            str(blocked / "preview.png"),
        ],
        env={**os.environ, "QT_QPA_PLATFORM": "offscreen", "QT_QUICK_BACKEND": "software"},
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    assert result.returncode == 1
    assert "Falha na captura" in result.stderr
