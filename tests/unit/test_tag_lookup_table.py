from rfid_reader.domain import InventoryStatus, TagLookupResult, TagLookupStatus
from rfid_reader.ui.pages import (
    START_PAGE_TITLE,
    SUMMARY_CARD_TITLE,
    TAG_TABLE_COLUMNS,
    TAG_TABLE_HEADINGS,
    SystemStatusPage,
    tag_lookup_values,
)


class RecordingLabel:
    def __init__(self) -> None:
        self.text = ""

    def configure(self, *, text: str) -> None:
        self.text = text


class RecordingTable:
    def __init__(self) -> None:
        self.insertions: list[str] = []
        self.updates: list[str] = []

    def insert(
        self,
        parent: str,
        index: str,
        *,
        iid: str,
        values: tuple[str, ...],
        tags: tuple[str, ...],
    ) -> None:
        self.insertions.append(iid)

    def item(
        self,
        iid: str,
        *,
        values: tuple[str, ...],
        tags: tuple[str, ...],
    ) -> None:
        self.updates.append(iid)

    def see(self, iid: str) -> None:
        pass


class RecordingWidget:
    def __init__(self) -> None:
        self.options: dict[str, str] = {}

    def configure(self, **options: str) -> None:
        self.options.update(options)


def test_start_page_exposes_only_found_summary_card() -> None:
    assert START_PAGE_TITLE == "Start"
    assert SUMMARY_CARD_TITLE == "EPCs encontrados"


def test_summary_label_renders_found_total() -> None:
    page = object.__new__(SystemStatusPage)
    found_label = RecordingLabel()
    page._found_count_label = found_label

    page.set_summary(15)

    assert found_label.text == "15"


def test_table_removes_tag_and_keeps_remaining_columns_in_exact_order() -> None:
    assert TAG_TABLE_COLUMNS == (
        "status",
        "customer",
        "invoice_number",
        "volume",
        "order_number",
        "dock",
    )
    assert tuple(heading for column, heading in TAG_TABLE_HEADINGS) == (
        "Status",
        "Cliente",
        "Nota fiscal",
        "Volume",
        "Pedido",
        "Doca",
    )


def test_found_row_uses_normalized_model_and_not_the_diagnostic_message() -> None:
    result = TagLookupResult(
        epc="484C443031",
        status=TagLookupStatus.FOUND,
        message="Mensagem mantida apenas no modelo",
        customer="Cliente 01",
        invoice_number="00127",
        order_number="00099",
        volume="1/2",
        dock="D04",
    )

    assert result.message == "Mensagem mantida apenas no modelo"
    assert tag_lookup_values(result) == (
        "Encontrada",
        "Cliente 01",
        "00127",
        "1/2",
        "00099",
        "D04",
    )


def test_epc_remains_internal_and_is_not_part_of_visual_values() -> None:
    epc = "484C44303130313237353835"
    result = TagLookupResult(
        epc,
        TagLookupStatus.FOUND,
        "Encontrada",
    )

    assert result.epc == epc
    assert epc not in tag_lookup_values(result)


def test_repeated_found_epc_updates_one_visual_row() -> None:
    page = object.__new__(SystemStatusPage)
    table = RecordingTable()
    page._tag_table = table
    page._tag_rows = {}
    page._next_tag_row = 0
    first = TagLookupResult(
        "484C443031",
        TagLookupStatus.FOUND,
        "Encontrada",
        customer="Cliente inicial",
    )
    updated = TagLookupResult(
        "484C443031",
        TagLookupStatus.FOUND,
        "Encontrada",
        customer="Cliente atualizado",
    )

    page.set_tag_lookup(first)
    page.set_tag_lookup(updated)

    assert table.insertions == ["tag-1"]
    assert table.updates == ["tag-1"]
    assert page._tag_rows == {"484C443031": "tag-1"}


def test_automatic_mode_keeps_stop_available_while_waiting_for_di1() -> None:
    page = object.__new__(SystemStatusPage)
    page._automatic_enabled = False
    page._inventory_status = InventoryStatus.STOPPED
    page._inventory_status_label = RecordingWidget()
    page._start_button = RecordingWidget()
    page._stop_button = RecordingWidget()

    page.set_automatic_enabled(True)

    assert page._start_button.options["state"] == "disabled"
    assert page._stop_button.options["state"] == "normal"
    page.set_inventory_status(InventoryStatus.READING)
    page.set_automatic_enabled(False)
    assert page._stop_button.options["state"] == "normal"
    page.set_inventory_status(InventoryStatus.STOPPED)
    assert page._start_button.options["state"] == "normal"
    assert page._stop_button.options["state"] == "disabled"
