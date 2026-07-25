import pytest

from rfid_reader.config import ConfigurationError, Settings, load_config


def valid_environment() -> dict[str, str]:
    return {
        "RFID_READER_HOST": "192.168.0.100",
        "RFID_READER_PORT": "5084",
        "RFID_READER_NAME": "fx9600-01",
        "RFID_ANTENNAS": "1",
        "RFID_DEDUPLICATION_WINDOW_SECONDS": "2.5",
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
        log_level="INFO",
    )


def test_loads_multiple_antennas_and_normalizes_duplicates() -> None:
    environment = valid_environment()
    environment["RFID_ANTENNAS"] = "1, 2,1,4"

    settings = load_config(environment)

    assert settings.antennas == (1, 2, 4)


def test_uses_defaults_for_optional_values() -> None:
    settings = load_config({"RFID_READER_HOST": "reader.local"})

    assert settings.reader_port == 5084
    assert settings.reader_name == "fx9600-01"
    assert settings.antennas == (1,)
    assert settings.deduplication_window_seconds == 2.0
    assert settings.connection_timeout_seconds == 3.0
    assert settings.status_check_interval_seconds == 5.0
    assert settings.log_level == "INFO"


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
