import pytest

from rfid_reader.config import (
    ConfigurationError,
    ReaderConfigurationValidationError,
    Settings,
    WaveshareConfigurationValidationError,
    load_config,
    validate_reader_connection,
    validate_waveshare_connection,
)
from rfid_reader.domain import ReaderConnectionSettings, WaveshareConnectionSettings


def valid_environment() -> dict[str, str]:
    return {
        "RFID_READER_HOST": "192.168.0.100",
        "RFID_READER_PORT": "5084",
        "RFID_READER_NAME": "fx9600-01",
        "RFID_ANTENNAS": "1",
        "RFID_DEDUPLICATION_WINDOW_SECONDS": "2.5",
        "SHAREPOINT_SYNC_URL": "https://example.test/sync",
        "LOCALAPPDATA": "C:/Users/test/AppData/Local",
        "RFID_LOG_LEVEL": "INFO",
    }


def test_loads_complete_valid_configuration_and_converts_types() -> None:
    settings = load_config(valid_environment())

    assert settings == Settings(
        reader_host="192.168.0.100",
        reader_port=5084,
        reader_name="fx9600-01",
        antennas=(1,),
        deduplication_window_seconds=2.5,
        connection_timeout_seconds=3.0,
        status_check_interval_seconds=5.0,
        sharepoint_sync_url="https://example.test/sync",
        sharepoint_sync_timeout_seconds=10.0,
        tag_lookup_queue_size=100,
        local_database_path=settings.local_database_path,
        log_level="INFO",
    )


def test_loads_multiple_antennas_and_normalizes_duplicates() -> None:
    environment = valid_environment()
    environment["RFID_ANTENNAS"] = "1, 2,1,4"

    settings = load_config(environment)

    assert settings.antennas == (1, 2, 4)


def test_uses_defaults_for_optional_values() -> None:
    settings = load_config(
        {
            "SHAREPOINT_SYNC_URL": "https://example.test/sync",
            "LOCALAPPDATA": "C:/Users/test/AppData/Local",
        }
    )

    assert settings.reader_host == "192.168.0.214"
    assert settings.reader_port == 5084
    assert settings.reader_name == "fx9600-01"
    assert settings.antennas == (1,)
    assert settings.deduplication_window_seconds == 2.0
    assert settings.connection_timeout_seconds == 3.0
    assert settings.status_check_interval_seconds == 5.0
    assert settings.sharepoint_sync_timeout_seconds == 10.0
    assert settings.tag_lookup_queue_size == 100
    assert str(settings.local_database_path).endswith("rfid-reader.sqlite3")
    assert settings.log_level == "INFO"
    assert settings.waveshare_connection == WaveshareConnectionSettings(
        serial_port="",
        baud_rate=9600,
        data_bits=8,
        parity="None",
        stop_bits=1,
        device_id=1,
    )


def test_loads_persisted_waveshare_configuration() -> None:
    environment = valid_environment()
    environment.update(
        {
            "WAVESHARE_SERIAL_PORT": " COM10 ",
            "WAVESHARE_BAUD_RATE": "19200",
            "WAVESHARE_DATA_BITS": "7",
            "WAVESHARE_PARITY": "even",
            "WAVESHARE_STOP_BITS": "2",
            "WAVESHARE_DEVICE_ID": "15",
        }
    )

    settings = load_config(environment)

    assert settings.waveshare_connection == WaveshareConnectionSettings(
        serial_port="COM10",
        baud_rate=19200,
        data_bits=7,
        parity="Even",
        stop_bits=2,
        device_id=15,
    )


def test_validates_waveshare_form_and_allows_empty_port_for_save() -> None:
    assert validate_waveshare_connection(" ", "9600", "8", "none", "1", "1") == (
        WaveshareConnectionSettings("", 9600, 8, "None", 1, 1)
    )


def test_requires_waveshare_port_only_for_connection_test() -> None:
    with pytest.raises(WaveshareConfigurationValidationError, match="porta COM"):
        validate_waveshare_connection(
            "",
            "9600",
            "8",
            "None",
            "1",
            "1",
            require_serial_port=True,
        )


@pytest.mark.parametrize(
    ("values", "message"),
    [
        (("COM5", "0", "8", "None", "1", "1"), "Baud rate"),
        (("COM5", "9600", "9", "None", "1", "1"), "Data bits"),
        (("COM5", "9600", "8", "invalid", "1", "1"), "Paridade"),
        (("COM5", "9600", "8", "None", "3", "1"), "Stop bits"),
        (("COM5", "9600", "8", "None", "1", "248"), "Device ID"),
    ],
)
def test_rejects_invalid_waveshare_form_values(
    values: tuple[str, str, str, str, str, str],
    message: str,
) -> None:
    with pytest.raises(WaveshareConfigurationValidationError, match=message):
        validate_waveshare_connection(*values)


def test_invalid_persisted_waveshare_configuration_fails_with_variable_name() -> None:
    environment = valid_environment()
    environment["WAVESHARE_DEVICE_ID"] = "0"

    with pytest.raises(ConfigurationError, match="WAVESHARE_DEVICE_ID"):
        load_config(environment)


@pytest.mark.parametrize("host", ["", "   "])
def test_rejects_missing_or_empty_host(host: str) -> None:
    environment = valid_environment()
    environment["RFID_READER_HOST"] = host

    with pytest.raises(ConfigurationError, match="RFID_READER_HOST"):
        load_config(environment)


