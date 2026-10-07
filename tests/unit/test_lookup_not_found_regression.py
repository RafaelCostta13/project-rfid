from rfid_reader.domain import TagLookupResult, TagLookupSessionSummary, TagLookupStatus


def test_not_found_result_is_not_accepted_by_found_collection() -> None:
    summary = TagLookupSessionSummary()
    result = TagLookupResult("AAA1", TagLookupStatus.NOT_FOUND, "EPC nao localizado")

    assert not summary.update(result)
    assert summary.total == 0
