from rfid_reader.ui.components import PAGE_NAMES
from rfid_reader.ui.navigation import NavigationState, PageId


def test_system_status_is_the_initial_page() -> None:
    navigation = NavigationState()

    assert navigation.current_page is PageId.SYSTEM_STATUS
    assert PAGE_NAMES[navigation.current_page] == "Start"


def test_select_changes_only_the_current_page() -> None:
    navigation = NavigationState()

    assert navigation.select(PageId.RFID_SETTINGS)
    assert navigation.current_page is PageId.RFID_SETTINGS


def test_select_current_page_is_idempotent() -> None:
    navigation = NavigationState(PageId.RFID_SETTINGS)

    assert not navigation.select(PageId.RFID_SETTINGS)
    assert navigation.current_page is PageId.RFID_SETTINGS
