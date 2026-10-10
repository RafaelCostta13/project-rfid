import math
import os
import subprocess
import sys
from pathlib import Path

import pytest

pytest.importorskip("PySide6")

from PySide6.QtGui import QImage


def test_configuration_startup_has_no_operational_io_or_workers(
    tmp_path: Path, qt_application: object
) -> None:
    script = """
import builtins
import socket
import threading
import urllib.request
from pathlib import Path
import pymodbus.client
import serial
original_import = builtins.__import__
blocked = ('rfid_reader.runtime', 'tkinter')
def guarded_import(name, *args, **kwargs):
    if any(name == item or name.startswith(item + '.') for item in blocked):
        raise AssertionError('Composição operacional indevida: ' + name)
    return original_import(name, *args, **kwargs)
def forbidden(*args, **kwargs):
    raise AssertionError('I/O ou thread operacional não autorizada')
builtins.__import__ = guarded_import
socket.create_connection = forbidden
socket.socket.connect = forbidden
urllib.request.urlopen = forbidden
serial.Serial = forbidden
pymodbus.client.ModbusSerialClient = forbidden
threading.Thread.start = forbidden
# Os __init__.py legados reexportam classes de drivers; importar não as inicializa.
from rfid_reader.readers.zebra_fx9600 import ZebraFX9600Reader
from rfid_reader.integrations.backend_client import BackendRFIDClient
from rfid_reader.services.connection_monitor import ConnectionMonitor
ZebraFX9600Reader.__init__ = forbidden
BackendRFIDClient.__init__ = forbidden
ConnectionMonitor.__init__ = forbidden
from rfid_reader.config import load_config
from rfid_reader.ui.qt.application import run_configuration
from rfid_reader.ui.qt.mock_data import PrototypeTheme
result = run_configuration(load_config({}), Path('unused.env'), PrototypeTheme.CORPORATE,
                           screenshot=Path('settings.png'), initial_page='settings')
assert result == 0
assert not Path('unused.env').exists()
assert Path('settings.png').exists()
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=tmp_path,
        env={**os.environ, "QT_QPA_PLATFORM": "offscreen", "QT_QUICK_BACKEND": "software"},
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stderr == ""


@pytest.mark.parametrize(("width", "height"), [(1366, 768), (1600, 900), (1920, 1080)])
@pytest.mark.parametrize("scale", [1.0, 1.25, 1.5])
def test_settings_render_at_windows_resolutions_and_dpi(
    width: int, height: int, scale: float, tmp_path: Path, qt_application: object
) -> None:
    screenshot = tmp_path / "settings.png"
    script = """
import sys
from pathlib import Path
from rfid_reader.config import load_config
from rfid_reader.ui.qt.application import run_configuration
from rfid_reader.ui.qt.mock_data import PrototypeTheme
raise SystemExit(run_configuration(load_config({}), Path('unused.env'), PrototypeTheme.CORPORATE,
                 size=(int(sys.argv[1]), int(sys.argv[2])), screenshot=Path(sys.argv[3]),
                 initial_page='settings'))
"""
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            script,
            str(math.ceil(width / scale)),
            str(math.ceil(height / scale)),
            str(screenshot),
        ],
        cwd=tmp_path,
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
    capture = QImage(str(screenshot))
    assert not capture.isNull()
    assert abs(capture.width() - width) <= 2
    assert abs(capture.height() - height) <= 2
    assert not (tmp_path / "unused.env").exists()
