import socket
import sys
from pathlib import Path
from types import ModuleType

import pytest

from rfid_reader.cli import main
from rfid_reader.config import Settings
from rfid_reader.ui.qt.mock_data import PrototypeTheme


def valid_environment() -> dict[str, str]:
    return {
        "RFID_READER_HOST": "reader.local",
        "RFID_READER_PORT": "5084",
        "RFID_READER_NAME": "fx9600-test",
        "RFID_ANTENNAS": "1,2",
        "RFID_DEDUPLICATION_WINDOW_SECONDS": "2.0",
        "SHAREPOINT_SYNC_URL": "https://example.test/sync",
        "RFID_LOG_LEVEL": "INFO",
    }


def test_check_config_returns_success_and_prints_safe_summary(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = main(["check-config"], valid_environment())

    assert exit_code == 0
    captured = capsys.readouterr()
    assert captured.out == (
        "Configuração válida\n"
        "Reader: fx9600-test\n"
        "Host: reader.local:5084\n"
        "Antenas: 1, 2\n"
        "Log level: INFO\n"
    )
    assert captured.err == ""


def test_check_config_returns_error_for_invalid_configuration(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = main(["check-config"], {"RFID_READER_HOST": ""})

    assert exit_code != 0
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "RFID_READER_HOST" in captured.err


def test_check_config_does_not_access_network(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_if_called(*args: object, **kwargs: object) -> None:
        raise AssertionError("check-config não deve acessar a rede")

    monkeypatch.setattr(socket, "create_connection", fail_if_called)

    assert main(["check-config"], valid_environment()) == 0


@pytest.mark.parametrize("options", [[], ["show"], ["--operate"]])
def test_official_entrypoint_opens_qt_with_validated_settings(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    options: list[str],
) -> None:
    received: list[tuple[Settings, Path]] = []
    module = ModuleType("rfid_reader.ui.qt.application")

    def operate(settings: Settings, path: Path, theme: PrototypeTheme, **kwargs: object) -> int:
        received.append((settings, path))
        return 0

    module.run_operational = operate
    module.PrototypeError = RuntimeError
    monkeypatch.setitem(sys.modules, module.__name__, module)
    configuration_path = tmp_path / ".env"

    assert main(options, valid_environment(), configuration_path) == 0
    assert received[0][0].reader_host == "reader.local"
    assert received[0][1] == configuration_path


def test_official_entrypoint_reports_qt_start_error(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    module = ModuleType("rfid_reader.ui.qt.application")

    def fail_to_start(*args: object, **kwargs: object) -> int:
        raise RuntimeError("interface indisponível")

    module.run_operational = fail_to_start
    module.PrototypeError = RuntimeError
    monkeypatch.setitem(sys.modules, module.__name__, module)

    assert main(["show"], valid_environment(), tmp_path / ".env") == 1
    assert "interface indisponível" in capsys.readouterr().err


def test_check_config_accepts_explicit_file_without_importing_qt(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setitem(sys.modules, "rfid_reader.cli_qt", None)
    path = tmp_path / "station.env"
    path.write_text("RFID_READER_NAME=Teste\n", encoding="utf-8")
    assert main(["check-config", "--env-file", str(path)], valid_environment()) == 0


def test_official_cli_forwards_preview_without_operational_configuration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = ModuleType("rfid_reader.ui.qt.application")
    received: list[object] = []

    def preview(*args: object, **kwargs: object) -> int:
        received.append(args)
        return 0

    module.run_prototype = preview
    module.PrototypeError = RuntimeError
    monkeypatch.setitem(sys.modules, module.__name__, module)
    assert main(["--preview"], {"RFID_READER_PORT": "invalid"}) == 0
    assert len(received) == 1