def test_rejects_non_numeric_port() -> None:
    environment = valid_environment()
    environment["RFID_READER_PORT"] = "not-a-port"

    with pytest.raises(ConfigurationError, match="RFID_READER_PORT"):
        load_config(environment)


@pytest.mark.parametrize("port", ["0", "65536"])
def test_rejects_port_outside_valid_range(port: str) -> None:
    environment = valid_environment()
    environment["RFID_READER_PORT"] = port

    with pytest.raises(ConfigurationError, match="RFID_READER_PORT"):
        load_config(environment)


@pytest.mark.parametrize("antennas", ["", "1,two", "0", "-1", "1,"])
def test_rejects_invalid_antenna_list(antennas: str) -> None:
    environment = valid_environment()
    environment["RFID_ANTENNAS"] = antennas

    with pytest.raises(ConfigurationError, match="RFID_ANTENNAS"):
        load_config(environment)


def test_rejects_negative_deduplication_window() -> None:
    environment = valid_environment()
    environment["RFID_DEDUPLICATION_WINDOW_SECONDS"] = "-0.1"

    with pytest.raises(ConfigurationError, match="RFID_DEDUPLICATION_WINDOW_SECONDS"):
        load_config(environment)


@pytest.mark.parametrize("window", ["not-a-number", "nan", "inf"])
def test_rejects_invalid_deduplication_window(window: str) -> None:
    environment = valid_environment()
    environment["RFID_DEDUPLICATION_WINDOW_SECONDS"] = window

    with pytest.raises(ConfigurationError, match="RFID_DEDUPLICATION_WINDOW_SECONDS"):
        load_config(environment)


def test_rejects_unknown_log_level() -> None:
    environment = valid_environment()
    environment["RFID_LOG_LEVEL"] = "VERBOSE"

    with pytest.raises(ConfigurationError, match="RFID_LOG_LEVEL"):
        load_config(environment)


def test_rejects_empty_reader_name() -> None:
    environment = valid_environment()
    environment["RFID_READER_NAME"] = " "

    with pytest.raises(ConfigurationError, match="RFID_READER_NAME"):
        load_config(environment)


def test_validates_and_normalizes_reader_form_fields() -> None:
    assert validate_reader_connection(
        "  Reader Doca 01  ",
        "  reader-doca-01  ",
        " 5084 ",
    ) == ReaderConnectionSettings(
        name="Reader Doca 01",
        host="reader-doca-01",
        port=5084,
    )


@pytest.mark.parametrize("name", ["", "   ", "Reader\nInjetado", "Reader ${INJETADO}"])
def test_rejects_invalid_reader_form_name(name: str) -> None:
    with pytest.raises(ReaderConfigurationValidationError, match="nome do reader"):
        validate_reader_connection(name, "192.168.0.214", "5084")


@pytest.mark.parametrize(
    "host",
    ["", " ", "192.168", "192.168.0.999", "-reader", "reader..local"],
)
def test_rejects_invalid_reader_form_host(host: str) -> None:
    with pytest.raises(ReaderConfigurationValidationError, match="endereço|IP|hostname"):
        validate_reader_connection("Reader", host, "5084")


@pytest.mark.parametrize("port", ["0", "65536", "abc", "5084.5", ""])
def test_rejects_invalid_reader_form_port(port: str) -> None:
    with pytest.raises(ReaderConfigurationValidationError, match="porta"):
        validate_reader_connection("Reader", "192.168.0.214", port)


@pytest.mark.parametrize(
    ("variable", "value"),
    [
        ("RFID_CONNECTION_TIMEOUT_SECONDS", "0"),
        ("RFID_CONNECTION_TIMEOUT_SECONDS", "invalid"),
        ("RFID_STATUS_CHECK_INTERVAL_SECONDS", "-1"),
        ("RFID_STATUS_CHECK_INTERVAL_SECONDS", "nan"),
    ],
)
def test_rejects_invalid_connection_timing(variable: str, value: str) -> None:
    environment = valid_environment()
    environment[variable] = value

    with pytest.raises(ConfigurationError, match=variable):
        load_config(environment)


@pytest.mark.parametrize(
    "url",
    ["not-a-url", "http://example.test/sync"],
)
def test_rejects_invalid_sharepoint_url_when_legacy_setting_is_used(url: str) -> None:
    environment = valid_environment()
    environment["SHAREPOINT_SYNC_URL"] = url

    with pytest.raises(ConfigurationError, match="SHAREPOINT_SYNC_URL"):
        load_config(environment)


def test_allows_missing_legacy_sharepoint_url_after_remote_cutover() -> None:
    environment = valid_environment()
    environment.pop("SHAREPOINT_SYNC_URL")

    assert load_config(environment).sharepoint_sync_url == ""


@pytest.mark.parametrize(
    ("variable", "value"),
    [
        ("SHAREPOINT_SYNC_TIMEOUT_SECONDS", "0"),
        ("SHAREPOINT_SYNC_TIMEOUT_SECONDS", "invalid"),
        ("TAG_LOOKUP_QUEUE_SIZE", "0"),
        ("TAG_LOOKUP_QUEUE_SIZE", "1.5"),
        ("SYNC_CHECK_INTERVAL_SECONDS", "1"),
        ("SYNC_CHECK_INTERVAL_SECONDS", "nan"),
    ],
)
def test_rejects_invalid_sharepoint_limits(variable: str, value: str) -> None:
    environment = valid_environment()
    environment[variable] = value

    with pytest.raises(ConfigurationError, match=variable):
        load_config(environment)
