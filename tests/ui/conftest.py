import os
from collections.abc import Iterator
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def qt_application() -> Iterator[object]:
    pytest.importorskip("PySide6", reason="Instale o extra qt para executar os testes QML.")
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    os.environ.setdefault("QT_QUICK_BACKEND", "software")
    if os.name == "nt":
        os.environ.setdefault(
            "QT_QPA_FONTDIR", str(Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts")
        )
    from PySide6.QtGui import QGuiApplication
    from PySide6.QtQuickControls2 import QQuickStyle

    QQuickStyle.setStyle("Basic")
    application = QGuiApplication.instance() or QGuiApplication(["rfid-qt-tests"])
    yield application
    application.processEvents()
