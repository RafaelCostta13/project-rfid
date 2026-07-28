import queue

from rfid_reader.domain import (
    InventoryCleared,
    InventoryEvent,
    InventoryStatus,
    InventoryStatusChanged,
    TagLookupChanged,
    TagLookupEvent,
    TagLookupKey,
    TagLookupResult,
    TagLookupSessionStarted,
    TagLookupSessionSummary,
    TagLookupStatus,
)
from rfid_reader.ui.main_window import MainWindow


class RecordingStatusPage:
    def __init__(self) -> None:
        self.clears = 0
        self.summaries: list[int] = []
        self.rows: dict[str, TagLookupResult] = {}
        self.inventory_statuses: list[InventoryStatus] = []

    def clear_tags(self) -> None:
        self.clears += 1
        self.rows.clear()

    def set_summary(self, found: int) -> None:
        self.summaries.append(found)

    def set_tag_lookup(self, result: TagLookupResult) -> None:
        self.rows[result.epc] = result

    def set_inventory_status(self, status: InventoryStatus) -> None:
        self.inventory_statuses.append(status)


def lookup_event(
    session_id: int,
    epc: str,
    status: TagLookupStatus,
    *,
    antenna_id: int = 1,
) -> TagLookupChanged:
    return TagLookupChanged(
        session_id,
        TagLookupKey("reader-01", antenna_id, epc),
        TagLookupResult(epc, status, status.value, customer=f"Cliente {epc}"),
    )


def window_without_tk() -> tuple[
    MainWindow,
    queue.SimpleQueue[InventoryEvent],
    queue.SimpleQueue[TagLookupEvent],
    RecordingStatusPage,
]:
    window = object.__new__(MainWindow)
    inventory_updates: queue.SimpleQueue[InventoryEvent] = queue.SimpleQueue()
    lookup_updates: queue.SimpleQueue[TagLookupEvent] = queue.SimpleQueue()
    page = RecordingStatusPage()
    window._inventory_updates = inventory_updates
    window._lookup_updates = lookup_updates
    window._lookup_session_id = 0
    window._lookup_summary = TagLookupSessionSummary()
    window._status_page = page
    return window, inventory_updates, lookup_updates, page


def test_mixed_lookup_events_display_and_count_only_found_results() -> None:
    window, _, updates, page = window_without_tk()
    updates.put(TagLookupSessionStarted(1))
    updates.put(lookup_event(1, "EPC-A", TagLookupStatus.FOUND))
    updates.put(lookup_event(1, "EPC-B", TagLookupStatus.NOT_FOUND))
    updates.put(lookup_event(1, "EPC-C", TagLookupStatus.CONSULTING))
    updates.put(lookup_event(1, "EPC-D", TagLookupStatus.ERROR))
    updates.put(lookup_event(1, "EPC-E", TagLookupStatus.FOUND))

    window._drain_lookup_updates()

    assert page.summaries == [0, 1, 2]
    assert set(page.rows) == {"EPC-A", "EPC-E"}
    assert all(result.status is TagLookupStatus.FOUND for result in page.rows.values())


def test_same_epc_from_different_keys_has_one_row_and_one_count() -> None:
    window, _, updates, page = window_without_tk()
    updates.put(TagLookupSessionStarted(1))
    updates.put(lookup_event(1, "EPC-01", TagLookupStatus.FOUND, antenna_id=1))
    updates.put(lookup_event(1, "EPC-01", TagLookupStatus.FOUND, antenna_id=2))

    window._drain_lookup_updates()

    assert page.summaries[-1] == 1
    assert list(page.rows) == ["EPC-01"]


def test_new_session_resets_card_and_ignores_old_results() -> None:
    window, _, updates, page = window_without_tk()
    updates.put(TagLookupSessionStarted(1))
    updates.put(lookup_event(1, "EPC-OLD", TagLookupStatus.FOUND))
    updates.put(TagLookupSessionStarted(2))
    updates.put(lookup_event(1, "EPC-STALE", TagLookupStatus.FOUND))

    window._drain_lookup_updates()

    assert page.summaries[-1] == 0
    assert page.rows == {}


def test_inventory_clear_resets_card_but_stop_preserves_it() -> None:
    window, inventory_updates, lookup_updates, page = window_without_tk()
    lookup_updates.put(TagLookupSessionStarted(1))
    lookup_updates.put(lookup_event(1, "EPC-01", TagLookupStatus.FOUND))
    window._drain_lookup_updates()

    inventory_updates.put(InventoryStatusChanged(InventoryStatus.STOPPED))
    window._drain_inventory_updates()
    assert page.summaries[-1] == 1

    inventory_updates.put(InventoryCleared())
    window._drain_inventory_updates()
    assert page.summaries[-1] == 0
