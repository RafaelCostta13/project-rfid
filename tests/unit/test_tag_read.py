from datetime import UTC, datetime

import pytest

from rfid_reader.domain import TagRead


def test_creates_tag_read_with_aware_utc_timestamp() -> None:
    read_at = datetime.now(UTC)

    tag = TagRead(
        epc="E28011700001",
        reader_id="fx9600-test",
        antenna_id=1,
        read_at=read_at,
    )

    assert tag.epc == "E28011700001"
    assert tag.read_at is read_at


def test_rejects_naive_timestamp() -> None:
    with pytest.raises(ValueError, match="UTC"):
        TagRead(
            epc="E28011700001",
            reader_id="fx9600-test",
            antenna_id=1,
            read_at=datetime.now(),
        )
