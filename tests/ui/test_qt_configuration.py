import threading
from collections.abc import Callable, Iterator
from pathlib import Path

import pytest
from dotenv import dotenv_values

pytest.importorskip("PySide6")

from PySide6.QtCore import QCoreApplication, QEvent, QObject, Qt, QTimer, qInstallMessageHandler
from PySide6.QtQuick import QQuickItem
from PySide6.QtTest import QTest

from rfid_reader.config import load_config
from rfid_reader.services import reader_configuration
from rfid_reader.ui.qt.application import create_engine
from rfid_reader.ui.qt.configuration import ConfigurationBridge, ConfigurationFeedback
from rfid_reader.ui.qt.status_bridge import ConnectionBridge


def wait_for(predicate: Callable[[], bool]) -> None:
    for _ in range(300):
        QTest.qWait(5)
        if predicate():
            return
    raise AssertionError("O evento Qt não chegou dentro do limite.")


@pytest.fixture
def configuration(qt_application: object, tmp_path: Path) -> Iterator[ConfigurationBridge]:
    bridge = ConfigurationBridge(load_config({}), tmp_path / ".env")
    yield bridge
    bridge.close()
    QCoreApplication.processEvents()


def save_and_wait(bridge: ConfigurationBridge, save: Callable[[], bool]) -> None:
    assert save()
    wait_for(lambda: not bridge.property("busy"))


def test_save_all_sections_preserves_file_and_reloads(
    configuration: ConfigurationBridge, tmp_path: Path
) -> None:
    path = tmp_path / ".env"
    untouched = b"# comentario\r\nCUSTOM=preservar\r\nTOKEN=ficticio-nao-exibir\r\n"
    path.write_bytes(untouched)
    finished: list[tuple[str, bool]] = []
    configuration.finished.connect(lambda section, success: finished.append((section, success)))
    save_and_wait(
        configuration, lambda: configuration.saveReader(" Reader D01 ", "reader.test", "6000")
    )
    save_and_wait(
        configuration, lambda: configuration.saveWaveshare("COM10", "19200", "7", "Even", "2", "15")
    )
    save_and_wait(configuration, lambda: configuration.saveStation(" d-02 "))
    save_and_wait(
        configuration, lambda: configuration.saveBackend(" https://backend.example.test/ ")
    )
    assert path.read_bytes().startswith(untouched)
    values = {key: value for key, value in dotenv_values(path).items() if value is not None}
    reopened = ConfigurationBridge(load_config(values), path)
    try:
        assert reopened.property("fields") == configuration.property("fields")
        assert reopened.property("fields")["station_dock"] == "D-02"
        assert reopened.property("fields")["serial_port"] == "COM10"
        assert reopened.property("fields")["reader_port"] == "6000"
        assert finished == [
            ("reader", True),
            ("waveshare", True),
            ("station", True),
            ("backend", True),
        ]
        assert all(value["state"] == "ok" for value in configuration.property("feedback").values())
    finally:
        reopened.close()


@pytest.mark.parametrize("section", ["reader", "waveshare", "station"])
def test_validation_keeps_file_and_memory_unchanged(
    section: str, configuration: ConfigurationBridge, tmp_path: Path
) -> None:
    before = configuration.property("fields")
    invalid = {
        "reader": lambda: configuration.saveReader("Reader", "reader.test", "invalid"),
        "waveshare": lambda: configuration.saveWaveshare("COM1", "9600", "8", "None", "1", "0"),
        "station": lambda: configuration.saveStation("invalid/dock"),
    }
    save_and_wait(configuration, invalid[section])
    assert configuration.property("feedback")[section]["state"] == "error"
    assert configuration.property("fields") == before
    assert not (tmp_path / ".env").exists()


def test_backend_keeps_existing_trim_only_validation(configuration: ConfigurationBridge) -> None:
    save_and_wait(configuration, lambda: configuration.saveBackend("  backend-local  "))
    assert configuration.property("fields")["backend_url"] == "backend-local"
    save_and_wait(configuration, lambda: configuration.saveBackend(""))
    assert configuration.property("fields")["backend_url"] == ""


