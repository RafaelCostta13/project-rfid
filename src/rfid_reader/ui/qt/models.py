"""Projeção incremental dos resultados normalizados para a tabela Qt."""

from PySide6.QtCore import (
    Property,
    QAbstractTableModel,
    QByteArray,
    QModelIndex,
    QObject,
    QPersistentModelIndex,
    Qt,
)

from rfid_reader.domain import TagLookupResult, TagLookupStatus

Index = QModelIndex | QPersistentModelIndex
COLUMNS = (
    ("record_status", "Status"),
    ("customer", "Cliente"),
    ("invoice_number", "Nota fiscal"),
    ("volume", "Volume"),
    ("order_number", "Pedido"),
    ("dock", "Doca"),
)
CELL_ROLE = int(Qt.ItemDataRole.UserRole) + 1
STATUS_ROLE = CELL_ROLE + 1


EXTRA_BOX_ROLE = STATUS_ROLE + 1
EPC_ROLE = EXTRA_BOX_ROLE + 1
EXTRA_BOX_REASON_ROLE = EPC_ROLE + 1


class TagTableModel(QAbstractTableModel):
    """Projeta resultados encontrados e Extra Box sem duplicar EPCs."""

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._records: list[TagLookupResult] = []
        self._rows: dict[str, int] = {}
        self._session_id = 0

    def rowCount(self, parent: Index | None = None) -> int:
        return 0 if parent is not None and parent.isValid() else len(self._records)

    def columnCount(self, parent: Index | None = None) -> int:
        return 0 if parent is not None and parent.isValid() else len(COLUMNS)

    def roleNames(self) -> dict[int, QByteArray]:
        return {
            int(Qt.ItemDataRole.DisplayRole): QByteArray(b"display"),
            CELL_ROLE: QByteArray(b"cellText"),
            STATUS_ROLE: QByteArray(b"rowStatus"),
            EXTRA_BOX_ROLE: QByteArray(b"isExtraBox"),
            EPC_ROLE: QByteArray(b"epc"),
            EXTRA_BOX_REASON_ROLE: QByteArray(b"extraBoxReason"),
        }

    def _get_column_titles(self) -> list[str]:
        return [title for attribute, title in COLUMNS]

    columnTitles = Property(list, _get_column_titles, constant=True)

    def data(self, index: Index, role: int = int(Qt.ItemDataRole.DisplayRole)) -> str | bool | None:
        if not index.isValid() or not (0 <= index.row() < len(self._records)):
            return None
        if not 0 <= index.column() < len(COLUMNS):
            return None
        result = self._records[index.row()]
        is_extra_box = self._is_extra_box(result)
        if role == STATUS_ROLE:
            return "Extra box" if is_extra_box else result.record_status or result.status.value
        if role == EXTRA_BOX_ROLE:
            return is_extra_box
        if role == EPC_ROLE:
            return result.epc
        if role == EXTRA_BOX_REASON_ROLE:
            return self._extra_box_reason(result)
        if role not in (int(Qt.ItemDataRole.DisplayRole), CELL_ROLE):
            return None
        values = (
            "Extra box" if is_extra_box else result.record_status or result.status.value,
            self._display_value(result.customer, is_extra_box),
            self._display_value(result.invoice_number, is_extra_box),
            self._display_value(result.volume, is_extra_box),
            self._display_value(result.order_number, is_extra_box),
            self._display_value(result.dock, is_extra_box),
        )
        return values[index.column()]

    @staticmethod
    def _is_extra_box(result: TagLookupResult) -> bool:
        return result.status in (TagLookupStatus.EXTRA_BOX, TagLookupStatus.NOT_FOUND)

    @staticmethod
    def _extra_box_reason(result: TagLookupResult) -> str:
        if result.status is TagLookupStatus.NOT_FOUND:
            return "Não cadastrado"
        if result.status is TagLookupStatus.EXTRA_BOX:
            return "Já lido"
        return ""

    @staticmethod
    def _display_value(value: str, is_extra_box: bool) -> str:
        return value if value else "—" if is_extra_box else value

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = int(Qt.ItemDataRole.DisplayRole),
    ) -> str | None:
        if role == int(Qt.ItemDataRole.DisplayRole) and orientation == Qt.Orientation.Horizontal:
            return COLUMNS[section][1] if 0 <= section < len(COLUMNS) else None
        return None

    def start_session(self, session_id: int) -> None:
        """Limpa a projeção somente na abertura de uma nova sessão."""

        if session_id <= self._session_id:
            return
        self.beginResetModel()
        self._session_id = session_id
        self._records.clear()
        self._rows.clear()
        self.endResetModel()

    def upsert(self, result: TagLookupResult, session_id: int) -> bool:
        """Projeta dados já aceitos; nunca executa GET, POST ou validação de hardware."""

        if session_id != self._session_id or (
            result.status
            not in (TagLookupStatus.FOUND, TagLookupStatus.EXTRA_BOX, TagLookupStatus.NOT_FOUND)
        ):
            return False
        row = self._rows.get(result.epc)
        if row is None:
            row = len(self._records)
            self.beginInsertRows(QModelIndex(), row, row)
            self._rows[result.epc] = row
            self._records.append(result)
            self.endInsertRows()
        elif self._records[row] != result:
            self._records[row] = result
            self.dataChanged.emit(
                self.index(row, 0),
                self.index(row, len(COLUMNS) - 1),
                [int(Qt.ItemDataRole.DisplayRole), CELL_ROLE, STATUS_ROLE],
            )
        return True
