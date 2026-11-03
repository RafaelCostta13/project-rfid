from pathlib import Path

import pytest

from rfid_reader.config import ConfigurationError, load_config
from rfid_reader.services.epc_filter import (
    DEFAULT_EPC_PREFIXES,
    EpcFilterConfigurationService,
    EpcFilterState,
    EpcFilterValidationError,
    normalize_epc_prefix,
    parse_epc_prefixes,
)


class Store:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}

    def save_values(self, values: dict[str, str]) -> None:
        self.values.update(values)


def test_authorizes_only_exact_normalized_prefixes() -> None:
    state = EpcFilterState(True, DEFAULT_EPC_PREFIXES)

    assert state.allows("484c443034303132")
    assert not state.allows("31484C443034303132")
    assert not state.allows("484C4")


def test_disabled_filter_allows_valid_epcs() -> None:
    assert EpcFilterState(False, ()).allows("313233343536")


@pytest.mark.parametrize("value", ["484C4", "484C444", "ZZZZZZ", ""])
def test_rejects_invalid_prefix(value: str) -> None:
    with pytest.raises(EpcFilterValidationError):
        normalize_epc_prefix(value)


def test_rejects_duplicate_prefixes() -> None:
    with pytest.raises(EpcFilterValidationError, match="duplicado"):
        parse_epc_prefixes("484C44,484c44")


def test_configuration_save_preserves_snapshot_until_next_session() -> None:
    settings = load_config({"LOCALAPPDATA": "C:/Users/test/AppData/Local"})
    store = Store()
    service = EpcFilterConfigurationService(settings, store)
    old = service.current()

    service.save(True, ["313233"])

    assert old.allows("484C44000000")
    assert not old.allows("313233000000")
    assert service.current().allows("313233000000")
    assert store.values["RFID_EPC_ALLOWED_PREFIXES"] == "313233"


def test_enabled_empty_configuration_is_rejected() -> None:
    with pytest.raises(ConfigurationError, match="RFID_EPC_ALLOWED_PREFIXES"):
        load_config(
            {
                "LOCALAPPDATA": str(Path("C:/Users/test/AppData/Local")),
                "RFID_EPC_FILTER_ENABLED": "true",
                "RFID_EPC_ALLOWED_PREFIXES": "",
            }
        )
