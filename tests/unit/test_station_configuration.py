from pathlib import Path

import pytest
from dotenv import dotenv_values

from rfid_reader.config import ConfigurationError, load_config, validate_station_dock
from rfid_reader.domain import ReaderConnectionSettings, WaveshareConnectionSettings
from rfid_reader.services.reader_configuration import DotEnvReaderConfigurationStore
from rfid_reader.services.station_configuration import StationConfigurationService
from rfid_reader.services.waveshare_configuration import DotEnvWaveshareConfigurationStore


def test_saves_reloads_changes_and_clears_dock_preserving_configuration(tmp_path: Path) -> None:
    path = tmp_path / ".env"
    original = (
        b"# configuracao\r\nSHAREPOINT_SYNC_URL=https://example.test/?sig=private\r\n"
        b"RFID_READER_HOST=reader.local\r\nWAVESHARE_SERIAL_PORT=COM3\r\n"
        b"export RFID_STATION_DOCK = D02\r\nRFID_STATION_DOCK=D03\r\n"
    )
    path.write_bytes(original)
    settings = load_config({"SHAREPOINT_SYNC_URL": "https://example.test"})
    store = DotEnvReaderConfigurationStore(path)
    station = StationConfigurationService(settings, store)

    for value in ("D01", "D05", ""):
        feedback = station.save(value)
        assert feedback.success
        assert station.current() == value
        persisted = {key: value for key, value in dotenv_values(path).items() if value is not None}
        reloaded = StationConfigurationService(load_config(persisted), store)
        assert reloaded.current() == value
        assert path.read_bytes().startswith(original.split(b"export")[0])
        assert b"\r\n" in path.read_bytes()


def test_device_saves_and_station_saves_preserve_each_other(tmp_path: Path) -> None:
    path = tmp_path / ".env"
    settings = load_config({"SHAREPOINT_SYNC_URL": "https://example.test"})
    store = DotEnvReaderConfigurationStore(path)
    station = StationConfigurationService(settings, store)
    assert station.save("D05").success
    store.save(ReaderConnectionSettings("Reader", "reader.local", 5084))
    DotEnvWaveshareConfigurationStore(path).save(
        WaveshareConnectionSettings("COM5", 9600, 8, "None", 1, 1)
    )
    assert dotenv_values(path)["RFID_STATION_DOCK"] == "D05"
    assert station.save("D01").success
    assert dotenv_values(path)["WAVESHARE_SERIAL_PORT"] == "COM5"
    assert dotenv_values(path)["RFID_READER_HOST"] == "reader.local"


def test_missing_dock_has_no_silent_default() -> None:
    settings = load_config({"SHAREPOINT_SYNC_URL": "https://example.test"})
    assert settings.station_dock == ""
    assert validate_station_dock(" d10 ") == "D10"


@pytest.mark.parametrize("value", ["D 01", "D01\nD02", "${TOKEN}", "x" * 33, 'D"01'])
def test_rejects_invalid_dock_without_writing(tmp_path: Path, value: str) -> None:
    path = tmp_path / ".env"
    settings = load_config({"SHAREPOINT_SYNC_URL": "https://example.test"})
    station = StationConfigurationService(settings, DotEnvReaderConfigurationStore(path))
    assert not station.save(value).success
    assert station.current() == ""
    assert not path.exists()
    with pytest.raises(ConfigurationError, match="RFID_STATION_DOCK"):
        load_config({"SHAREPOINT_SYNC_URL": "https://example.test", "RFID_STATION_DOCK": value})


def test_write_failure_preserves_file_and_memory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import rfid_reader.services.reader_configuration as persistence

    path = tmp_path / ".env"
    settings = load_config({"SHAREPOINT_SYNC_URL": "https://example.test"})
    station = StationConfigurationService(settings, DotEnvReaderConfigurationStore(path))
    assert station.save("D01").success
    original = path.read_bytes()

    def fail_replace(*args: object) -> None:
        raise PermissionError("simulated")

    monkeypatch.setattr(persistence.os, "replace", fail_replace)
    assert not station.save("D05").success
    assert station.current() == "D01"
    assert path.read_bytes() == original
    assert list(tmp_path.iterdir()) == [path]


@pytest.mark.parametrize(
    ("variable", "value"),
    [
        ("SYNC_CHECK_INTERVAL_SECONDS", "1"),
        ("SYNC_CHECK_INTERVAL_SECONDS", "nan"),
    ],
)
def test_validates_health_check_configuration(variable: str, value: str) -> None:
    with pytest.raises(ConfigurationError, match=variable):
        load_config({"SHAREPOINT_SYNC_URL": "https://example.test", variable: value})
