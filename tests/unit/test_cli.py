import socket

import pytest

from rfid_reader.cli import main


def valid_environment() -> dict[str, str]:
    return {
        "RFID_READER_HOST": "reader.local",
        "RFID_READER_PORT": "5084",
        "RFID_READER_NAME": "fx9600-test",
        "RFID_ANTENNAS": "1,2",
        "RFID_DEDUPLICATION_WINDOW_SECONDS": "2.0",
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