@pytest.mark.parametrize("section", ["reader", "waveshare", "station", "backend"])
def test_io_failure_does_not_update_memory_or_original_file(
    section: str,
    configuration: ConfigurationBridge,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / ".env"
    original = b"CUSTOM=preservar\r\n"
    path.write_bytes(original)
    before = configuration.property("fields")

    def fail_replace(source: Path, destination: Path) -> None:
        raise PermissionError("falha simulada")

    monkeypatch.setattr(reader_configuration.os, "replace", fail_replace)
    operations = {
        "reader": lambda: configuration.saveReader("Novo", "reader.test", "6000"),
        "waveshare": lambda: configuration.saveWaveshare("COM10", "9600", "8", "None", "1", "1"),
        "station": lambda: configuration.saveStation("D02"),
        "backend": lambda: configuration.saveBackend("https://backend.example.test"),
    }
    save_and_wait(configuration, operations[section])
    assert configuration.property("feedback")[section]["state"] == "error"
    assert configuration.property("fields") == before
    assert path.read_bytes() == original
    assert not list(tmp_path.glob("*.tmp"))


def test_save_runs_outside_gui_and_rejects_overlapping_commands(
    configuration: ConfigurationBridge, monkeypatch: pytest.MonkeyPatch
) -> None:
    started, release = threading.Event(), threading.Event()
    worker_ids: list[int] = []
    original_save = configuration._reader.save

    def delayed_save(name: str, host: str, port: str) -> bool:
        worker_ids.append(threading.get_ident())
        started.set()
        assert release.wait(2)
        return original_save(name, host, port)

    monkeypatch.setattr(configuration._reader, "save", delayed_save)
    tick: list[bool] = []
    try:
        assert configuration.saveReader("Novo", "reader.test", "6000")
        assert started.wait(1)
        assert configuration.property("busy")
        assert not configuration.saveStation("D02")
        assert not configuration.saveBackend("https://backend.example.test")
        QTimer.singleShot(0, lambda: tick.append(True))
        wait_for(lambda: bool(tick))
        assert worker_ids != [threading.get_ident()]
    finally:
        release.set()
    wait_for(lambda: not configuration.property("busy"))


def test_close_waits_for_inflight_save_and_ignores_late_callbacks(
    configuration: ConfigurationBridge, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    started, release = threading.Event(), threading.Event()
    original_save = configuration._backend.save

    def delayed_save(value: str) -> bool:
        started.set()
        assert release.wait(2)
        return original_save(value)

    monkeypatch.setattr(configuration._backend, "save", delayed_save)
    finished: list[bool] = []
    configuration.finished.connect(lambda section, success: finished.append(success))
    assert configuration.saveBackend("https://backend.example.test")
    try:
        assert started.wait(1)
        configuration.beginClose()
        assert not configuration.saveStation("D03")
    finally:
        release.set()
        configuration.close()
    QCoreApplication.processEvents()
    assert finished == []
    assert (
        dotenv_values(tmp_path / ".env")["RFID_BACKEND_BASE_URL"] == "https://backend.example.test"
    )
    assert not any(thread.name.startswith("qt-configuration") for thread in threading.enumerate())
    configuration.close()


def test_unexpected_worker_error_is_reported_without_form_secrets(
    configuration: ConfigurationBridge,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    def fail(value: str) -> bool:
        raise RuntimeError("secret-do-formulario")

    monkeypatch.setattr(configuration._backend, "save", fail)
    save_and_wait(configuration, lambda: configuration.saveBackend("secret-do-formulario"))
    assert configuration.property("feedback")["backend"]["state"] == "error"
    assert "error_type=RuntimeError" in caplog.text
    assert "secret-do-formulario" not in caplog.text
    assert "secret-do-formulario" not in configuration.property("feedback")["backend"]["message"]


def test_feedback_is_queued_on_gui_and_invalid_events_ignored(
    configuration: ConfigurationBridge,
) -> None:
    notifications: list[int] = []
    configuration.changed.connect(lambda: notifications.append(threading.get_ident()))
    configuration.feedbackReceived.emit("invalid")
    thread = threading.Thread(
        target=lambda: configuration.feedbackReceived.emit(
            ConfigurationFeedback("reader", True, "Salvo")
        )
    )
    thread.start()
    thread.join()
    assert notifications == []
    wait_for(lambda: bool(notifications))
    assert notifications == [threading.get_ident()]
    copy = configuration.property("feedback")
    copy["reader"]["message"] = "mutado"
    assert configuration.property("feedback")["reader"]["message"] == "Salvo"


@pytest.mark.parametrize("size", [(1366, 768), (1600, 900), (1920, 1080), (910, 512)])
def test_configuration_qml_loads_and_saves_without_operations(
    size: tuple[int, int], configuration: ConfigurationBridge, tmp_path: Path
) -> None:
    messages: list[str] = []
    old_handler = qInstallMessageHandler(lambda kind, context, message: messages.append(message))
    bridge = ConnectionBridge()
    engine, window = create_engine(bridge, configuration, initial_page="settings")
    try:
        window.resize(*size)
        window.show()
        QTest.qWait(50)
        assert window.findChild(QObject, "settingsPage").property("visible")
        assert window.findChild(QObject, "settingsNavigation").property("enabled")
        assert not window.findChild(QObject, "scenarioSelector").property("visible")
        for name in (
            "startButton",
            "stopButton",
            "readerTestButton",
            "waveshareTestButton",
            "backendTestButton",
        ):
            assert not window.findChild(QObject, name).property("enabled")
        assert not (tmp_path / ".env").exists()
        window.findChild(QObject, "readerNameField").setProperty("text", " Reader novo ")
        window.findChild(QObject, "readerHostField").setProperty("text", "reader.test")
        window.findChild(QObject, "readerPortField").setProperty("text", "6000")
        window.findChild(QObject, "readerSaveButton").clicked.emit()
        wait_for(lambda: not configuration.property("busy"))
        assert window.findChild(QObject, "readerNameField").property("text") == "Reader novo"
        assert window.findChild(QObject, "readerFeedback").property("text")
        assert not window.grabWindow().isNull()
        window.findChild(QObject, "startNavigation").clicked.emit()
        assert window.property("currentPage") == "start"
        window.findChild(QObject, "settingsNavigation").clicked.emit()
        assert window.property("currentPage") == "settings"
        assert not messages, "\n".join(messages)
    finally:
        window.close()
        engine.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        bridge.close()
        qInstallMessageHandler(old_handler)


def test_dock_combo_accepts_keyboard_custom_value(configuration: ConfigurationBridge) -> None:
    bridge = ConnectionBridge()
    engine, window = create_engine(bridge, configuration, initial_page="settings")
    try:
        window.show()
        QTest.qWait(30)
        dock = window.findChild(QQuickItem, "dockField")
        editor = dock.property("contentItem")
        editor.forceActiveFocus()
        QTest.keyClick(window, Qt.Key.Key_A, Qt.KeyboardModifier.ControlModifier)
        for key in (Qt.Key.Key_D, Qt.Key.Key_Minus, Qt.Key.Key_0, Qt.Key.Key_7):
            QTest.keyClick(window, key)
        window.findChild(QObject, "dockSaveButton").clicked.emit()
        wait_for(lambda: not configuration.property("busy"))
        assert configuration.property("fields")["station_dock"] == "D-07"
        assert dock.property("editText") == "D-07"
    finally:
        window.close()
        engine.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        bridge.close()


def test_settings_scroll_and_section_save_preserve_other_drafts(
    configuration: ConfigurationBridge,
) -> None:
    bridge = ConnectionBridge()
    engine, window = create_engine(bridge, configuration, initial_page="settings")
    try:
        window.resize(910, 512)
        window.show()
        QTest.qWait(30)
        page = window.findChild(QQuickItem, "settingsPage")
        flickable = page.property("contentItem")
        assert flickable.property("contentHeight") > flickable.height()
        flickable.setProperty("contentY", flickable.property("contentHeight") - flickable.height())
        QTest.qWait(10)
        save_button = window.findChild(QQuickItem, "backendSaveButton")
        assert 0 <= save_button.mapToItem(page, 0, 0).y() < page.height()
        window.findChild(QObject, "serialPortField").setProperty("text", "draft-COM10")
        url_field = window.findChild(QObject, "backendUrlField")
        url_field.setProperty("text", " https://backend.example.test ")
        save_button.clicked.emit()
        wait_for(lambda: not configuration.property("busy"))
        assert url_field.property("text") == "https://backend.example.test"
        assert window.findChild(QObject, "serialPortField").property("text") == "draft-COM10"
        window.findChild(QObject, "readerPortField").setProperty("text", "invalid")
        window.findChild(QObject, "readerSaveButton").clicked.emit()
        wait_for(lambda: not configuration.property("busy"))
        assert window.findChild(QObject, "readerPortField").property("text") == "invalid"
        assert configuration.property("feedback")["reader"]["state"] == "error"
    finally:
        window.close()
        engine.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        bridge.close()
