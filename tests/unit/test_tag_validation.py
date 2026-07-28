import pytest

from rfid_reader.services.tag_validation import is_valid_epc


@pytest.mark.parametrize(
    "epc",
    [
        "484C44303130313237353835",
        "484c44303130313237353835",
        "FFFE",
        "00",
    ],
)
def test_accepts_structurally_valid_hexadecimal_epc(epc: str) -> None:
    assert is_valid_epc(epc)


@pytest.mark.parametrize("epc", ["", "ABC", "GG", "41-42", "41 42"])
def test_rejects_epc_outside_existing_hexadecimal_structure(epc: str) -> None:
    assert not is_valid_epc(epc)
