from rfid_reader.domain import TagLookupResult, TagLookupStatus
from rfid_reader.ui.pages import TAG_TABLE_COLUMNS, TAG_TABLE_HEADINGS, tag_lookup_values


def test_table_has_required_columns_in_exact_order() -> None:
    assert TAG_TABLE_COLUMNS == (
        "tag",
        "status",
        "customer",
        "invoice_number",
        "volume",
        "order_number",
        "dock",
    )
    assert tuple(heading for column, heading in TAG_TABLE_HEADINGS) == (
        "Tag",
        "Status",
        "Cliente",
        "Nota fiscal",
        "Volume",
        "Pedido",
        "Doca",
    )


def test_consulting_row_keeps_additional_cells_empty() -> None:
    result = TagLookupResult(
        "484C44303130313237353835",
        TagLookupStatus.CONSULTING,
        "",
        tag="HLD010127585",
    )

    assert tag_lookup_values(result) == (
        "HLD010127585",
        "Consultando",
        "",
        "",
        "",
        "",
        "",
    )


def test_found_row_uses_normalized_model_and_not_the_diagnostic_message() -> None:
    result = TagLookupResult(
        epc="EPC-01",
        status=TagLookupStatus.FOUND,
        message="Mensagem mantida apenas no modelo",
        tag="TAG-01",
        customer="Cliente 01",
        invoice_number="00127",
        order_number="00099",
        volume="1/2",
        dock="D04",
    )

    assert result.message == "Mensagem mantida apenas no modelo"
    assert tag_lookup_values(result) == (
        "TAG-01",
        "Encontrada",
        "Cliente 01",
        "00127",
        "1/2",
        "00099",
        "D04",
    )


def test_error_row_does_not_show_error_message_in_data_columns() -> None:
    result = TagLookupResult(
        "EPC-ERROR",
        TagLookupStatus.ERROR,
        "Não foi possível consultar a etiqueta.",
        tag="Tag inválida",
    )

    assert tag_lookup_values(result) == (
        "Tag inválida",
        "Erro",
        "",
        "",
        "",
        "",
        "",
    )


def test_epc_remains_internal_and_is_not_part_of_visual_values() -> None:
    epc = "484C44303130313237353835"
    result = TagLookupResult(
        epc,
        TagLookupStatus.FOUND,
        "Encontrada",
        tag="HLD010127585",
    )

    assert result.epc == epc
    assert epc not in tag_lookup_values(result)
