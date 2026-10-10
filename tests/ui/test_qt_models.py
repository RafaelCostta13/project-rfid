from dataclasses import replace

import pytest

pytest.importorskip("PySide6")

from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtTest import QAbstractItemModelTester, QSignalSpy

from rfid_reader.domain import TagLookupStatus
from rfid_reader.ui.qt.mock_data import MOCK_RECORDS
from rfid_reader.ui.qt.models import CELL_ROLE, STATUS_ROLE, TagTableModel


def test_six_columns_preserve_strings_and_internal_epc(qt_application: object) -> None:
    model = TagTableModel()
    model.start_session(1)
    assert model.upsert(MOCK_RECORDS[0], 1)
    assert model.columnCount() == 6
    assert [model.data(model.index(0, column)) for column in range(6)] == [
        "lido",
        "Cliente exemplo A",
        "00012341",
        "001",
        "000056781",
        "D01",
    ]
    assert [model.headerData(i, Qt.Orientation.Horizontal) for i in range(6)] == [
        "Status",
        "Cliente",
        "Nota fiscal",
        "Volume",
        "Pedido",
        "Doca",
    ]


def test_insert_update_and_unchanged_result_are_incremental(qt_application: object) -> None:
    model = TagTableModel()
    model.start_session(1)
    inserted = QSignalSpy(model.rowsInserted)
    changed = QSignalSpy(model.dataChanged)
    resets = QSignalSpy(model.modelReset)
    model.upsert(MOCK_RECORDS[0], 1)
    model.upsert(MOCK_RECORDS[0], 1)
    updated = replace(MOCK_RECORDS[0], customer="Atualizado", record_status="duplicado")
    model.upsert(updated, 1)
    assert model.rowCount() == 1
    assert inserted.count() == 1
    assert changed.count() == 1
    assert resets.count() == 0
    assert model.data(model.index(0, 0), STATUS_ROLE) == "duplicado"
    assert model.data(model.index(0, 1), CELL_ROLE) == "Atualizado"


@pytest.mark.parametrize(
    "status",
    [
        TagLookupStatus.NOT_FOUND,
        TagLookupStatus.ERROR,
        TagLookupStatus.CONSULTING,
        TagLookupStatus.WAITING,
    ],
)
def test_only_found_records_are_visible(status: TagLookupStatus, qt_application: object) -> None:
    model = TagTableModel()
    model.start_session(1)
    assert not model.upsert(replace(MOCK_RECORDS[0], status=status), 1)
    assert model.rowCount() == 0


def test_session_reset_rejects_late_results(qt_application: object) -> None:
    model = TagTableModel()
    model.start_session(1)
    model.upsert(MOCK_RECORDS[0], 1)
    model.start_session(2)
    assert model.rowCount() == 0
    assert not model.upsert(MOCK_RECORDS[1], 1)
    assert model.upsert(MOCK_RECORDS[1], 2)
    model.start_session(1)
    model.start_session(2)
    assert model.rowCount() == 1


def test_invalid_indexes_roles_and_tree_parents(qt_application: object) -> None:
    model = TagTableModel()
    model.start_session(1)
    model.upsert(MOCK_RECORDS[0], 1)
    assert model.data(QModelIndex()) is None
    assert model.data(model.index(0, 0), int(Qt.ItemDataRole.DecorationRole)) is None
    assert model.rowCount(model.index(0, 0)) == 0
    assert model.columnCount(model.index(0, 0)) == 0
    assert model.headerData(-1, Qt.Orientation.Horizontal) is None
    assert model.headerData(6, Qt.Orientation.Horizontal) is None
    assert model.headerData(0, Qt.Orientation.Vertical) is None


def test_model_obeys_qt_item_model_contract(qt_application: object) -> None:
    model = TagTableModel()
    tester = QAbstractItemModelTester(model, QAbstractItemModelTester.FailureReportingMode.Warning)
    model.start_session(1)
    for record in MOCK_RECORDS:
        model.upsert(record, 1)
    model.upsert(replace(MOCK_RECORDS[0], customer="Outro"), 1)
    model.start_session(2)
    assert tester.model() is model
