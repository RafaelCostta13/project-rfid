from rfid_reader.domain import TagLookupResult, TagLookupSessionSummary, TagLookupStatus


def result(epc: str, status: TagLookupStatus) -> TagLookupResult:
    return TagLookupResult(epc, status, status.value)


def test_summary_starts_with_zero_found_results() -> None:
    summary = TagLookupSessionSummary()

    assert summary.total == 0


def test_summary_accepts_only_found_results() -> None:
    summary = TagLookupSessionSummary()

    assert summary.update(result("EPC-FOUND-01", TagLookupStatus.FOUND))
    assert summary.update(result("EPC-FOUND-02", TagLookupStatus.FOUND))
    assert not summary.update(result("EPC-NOT-FOUND", TagLookupStatus.NOT_FOUND))
    assert not summary.update(result("EPC-CONSULTING", TagLookupStatus.CONSULTING))
    assert not summary.update(result("EPC-ERROR", TagLookupStatus.ERROR))

    assert summary.total == 2


def test_repeated_found_result_for_same_epc_does_not_duplicate_count() -> None:
    summary = TagLookupSessionSummary()

    summary.update(result("EPC-01", TagLookupStatus.FOUND))
    summary.update(result("EPC-01", TagLookupStatus.FOUND))
    summary.update(result("EPC-01", TagLookupStatus.FOUND))

    assert summary.total == 1


def test_non_found_updates_do_not_remove_confirmed_result() -> None:
    summary = TagLookupSessionSummary()
    summary.update(result("EPC-01", TagLookupStatus.FOUND))

    summary.update(result("EPC-01", TagLookupStatus.ERROR))
    summary.update(result("EPC-01", TagLookupStatus.NOT_FOUND))

    assert summary.total == 1


def test_different_internal_epcs_are_counted_independently() -> None:
    summary = TagLookupSessionSummary()

    summary.update(result("4550432D3031", TagLookupStatus.FOUND))
    summary.update(result("4550432D303100", TagLookupStatus.FOUND))

    assert summary.total == 2


def test_reset_discards_results_from_previous_session() -> None:
    summary = TagLookupSessionSummary()
    summary.update(result("EPC-FOUND", TagLookupStatus.FOUND))

    summary.reset()

    assert summary.total == 0
