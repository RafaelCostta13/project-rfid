from rfid_reader.domain import TagLookupStatus
from rfid_reader.ui.qt.simulation import simulated_result


def test_simulated_results_are_unique_valid_and_classified() -> None:
    found = simulated_result(1, extra_box=False)
    extra = simulated_result(2, extra_box=True)

    assert found.epc == "424D57000000000000000001"
    assert found.epc != extra.epc
    assert found.status is TagLookupStatus.FOUND
    assert extra.status is TagLookupStatus.EXTRA_BOX
    assert found.supplier == "BMW do Brasil Ltda"
