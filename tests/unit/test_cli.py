import socket

import pytest

from rfid_reader import cli
from rfid_reader.cli import main
from rfid_reader.config import Settings


def valid_environment() -> dict[str, str]:
    return {
        "RFID_READER_HOST": "reader.local",
        "RFID_READER_PORT": "5084",
        "RFID_READER_NAME": "fx9600-test",
        "RFID_ANTENNAS": "1,2",
        "RFID_DEDUPLICATION_WINDOW_SECONDS": "2.0",
        "SHAREPOINT_LOOKUP_URL": "https://example.test/lookup",
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
    exit_code = main(["check-config"], {})

    assert exit_code != 0
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "RFID_READER_HOST" in captured.err


def test_check_config_does_not_access_network(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_if_called(*args: object, **kwargs: object) -> None:
        raise AssertionError("check-config não deve acessar a rede")

    monkeypatch.setattr(socket, "create_connection", fail_if_called)

    assert main(["check-config"], valid_environment()) == 0


def test_show_opens_application_with_validated_settings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    received: list[Settings] = []

    def fake_run_application(settings: Settings) -> None:
        received.append(settings)

    monkeypatch.setattr(cli, "run_application", fake_run_application)

    assert main(["show"], valid_environment()) == 0
    assert received[0].reader_host == "reader.local"


def test_show_reports_application_start_error(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def fail_to_start(settings: Settings) -> None:
        raise cli.ApplicationError("interface indisponível")

    monkeypatch.setattr(cli, "run_application", fail_to_start)

    assert main(["show"], valid_environment()) == 1
    assert "interface indisponível" in capsys.readouterr().err
