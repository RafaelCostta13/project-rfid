import logging

import pytest

from rfid_reader.services.tag_presentation import (
    INVALID_TAG_TEXT,
    NON_ASCII_TAG_TEXT,
    epc_hex_to_ascii,
)


def test_converts_epc_hex_to_ascii() -> None:
    assert epc_hex_to_ascii("484C44303130313237353835") == "HLD010127585"


def test_accepts_lowercase_hexadecimal() -> None:
    assert epc_hex_to_ascii("484c44303130313237353835") == "HLD010127585"


@pytest.mark.parametrize("epc", ["", "ABC", "GG", "41-42", "41 42"])
def test_invalid_hexadecimal_has_safe_presentation(epc: str) -> None:
    assert epc_hex_to_ascii(epc) == INVALID_TAG_TEXT


def test_non_ascii_bytes_have_distinct_safe_presentation() -> None:
    assert epc_hex_to_ascii("FFFE") == NON_ASCII_TAG_TEXT


@pytest.mark.parametrize("epc", ["41420A", "410942", "410042", "2020"])
def test_control_or_empty_ascii_is_not_rendered(epc: str) -> None:
    assert epc_hex_to_ascii(epc) == INVALID_TAG_TEXT


def test_only_trims_leading_and_trailing_ascii_spaces() -> None:
    assert epc_hex_to_ascii("2041204220") == "A B"


def test_conversion_error_is_logged_with_original_epc(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.WARNING):
        result = epc_hex_to_ascii("ABC")

    assert result == INVALID_TAG_TEXT
    assert "epc=ABC" in caplog.text
