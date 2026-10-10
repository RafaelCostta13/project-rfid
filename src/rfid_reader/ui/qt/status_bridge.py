"""Projeção somente de leitura dos eventos de conexão existentes, sem sondagens."""

from collections.abc import Mapping

from PySide6.QtCore import Property, QObject, Qt, Signal, Slot

from rfid_reader.domain import ConnectionKind, ConnectionStatus
from rfid_reader.ui.qt.mock_data import PrototypeTheme
from rfid_reader.ui.qt.models import TagTableModel

CONNECTION_LABELS = {
    ConnectionKind.RFID: "RFID",
    ConnectionKind.INTERNET: "Internet",
    ConnectionKind.WAVESHARE: "Comandos",
    ConnectionKind.SYSTEM: "Sistema",
}
STATE_COLORS = {
    ConnectionStatus.CONNECTED: "ok",
    ConnectionStatus.CHECKING: "checking",
    ConnectionStatus.DISCONNECTED: "error",
    ConnectionStatus.ERROR: "error",
}


class ConnectionBridge(QObject):
    """Recebe o callback do monitor; não é monitor nem controller operacional."""

    changed = Signal()
    statusReceived = Signal(object, object)

    def __init__(self, theme: PrototypeTheme = PrototypeTheme.CORPORATE) -> None:
        super().__init__()
        self._theme = theme
        self._states: dict[ConnectionKind, ConnectionStatus] = {}
        self._closed = False
        self._model = TagTableModel(self)
        self.statusReceived.connect(self._apply_status, Qt.ConnectionType.QueuedConnection)

    def _get_connections(self) -> list[dict[str, str]]:
        return [
            {
                "label": label,
                "state": STATE_COLORS[self._states[kind]] if kind in self._states else "unknown",
                "description": self._states[kind].value if kind in self._states else "Desconhecido",
            }
            for kind, label in CONNECTION_LABELS.items()
        ]

    def _get_theme(self) -> str:
        return self._theme.value

    def _get_model(self) -> QObject:
        return self._model

    theme = Property(str, _get_theme, notify=changed)
    connections = Property(list, _get_connections, notify=changed)
    tagModel = Property(QObject, _get_model, constant=True)
    simulated = Property(bool, lambda self: False, constant=True)
    bannerText = Property(str, lambda self: "CONFIGURAÇÕES LOCAIS · SEM LEITURA", constant=True)
    scenario = Property(str, lambda self: "", constant=True)
    operationState = Property(str, lambda self: "unknown", constant=True)
    operationTitle = Property(str, lambda self: "Leitura não integrada", constant=True)
    operationDescription = Property(
        str,
        lambda self: "Somente configurações e estados observados; sem comandos operacionais.",
        constant=True,
    )
    foundCount = Property(int, lambda self: 0, constant=True)
    startEnabled = Property(bool, lambda self: False, constant=True)
    stopEnabled = Property(bool, lambda self: False, constant=True)

    def receive_status(self, kind: ConnectionKind, status: ConnectionStatus) -> None:
        """Assinatura do StatusListener; pode ser chamada por workers existentes."""

        self.statusReceived.emit(kind, status)

    def observe_snapshot(self, states: Mapping[ConnectionKind, ConnectionStatus]) -> None:
        """Adapta ConnectionMonitor.statuses(), sem criar verificadores adicionais."""

        for kind, status in states.items():
            self.receive_status(kind, status)

    @Slot(object, object)
    def _apply_status(self, kind: object, status: object) -> None:
        if self._closed or not isinstance(kind, ConnectionKind) or kind not in CONNECTION_LABELS:
            return
        if not isinstance(status, ConnectionStatus) or self._states.get(kind) is status:
            return
        self._states[kind] = status
        self.changed.emit()

    @Slot(str, result=bool)
    def selectTheme(self, name: str) -> bool:
        try:
            theme = PrototypeTheme(name)
        except ValueError:
            return False
        if theme != self._theme:
            self._theme = theme
            self.changed.emit()
        return True

    @Slot(str, result=bool)
    def selectScenario(self, name: str) -> bool:
        return False

    @Slot()
    def requestStart(self) -> None:
        """Sem integração de comandos nesta etapa."""

    @Slot()
    def requestStop(self) -> None:
        """Sem integração de comandos nesta etapa."""

    def close(self) -> None:
        self._closed = True
