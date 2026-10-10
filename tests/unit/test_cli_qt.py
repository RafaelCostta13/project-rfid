import builtins
import os
import sys
from pathlib import Path
from types import ModuleType

import pytest

from rfid_reader.cli_qt import main
from rfid_reader.config import Settings
from rfid_reader.ui.qt.mock_data import PrototypeScenario, PrototypeTheme


def test_qt_cli_forwards_only_preview_options(monkeypatch: pytest.MonkeyPatch) -> None:
    received: list[tuple[object, ...]] = []
    module = ModuleType("rfid_reader.ui.qt.application")

    def preview(theme: PrototypeTheme, scenario: PrototypeScenario, **kwargs: object) -> int:
        received.append((theme, scenario, kwargs))
        return 0

    module.run_prototype = preview
    module.PrototypeError = RuntimeError
    monkeypatch.setitem(sys.modules, module.__name__, module)
    assert (
        main(
            [
                "--preview",
                "--theme",
                "navy",
                "--scenario",
                "empty",
                "--windowed",
                "--size",
                "1600",
                "900",
                "--screenshot",
                "capture.png",
            ]
        )
        == 0
    )
    assert received == [
        (
            PrototypeTheme.NAVY,
            PrototypeScenario.EMPTY,
            {
                "windowed": True,
                "size": (1600, 900),
                "screenshot": Path("capture.png"),
            },
        )
    ]


def test_qt_cli_explains_missing_dependency(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    original_import = builtins.__import__

    def without_qt(name: str, *args: object, **kwargs: object) -> object:
        if name == "rfid_reader.ui.qt.application":
            raise ModuleNotFoundError("PySide6", name="PySide6")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", without_qt)
    assert main([]) == 1
    assert 'python -m pip install -e "."' in capsys.readouterr().err


def test_qt_cli_reports_load_failure(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    module = ModuleType("rfid_reader.ui.qt.application")

    def fail(*args: object, **kwargs: object) -> int:
        raise RuntimeError("Main.qml indisponível")

    module.run_prototype = fail
    module.PrototypeError = RuntimeError
    monkeypatch.setitem(sys.modules, module.__name__, module)
    assert main(["--preview"]) == 1
    assert "Main.qml indisponível" in capsys.readouterr().err


def test_qt_cli_rejects_invalid_capture_size() -> None:
    with pytest.raises(SystemExit) as error:
        main(["--size", "100", "100"])
    assert error.value.code == 2


def test_qt_cli_rejects_non_png_capture() -> None:
    with pytest.raises(SystemExit) as error:
        main(["--screenshot", "preview.jpg"])
    assert error.value.code == 2


@pytest.mark.parametrize(
    "options",
    [
        ["--preview", "--page", "settings"],
        ["--preview", "--env-file", "other.env"],
        ["--configure", "--scenario", "reading"],
    ],
)
def test_configuration_options_cannot_mix_with_simulation(options: list[str]) -> None:
    with pytest.raises(SystemExit) as error:
        main(options)
    assert error.value.code == 2


def test_configuration_cli_uses_injected_environment_without_reading_files(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    received: list[tuple[Settings, Path, PrototypeTheme, dict[str, object]]] = []
    module = ModuleType("rfid_reader.ui.qt.application")

    def configure(settings: Settings, path: Path, theme: PrototypeTheme, **kwargs: object) -> int:
        received.append((settings, path, theme, kwargs))
        return 0

    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("O ambiente injetado não deve carregar .env")

    module.run_configuration = configure
    module.PrototypeError = RuntimeError
    monkeypatch.setitem(sys.modules, module.__name__, module)
    monkeypatch.setattr("rfid_reader.cli_qt.find_dotenv", forbidden)
    monkeypatch.setattr("rfid_reader.cli_qt.load_dotenv", forbidden)
    path = tmp_path / "config.env"
    assert (
        main(
            ["--configure", "--page", "settings", "--theme", "navy"],
            {"RFID_READER_NAME": "Ficticio"},
            path,
        )
        == 0
    )
    settings, saved_path, theme, kwargs = received[0]
    assert settings.reader_name == "Ficticio"
    assert saved_path == path
    assert theme is PrototypeTheme.NAVY
    assert kwargs["initial_page"] == "settings"
    assert not path.exists()


def test_configuration_cli_preserves_environment_priority_over_dotenv(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = ModuleType("rfid_reader.ui.qt.application")
    received: list[Settings] = []

    def configure(settings: Settings, path: Path, theme: PrototypeTheme, **kwargs: object) -> int:
        received.append(settings)
        return 0

    module.run_configuration = configure
    module.PrototypeError = RuntimeError
    monkeypatch.setitem(sys.modules, module.__name__, module)
    path = tmp_path / ".env"
    path.write_text("RFID_READER_NAME=do-arquivo\nRFID_READER_PORT=6000\n", encoding="utf-8")
    for key in os.environ:
        if key.startswith(("RFID_", "WAVESHARE_", "SHAREPOINT_")):
            monkeypatch.delenv(key)
    monkeypatch.setenv("RFID_READER_NAME", "do-ambiente")
    assert main(["--configure", "--env-file", str(path)]) == 0
    assert received[0].reader_name == "do-ambiente"
    assert received[0].reader_port == 6000


def test_configuration_cli_reports_invalid_settings_before_creating_window(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    module = ModuleType("rfid_reader.ui.qt.application")

    def forbidden(*args: object, **kwargs: object) -> int:
        raise AssertionError("Não deve abrir janela com configuração inválida")

    module.run_configuration = forbidden
    module.PrototypeError = RuntimeError
    monkeypatch.setitem(sys.modules, module.__name__, module)
    assert main(["--configure"], {"RFID_READER_PORT": "invalid"}) == 2
    assert "Erro de configuração" in capsys.readouterr().err


@pytest.mark.parametrize(
    "options",
    [
        ["--operate", "--configure"],
        ["--operate", "--scenario", "reading"],
        ["--operate", "--screenshot", "capture.png"],
        ["--screenshot", "capture.png"],
        ["--preview", "--operate"],
        ["--preview", "--configure"],
        ["--scenario", "ready"],
    ],
)
def test_operational_cli_rejects_mixed_or_automatic_capture_modes(options: list[str]) -> None:
    with pytest.raises(SystemExit) as error:
        main(options)
    assert error.value.code == 2


def test_operational_cli_passes_validated_config_to_runtime_entrypoint(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = ModuleType("rfid_reader.ui.qt.application")
    received: list[tuple[Settings, Path, dict[str, object]]] = []

    def operate(settings: Settings, path: Path, theme: PrototypeTheme, **kwargs: object) -> int:
        received.append((settings, path, kwargs))
        return 0

    module.run_operational = operate
    module.PrototypeError = RuntimeError
    monkeypatch.setitem(sys.modules, module.__name__, module)
    path = tmp_path / ".env"
    assert main(["--operate", "--windowed"], {"RFID_READER_NAME": "simulado"}, path) == 0
    assert received[0][0].reader_name == "simulado"
    assert received[0][1] == path
    assert received[0][2] == {"windowed": True, "size": (1366, 768), "initial_page": "start"}
    assert not path.exists()
