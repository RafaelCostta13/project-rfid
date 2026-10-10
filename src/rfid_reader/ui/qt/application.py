"""Entradas Qt de operação, prévia visual e configuração isolada."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, QTimer, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickWindow
from PySide6.QtQuickControls2 import QQuickStyle

from rfid_reader.ui.qt.bridge import PrototypeBridge
from rfid_reader.ui.qt.mock_data import PrototypeScenario, PrototypeTheme

if TYPE_CHECKING:
    from rfid_reader.config import Settings
    from rfid_reader.ui.qt.configuration import ConfigurationBridge

QML_PATH = Path(__file__).resolve().parent.parent / "qml" / "Main.qml"


class PrototypeError(RuntimeError):
    """Falha ao carregar ou renderizar a prévia QML."""


def create_engine(
    bridge: QObject,
    settings_bridge: QObject | None = None,
    *,
    diagnostic_bridge: QObject | None = None,
    initial_page: str = "start",
) -> tuple[QQmlApplicationEngine, QQuickWindow]:
    """Carrega exclusivamente recursos empacotados, sem depender do cwd."""

    engine = QQmlApplicationEngine()
    properties: dict[str, object] = {"uiBridge": bridge, "initialPage": initial_page}
    # Python None vira undefined, não null, em uma propriedade var do QML.
    if settings_bridge is not None:
        properties["settingsBridge"] = settings_bridge
    if diagnostic_bridge is not None:
        properties["diagnosticBridge"] = diagnostic_bridge
    engine.setInitialProperties(properties)
    engine.load(QUrl.fromLocalFile(str(QML_PATH)))
    roots = engine.rootObjects()
    if not roots or not isinstance(roots[0], QQuickWindow):
        raise PrototypeError("Não foi possível carregar Main.qml; consulte os erros QML.")
    return engine, roots[0]


def run_prototype(
    theme: PrototypeTheme,
    scenario: PrototypeScenario,
    *,
    windowed: bool = False,
    size: tuple[int, int] = (1366, 768),
    screenshot: Path | None = None,
) -> int:
    """Executa um único event loop Qt; nenhuma configuração operacional é lida."""

    QQuickStyle.setStyle("Basic")
    application = QGuiApplication(["rfid-reader-qt"])
    application.setApplicationName("DSV RFID · Protótipo simulado")
    application.setOrganizationName("DSV")
    bridge = PrototypeBridge(theme, scenario)
    return _run_window(application, bridge, windowed=windowed, size=size, screenshot=screenshot)


def run_configuration(
    settings: Settings,
    path: Path,
    theme: PrototypeTheme,
    *,
    windowed: bool = False,
    size: tuple[int, int] = (1366, 768),
    screenshot: Path | None = None,
    initial_page: str = "start",
) -> int:
    """Configuração local, sem conectar RFID/COM/HTTP nem habilitar operações."""

    from rfid_reader.ui.qt.configuration import ConfigurationBridge
    from rfid_reader.ui.qt.status_bridge import ConnectionBridge

    QQuickStyle.setStyle("Basic")
    application = QGuiApplication(["rfid-reader-qt"])
    application.setApplicationName("DSV RFID · Configurações locais")
    application.setOrganizationName("DSV")
    bridge = ConnectionBridge(theme)
    configuration = ConfigurationBridge(settings, path)
    try:
        return _run_window(
            application,
            bridge,
            settings_bridge=configuration,
            windowed=windowed,
            size=size,
            screenshot=screenshot,
            initial_page=initial_page,
        )
    finally:
        bridge.close()
        configuration.close()


def _run_window(
    application: QGuiApplication,
    bridge: QObject,
    *,
    settings_bridge: ConfigurationBridge | None = None,
    diagnostic_bridge: QObject | None = None,
    windowed: bool,
    size: tuple[int, int],
    screenshot: Path | None,
    initial_page: str = "start",
) -> int:
    engine, window = create_engine(
        bridge, settings_bridge, diagnostic_bridge=diagnostic_bridge, initial_page=initial_page
    )
    window.resize(*size)
    if windowed or screenshot is not None:
        window.show()
    else:
        window.showMaximized()
    capture_error: str | None = None

    def capture() -> None:
        nonlocal capture_error
        if screenshot is None:
            return
        try:
            screenshot.parent.mkdir(parents=True, exist_ok=True)
            captured = window.grabWindow()
            if captured.isNull() or not captured.save(str(screenshot)):
                capture_error = "Não foi possível salvar a captura PNG do protótipo."
        except (OSError, ValueError, RuntimeError) as error:
            capture_error = f"Falha na captura do protótipo: {error}"
        finally:
            application.exit(1 if capture_error else 0)

    if screenshot is not None:
        QTimer.singleShot(700, capture)
    try:
        result = application.exec()
        if capture_error:
            raise PrototypeError(capture_error)
        return result
    finally:
        window.close()
        engine.deleteLater()
        application.processEvents()


def run_operational(
    settings: Settings,
    path: Path,
    theme: PrototypeTheme,
    *,
    windowed: bool = False,
    size: tuple[int, int] = (1366, 768),
    initial_page: str = "start",
) -> int:
    """Único event loop Qt sobre o runtime operacional compartilhado."""

    from rfid_reader.runtime import ApplicationRuntime, configure_logging
    from rfid_reader.ui.qt.configuration import ConfigurationBridge
    from rfid_reader.ui.qt.operational import OperationalBridge

    configure_logging(settings.log_level)
    QQuickStyle.setStyle("Basic")
    application = QGuiApplication(["rfid-reader-qt"])
    application.setApplicationName("DSV RFID")
    application.setOrganizationName("DSV")
    runtime = ApplicationRuntime(settings, path)
    bridge = OperationalBridge(runtime, theme)
    configuration = ConfigurationBridge(settings, path, runtime)
    # O bootstrap ocorre somente depois de o QML carregar com sucesso.
    QTimer.singleShot(0, runtime.start)
    application.aboutToQuit.connect(bridge.beginClose)
    application.aboutToQuit.connect(configuration.beginClose)
    try:
        return _run_window(
            application,
            bridge,
            settings_bridge=configuration,
            diagnostic_bridge=bridge,
            windowed=windowed,
            size=size,
            screenshot=None,
            initial_page=initial_page,
        )
    finally:
        bridge.close()
        configuration.close()
        runtime.close()
