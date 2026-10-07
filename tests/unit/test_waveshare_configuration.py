import threading
import time
from collections.abc import Callable
from pathlib import Path

import pytest
from dotenv import dotenv_values

from rfid_reader.config import Settings, load_config
from rfid_reader.domain import (
    WaveshareConfigurationAction,
    WaveshareConfigurationFeedback,
    WaveshareConfigurationOutcome,
    WaveshareConnectionSettings,
)
from rfid_reader.integrations.waveshare_modbus import (
    WavesharePortBusyError,
    WavesharePortOpenError,
    WaveshareProtocolError,
    WaveshareTimeoutError,
)
from rfid_reader.services.waveshare_configuration import (
    DotEnvWaveshareConfigurationStore,
    WaveshareConfigurationService,
    WaveshareConfigurationWriteError,
)


def application_settings() -> Settings:
    return Settings(
        reader_host="192.168.0.214",
        reader_port=5084,
        reader_name="reader",
        antennas=(1,),
        deduplication_window_seconds=2.0,
        connection_timeout_seconds=3.0,
        status_check_interval_seconds=5.0,
        sharepoint_sync_url="https://example.test/sync",
        sharepoint_sync_timeout_seconds=10.0,
        tag_lookup_queue_size=100,
        local_database_path=Path("local.sqlite3"),
        log_level="INFO",
    )


def wait_until(predicate: Callable[[], bool], timeout: float = 1.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.005)
    raise AssertionError("condição assíncrona não foi atendida")


class RecordingStore:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.saved: list[WaveshareConnectionSettings] = []

    def save(self, settings: WaveshareConnectionSettings) -> None:
        if self.fail:
            raise WaveshareConfigurationWriteError("falha simulada")
        self.saved.append(settings)


class FakeTester:
    def __init__(
        self,
        error: Exception | None = None,
        started: threading.Event | None = None,
        release: threading.Event | None = None,
    ) -> None:
        self.error = error
        self.started = started
        self.release = release
        self.tested: list[WaveshareConnectionSettings] = []

    def test(self, settings: WaveshareConnectionSettings) -> None:
        self.tested.append(settings)
        if self.started is not None:
            self.started.set()
        if self.release is not None:
            assert self.release.wait(1.0)
        if self.error is not None:
            raise self.error


def form_values(port: str = "COM5") -> tuple[str, str, str, str, str, str]:
    return port, "9600", "8", "None", "1", "1"


def test_dotenv_store_preserves_other_keys_and_persists_all_values(tmp_path: Path) -> None:
    path = tmp_path / ".env"
    path.write_text(
        "RFID_READER_HOST=192.168.0.214\nSHAREPOINT_SYNC_URL=https://secret.test/?sig=secret\n",
        encoding="utf-8",
    )

    DotEnvWaveshareConfigurationStore(path).save(
        WaveshareConnectionSettings("COM10", 19200, 7, "Even", 2, 15)
    )

    assert dotenv_values(path) == {
        "RFID_READER_HOST": "192.168.0.214",
        "SHAREPOINT_SYNC_URL": "https://secret.test/?sig=secret",
        "WAVESHARE_SERIAL_PORT": "COM10",
        "WAVESHARE_BAUD_RATE": "19200",
        "WAVESHARE_DATA_BITS": "7",
        "WAVESHARE_PARITY": "Even",
        "WAVESHARE_STOP_BITS": "2",
        "WAVESHARE_DEVICE_ID": "15",
    }
    persisted = {key: value for key, value in dotenv_values(path).items() if value is not None}
    assert load_config(persisted).waveshare_connection == WaveshareConnectionSettings(
        "COM10", 19200, 7, "Even", 2, 15
    )


def test_dotenv_store_allows_empty_serial_port(tmp_path: Path) -> None:
    path = tmp_path / ".env"

    DotEnvWaveshareConfigurationStore(path).save(
        WaveshareConnectionSettings("", 9600, 8, "None", 1, 1)
    )

    assert dotenv_values(path)["WAVESHARE_SERIAL_PORT"] == ""


def test_save_updates_store_and_memory_without_testing_connection() -> None:
    store = RecordingStore()
    tester = FakeTester()
    events: list[WaveshareConfigurationFeedback] = []
    service = WaveshareConfigurationService(application_settings(), store, tester, events.append)

    assert service.save(*form_values(" COM5 "))

    expected = WaveshareConnectionSettings("COM5", 9600, 8, "None", 1, 1)
    assert store.saved == [expected]
    assert service.current() == expected
    assert tester.tested == []
    assert events[-1].action is WaveshareConfigurationAction.SAVE
    assert events[-1].outcome is WaveshareConfigurationOutcome.SUCCESS
    assert events[-1].settings == expected


def test_save_failure_does_not_change_memory() -> None:
    events: list[WaveshareConfigurationFeedback] = []
    service = WaveshareConfigurationService(
        application_settings(),
        RecordingStore(fail=True),
        FakeTester(),
        events.append,
    )

    assert not service.save(*form_values())
    assert service.current().serial_port == ""
    assert events[-1].outcome is WaveshareConfigurationOutcome.ERROR


def test_connection_uses_form_values_without_saving() -> None:
    store = RecordingStore()
    tester = FakeTester()
    events: list[WaveshareConfigurationFeedback] = []
    service = WaveshareConfigurationService(application_settings(), store, tester, events.append)
    try:
        assert service.test_connection(" COM10 ", "19200", "7", "Even", "2", "15")
        wait_until(lambda: len(events) == 2)

        assert tester.tested == [WaveshareConnectionSettings("COM10", 19200, 7, "Even", 2, 15)]
        assert store.saved == []
        assert service.current().serial_port == ""
        assert [event.outcome for event in events] == [
            WaveshareConfigurationOutcome.IN_PROGRESS,
            WaveshareConfigurationOutcome.SUCCESS,
        ]
    finally:
        service.close()


def test_connection_without_port_does_not_start_tester() -> None:
    tester = FakeTester()
    events: list[WaveshareConfigurationFeedback] = []
    service = WaveshareConfigurationService(
        application_settings(),
        RecordingStore(),
        tester,
        events.append,
    )

    assert not service.test_connection(*form_values(""))
    assert tester.tested == []
    assert events[-1].message == "Informe a porta COM da Waveshare."


@pytest.mark.parametrize(
    ("error", "message"),
    [
        (WaveshareTimeoutError(), "Não foi possível conectar"),
        (WaveshareProtocolError(), "Não foi possível conectar"),
        (WavesharePortOpenError(), "Não foi possível abrir"),
        (WavesharePortBusyError(), "utilizada por outro processo"),
    ],
)
def test_connection_reports_expected_failures(error: Exception, message: str) -> None:
    events: list[WaveshareConfigurationFeedback] = []
    service = WaveshareConfigurationService(
        application_settings(),
        RecordingStore(),
        FakeTester(error),
        events.append,
    )
    try:
        assert service.test_connection(*form_values())
        wait_until(lambda: len(events) == 2)

        assert events[-1].outcome is WaveshareConfigurationOutcome.ERROR
        assert message in events[-1].message
    finally:
        service.close()


def test_prevents_simultaneous_connection_tests() -> None:
    started = threading.Event()
    release = threading.Event()
    tester = FakeTester(started=started, release=release)
    service = WaveshareConfigurationService(
        application_settings(),
        RecordingStore(),
        tester,
        lambda event: None,
    )
    try:
        assert service.test_connection(*form_values())
        assert started.wait(1.0)
        assert not service.test_connection(*form_values("COM10"))
        assert len(tester.tested) == 1
    finally:
        release.set()
        service.close()
