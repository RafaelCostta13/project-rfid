import threading
import time
from collections.abc import Callable
from pathlib import Path

import pytest
from dotenv import dotenv_values

from rfid_reader.config import Settings
from rfid_reader.domain import (
    ReaderConfigurationAction,
    ReaderConfigurationFeedback,
    ReaderConfigurationOutcome,
    ReaderConnectionSettings,
)
from rfid_reader.readers.base import (
    DisconnectCallback,
    ReaderConnectionError,
    ReaderTimeoutError,
    TagCallback,
)
from rfid_reader.services import reader_configuration
from rfid_reader.services.reader_configuration import (
    DotEnvReaderConfigurationStore,
    ReaderConfigurationService,
    ReaderConfigurationWriteError,
)


def application_settings() -> Settings:
    return Settings(
        reader_host="192.168.0.100",
        reader_port=5084,
        reader_name="reader-original",
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
        self.saved: list[ReaderConnectionSettings] = []

    def save(self, settings: ReaderConnectionSettings) -> None:
        if self.fail:
            raise ReaderConfigurationWriteError("falha simulada")
        self.saved.append(settings)


class RecordingConfigurer:
    def __init__(self) -> None:
        self.configurations: list[ReaderConnectionSettings] = []

    def configure_connection(self, host: str, port: int, reader_id: str) -> None:
        self.configurations.append(ReaderConnectionSettings(reader_id, host, port))


class FakeTemporaryReader:
    def __init__(
        self,
        *,
        connect_error: Exception | None = None,
        connect_started: threading.Event | None = None,
        connect_release: threading.Event | None = None,
        disconnect_error: Exception | None = None,
    ) -> None:
        self._connect_error = connect_error
        self._connect_started = connect_started
        self._connect_release = connect_release
        self._disconnect_error = disconnect_error
        self.connected = False
        self.connect_calls = 0
        self.disconnect_calls = 0
        self.start_inventory_calls = 0

    def connect(self) -> None:
        self.connect_calls += 1
        if self._connect_started is not None:
            self._connect_started.set()
        if self._connect_release is not None:
            assert self._connect_release.wait(1.0)
        if self._connect_error is not None:
            raise self._connect_error
        self.connected = True

    def disconnect(self) -> None:
        self.disconnect_calls += 1
        self.connected = False
        if self._disconnect_error is not None:
            raise self._disconnect_error

    def is_connected(self) -> bool:
        return self.connected

    def start_inventory(self, callback: TagCallback) -> bool:
        self.start_inventory_calls += 1
        return False

    def stop_inventory(self) -> bool:
        return False

    def is_inventorying(self) -> bool:
        return False

    def set_disconnect_callback(self, callback: DisconnectCallback) -> None:
        return None


def test_dotenv_store_updates_only_reader_keys_and_preserves_crlf(tmp_path: Path) -> None:
    path = tmp_path / ".env"
    original = (
        b"# ambiente local\r\n"
        b"RFID_READER_HOST=192.168.0.100\r\n"
        b"export RFID_READER_PORT = 5000\r\n"
        b"SHAREPOINT_SYNC_URL=https://secret.example.test/?sig=secret\r\n"
        b"CUSTOM_VALUE=preservar\r\n"
    )
    path.write_bytes(original)
    store = DotEnvReaderConfigurationStore(path)

    store.save(ReaderConnectionSettings("Reader Doca 01", "192.168.0.214", 5084))

    content = path.read_bytes()
    assert b'RFID_READER_NAME="Reader Doca 01"\r\n' in content
    assert b'RFID_READER_HOST="192.168.0.214"\r\n' in content
    assert b"export RFID_READER_PORT =5084\r\n" in content
    assert b"SHAREPOINT_SYNC_URL=https://secret.example.test/?sig=secret\r\n" in content
    assert b"CUSTOM_VALUE=preservar\r\n" in content
    assert content.startswith(b"# ambiente local\r\n")


def test_dotenv_store_creates_missing_file_with_only_reader_keys(tmp_path: Path) -> None:
    path = tmp_path / ".env"

    DotEnvReaderConfigurationStore(path).save(
        ReaderConnectionSettings("Reader", "reader.local", 6000)
    )

    assert path.read_text(encoding="utf-8") == (
        'RFID_READER_NAME="Reader"\nRFID_READER_HOST="reader.local"\nRFID_READER_PORT=6000\n'
    )
    assert dotenv_values(path) == {
        "RFID_READER_NAME": "Reader",
        "RFID_READER_HOST": "reader.local",
        "RFID_READER_PORT": "6000",
    }


def test_dotenv_store_preserves_original_when_atomic_replace_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / ".env"
    original = "RFID_READER_HOST=192.168.0.100\nCUSTOM=preservar\n"
    path.write_text(original, encoding="utf-8")

    def fail_replace(source: Path, destination: Path) -> None:
        raise PermissionError("sem permissão")

    monkeypatch.setattr(reader_configuration.os, "replace", fail_replace)

    with pytest.raises(ReaderConfigurationWriteError):
        DotEnvReaderConfigurationStore(path).save(
            ReaderConnectionSettings("Reader", "192.168.0.214", 5084)
        )

    assert path.read_text(encoding="utf-8") == original
    assert list(tmp_path.glob("*.tmp")) == []


def test_dotenv_store_reports_invalid_encoding_without_replacing_file(tmp_path: Path) -> None:
    path = tmp_path / ".env"
    original = b"RFID_READER_HOST=\xff\n"
    path.write_bytes(original)

    with pytest.raises(ReaderConfigurationWriteError):
        DotEnvReaderConfigurationStore(path).save(
            ReaderConnectionSettings("Reader", "192.168.0.214", 5084)
        )

    assert path.read_bytes() == original


def test_save_updates_store_memory_and_next_reader_connection() -> None:
    store = RecordingStore()
    configurer = RecordingConfigurer()
    events: list[ReaderConfigurationFeedback] = []
    service = ReaderConfigurationService(
        application_settings(),
        store,
        configurer,
        lambda settings: FakeTemporaryReader(),
        lambda: False,
        events.append,
    )

    assert service.save("  Reader Novo  ", " 192.168.0.214 ", "6000")

    expected = ReaderConnectionSettings("Reader Novo", "192.168.0.214", 6000)
    assert store.saved == [expected]
    assert service.current() == expected
    assert configurer.configurations == [expected]
    assert events[-1].action is ReaderConfigurationAction.SAVE
    assert events[-1].outcome is ReaderConfigurationOutcome.SUCCESS
    assert events[-1].settings == expected


def test_invalid_or_failed_save_does_not_change_memory_or_reader() -> None:
    for store, port in ((RecordingStore(), "invalid"), (RecordingStore(fail=True), "5084")):
        configurer = RecordingConfigurer()
        events: list[ReaderConfigurationFeedback] = []
        service = ReaderConfigurationService(
            application_settings(),
            store,
            configurer,
            lambda settings: FakeTemporaryReader(),
            lambda: False,
            events.append,
        )

        assert not service.save("Reader Novo", "192.168.0.214", port)
        assert service.current() == application_settings().reader_connection
        assert configurer.configurations == []
        assert events[-1].outcome is ReaderConfigurationOutcome.ERROR


def test_temporary_test_uses_form_values_without_saving_or_starting_inventory() -> None:
    store = RecordingStore()
    configurer = RecordingConfigurer()
    events: list[ReaderConfigurationFeedback] = []
    configurations: list[ReaderConnectionSettings] = []
    readers: list[FakeTemporaryReader] = []

    def factory(settings: ReaderConnectionSettings) -> FakeTemporaryReader:
        configurations.append(settings)
        reader = FakeTemporaryReader()
        readers.append(reader)
        return reader

    service = ReaderConfigurationService(
        application_settings(),
        store,
        configurer,
        factory,
        lambda: False,
        events.append,
    )
    try:
        assert service.test_connection("Reader Teste", "reader-teste", "6000")
        wait_until(lambda: len(events) == 2)

        assert configurations == [ReaderConnectionSettings("Reader Teste", "reader-teste", 6000)]
        assert [event.outcome for event in events] == [
            ReaderConfigurationOutcome.IN_PROGRESS,
            ReaderConfigurationOutcome.SUCCESS,
        ]
        assert readers[0].connect_calls == 1
        assert readers[0].disconnect_calls == 1
        assert readers[0].start_inventory_calls == 0
        assert store.saved == []
        assert configurer.configurations == []
        assert service.current() == application_settings().reader_connection
    finally:
        service.close()


@pytest.mark.parametrize(
    ("error", "message"),
    [
        (ReaderTimeoutError("timeout"), "Tempo limite"),
        (ReaderConnectionError("recusada"), "Não foi possível"),
    ],
)
def test_temporary_test_reports_friendly_failure_and_disconnects(
    error: Exception,
    message: str,
) -> None:
    events: list[ReaderConfigurationFeedback] = []
    reader = FakeTemporaryReader(connect_error=error)
    service = ReaderConfigurationService(
        application_settings(),
        RecordingStore(),
        RecordingConfigurer(),
        lambda settings: reader,
        lambda: False,
        events.append,
    )
    try:
        assert service.test_connection("Reader", "192.168.0.214", "5084")
        wait_until(lambda: len(events) == 2)

        assert events[-1].outcome is ReaderConfigurationOutcome.ERROR
        assert message in events[-1].message
        assert reader.disconnect_calls == 1
        assert reader.start_inventory_calls == 0
    finally:
        service.close()


def test_inventory_active_blocks_temporary_connection() -> None:
    events: list[ReaderConfigurationFeedback] = []
    factory_calls: list[ReaderConnectionSettings] = []

    def factory(settings: ReaderConnectionSettings) -> FakeTemporaryReader:
        factory_calls.append(settings)
        return FakeTemporaryReader()

    service = ReaderConfigurationService(
        application_settings(),
        RecordingStore(),
        RecordingConfigurer(),
        factory,
        lambda: True,
        events.append,
    )

    assert not service.test_connection("Reader", "192.168.0.214", "5084")
    assert factory_calls == []
    assert "Pare a leitura" in events[-1].message


def test_prevents_simultaneous_connection_tests() -> None:
    started = threading.Event()
    release = threading.Event()
    events: list[ReaderConfigurationFeedback] = []
    factory_calls = 0

    def factory(settings: ReaderConnectionSettings) -> FakeTemporaryReader:
        nonlocal factory_calls
        factory_calls += 1
        return FakeTemporaryReader(connect_started=started, connect_release=release)

    service = ReaderConfigurationService(
        application_settings(),
        RecordingStore(),
        RecordingConfigurer(),
        factory,
        lambda: False,
        events.append,
    )
    try:
        assert service.test_connection("Reader", "192.168.0.214", "5084")
        assert started.wait(1.0)

        assert not service.test_connection("Outro", "192.168.0.215", "5085")
        assert factory_calls == 1
    finally:
        release.set()
        service.close()


def test_configuration_only_service_saves_without_creating_a_reader() -> None:
    store = RecordingStore()
    events: list[ReaderConfigurationFeedback] = []
    service = ReaderConfigurationService(
        application_settings(), store, None, None, lambda: False, events.append
    )
    try:
        assert service.save("Reader local", "reader.local", "6000")
        assert service.current() == ReaderConnectionSettings("Reader local", "reader.local", 6000)
        assert store.saved == [service.current()]
        assert not service.test_connection("Reader local", "reader.local", "6000")
        assert events[-1].outcome is ReaderConfigurationOutcome.ERROR
        assert "não integrado" in events[-1].message
    finally:
        service.close()
