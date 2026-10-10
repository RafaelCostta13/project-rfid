"""Apresentação Qt dos eventos do runtime; nenhuma regra RFID vive na UI."""

from PySide6.QtCore import Property, QObject, Qt, Signal, Slot

from rfid_reader.domain import (
    ConnectionKind,
    ConnectionStatus,
    InventoryStatus,
    InventoryStatusChanged,
    TagLookupChanged,
    TagLookupSessionStarted,
    TagLookupStatus,
)
from rfid_reader.runtime import ApplicationRuntime, CommandFinished, RuntimeEvent
from rfid_reader.services.automatic_inventory import OPERATIONAL_CONNECTIONS
from rfid_reader.services.waveshare_diagnostic import DiagnosticEvent, DiagnosticEventKind
from rfid_reader.ui.qt.mock_data import PrototypeTheme
from rfid_reader.ui.qt.models import TagTableModel
from rfid_reader.ui.qt.status_bridge import CONNECTION_LABELS, STATE_COLORS


class OperationalBridge(QObject):
    changed = Signal()
    eventReceived = Signal(object)

    def __init__(self, runtime: ApplicationRuntime, theme: PrototypeTheme) -> None:
        super().__init__()
        self._theme = theme
        self._closed = False
        self._states: dict[ConnectionKind, ConnectionStatus] = {}
        self._model = TagTableModel(self)
        self.runtime = runtime
        self._inventory = runtime.inventory.status
        self._automatic = runtime.automatic.enabled
        self._command_pending = False
        self._message = ""
        self._diagnostic_connected = False
        self._diagnostic_message = "Desconectado"
        self._inputs: list[bool | None] = [None] * 5
        self._relays: list[bool | None] = [None] * 8
        self._session_id = 0
        self.eventReceived.connect(self._apply_event, Qt.ConnectionType.QueuedConnection)
        self._unsubscribe = runtime.subscribe(self.eventReceived.emit)
        self._states.update(runtime.statuses())

    def _get_connections(self) -> list[dict[str, str]]:
        return [
            {
                "label": label,
                "state": STATE_COLORS[self._states[kind]] if kind in self._states else "unknown",
                "description": self._states[kind].value if kind in self._states else "Desconhecido",
            }
            for kind, label in CONNECTION_LABELS.items()
        ]

    theme = Property(str, lambda self: self._theme.value, notify=changed)
    connections = Property(list, _get_connections, notify=changed)
    tagModel = Property(QObject, lambda self: self._model, constant=True)
    simulated = Property(bool, lambda self: False, constant=True)
    scenario = Property(str, lambda self: "", constant=True)

    @Slot(str, result=bool)
    def selectTheme(self, name: str) -> bool:
        try:
            self._theme = PrototypeTheme(name)
        except ValueError:
            return False
        self.changed.emit()
        return True

    @Slot(str, result=bool)
    def selectScenario(self, name: str) -> bool:
        return False

    def _ready(self) -> bool:
        return all(
            self._states.get(kind) is ConnectionStatus.CONNECTED for kind in OPERATIONAL_CONNECTIONS
        )

    def _operation_state(self) -> str:
        if self._inventory is InventoryStatus.ERROR:
            return "error"
        if self._inventory is InventoryStatus.READING:
            return "reading"
        if any(
            self._states.get(kind) in (ConnectionStatus.ERROR, ConnectionStatus.DISCONNECTED)
            for kind in OPERATIONAL_CONNECTIONS
        ):
            return "error"
        return "ok" if self._ready() else "checking"

    def _operation_title(self) -> str:
        if self._inventory is InventoryStatus.READING:
            return "Leitura em andamento"
        if self._inventory is InventoryStatus.ERROR:
            return "Falha na leitura RFID"
        if not self._ready():
            return (
                "Verificando conexões"
                if self._operation_state() == "checking"
                else "Sistema indisponível"
            )
        return "Aguardando DI1" if self._automatic else "Sistema apto"

    def _operation_description(self) -> str:
        if self._message:
            return self._message
        if self._inventory is InventoryStatus.READING:
            return "Inventário ativo · DI2 encerra o ciclo · limite de 60 segundos."
        if self._automatic:
            return "Modo automático habilitado · aguardando DI1 ATIVA → DESATIVADA."
        return "Iniciar leitura habilita o modo automático; o inventário aguarda DI1."

    bannerText = Property(str, lambda self: "OPERAÇÃO RFID", constant=True)
    operationState = Property(str, _operation_state, notify=changed)
    operationTitle = Property(str, _operation_title, notify=changed)
    operationDescription = Property(str, _operation_description, notify=changed)
    foundCount = Property(int, lambda self: self._model.rowCount(), notify=changed)
    startEnabled = Property(
        bool,
        lambda self: (
            not self._closed
            and not self._command_pending
            and not self._automatic
            and self._ready()
            and self._inventory is not InventoryStatus.READING
        ),
        notify=changed,
    )
    stopEnabled = Property(
        bool,
        lambda self: not self._closed and not self._command_pending and self._automatic,
        notify=changed,
    )
    diagnosticConnected = Property(bool, lambda self: self._diagnostic_connected, notify=changed)
    diagnosticMessage = Property(str, lambda self: self._diagnostic_message, notify=changed)
    diagnosticInputs = Property(list, lambda self: self._inputs, notify=changed)
    diagnosticRelays = Property(list, lambda self: self._relays, notify=changed)
    automaticEnabled = Property(bool, lambda self: self._automatic, notify=changed)
    operational = Property(bool, lambda self: True, constant=True)

    @Slot(object)
    def _apply_event(self, event: object) -> None:
        if self._closed or not isinstance(event, RuntimeEvent):
            return
        value = event.value
        if event.channel == "connection" and isinstance(value, tuple):
            kind, status = value
            if isinstance(kind, ConnectionKind) and isinstance(status, ConnectionStatus):
                self._states[kind] = status
        elif isinstance(value, InventoryStatusChanged):
            self._inventory = value.status
        elif event.channel == "automatic" and isinstance(value, bool):
            self._automatic = value
        elif isinstance(value, TagLookupSessionStarted):
            self._session_id = value.session_id
            self._model.start_session(value.session_id)
            self._message = ""
        elif isinstance(value, TagLookupChanged):
            if value.session_id != self._session_id:
                return
            self._model.upsert(value.result, value.session_id)
            if value.result.status is TagLookupStatus.ERROR:
                self._message = value.result.message
        elif isinstance(value, CommandFinished):
            if value.command in ("start", "stop"):
                self._command_pending = False
                if not value.success and value.command == "start":
                    self._message = "Não foi possível habilitar a leitura. Verifique as conexões."
            if value.message:
                self._message = value.message
        elif isinstance(value, DiagnosticEvent):
            self._apply_diagnostic(value)
        self.changed.emit()

    def _apply_diagnostic(self, event: DiagnosticEvent) -> None:
        if event.kind is DiagnosticEventKind.CONNECTED:
            self._diagnostic_connected = True
            self._diagnostic_message = "Conectado"
        elif event.kind is DiagnosticEventKind.DISCONNECTED:
            self._diagnostic_connected = False
            self._diagnostic_message = event.message or "Desconectado"
            self._inputs = [None] * 5
            self._relays = [None] * 8
        elif event.kind is DiagnosticEventKind.CONNECTING:
            self._diagnostic_message = "Conectando..."
        elif event.kind is DiagnosticEventKind.INPUTS:
            self._inputs = list(event.states[:5])
        elif event.kind is DiagnosticEventKind.RELAYS:
            if event.channel:
                self._relays[event.channel - 1] = event.states[0]
            else:
                self._relays = list(event.states[:8])
        elif event.kind is DiagnosticEventKind.RELAY_ERROR:
            self._relays[event.channel - 1] = None
            self._diagnostic_message = event.message
        elif event.kind is DiagnosticEventKind.AUTOMATIC:
            self._diagnostic_message = event.message or "CH1–CH3 sob controle operacional"

    @Slot()
    def requestStart(self) -> None:
        if self.startEnabled:
            self._message = ""
            self._command_pending = self.runtime.start_automatic()
            self.changed.emit()

    @Slot()
    def requestStop(self) -> None:
        if self.stopEnabled:
            self._command_pending = self.runtime.stop_automatic()
            self.changed.emit()

    @Slot()
    def connectDiagnostic(self) -> None:
        self.runtime.submit("diagnostic_connect", self.runtime.diagnostic.connect)

    @Slot()
    def disconnectDiagnostic(self) -> None:
        self.runtime.submit("diagnostic_disconnect", self.runtime.diagnostic.disconnect)

    @Slot(int, bool)
    def setRelay(self, channel: int, enabled: bool) -> None:
        if self._closed or not self._diagnostic_connected or channel not in range(1, 9):
            return
        if channel <= 3 and self._automatic:
            return

        def set_relay() -> None:
            if not self.runtime.automatic.enabled:
                self.runtime.diagnostic.connect()
            self.runtime.diagnostic.set_relay(channel, enabled)

        self.runtime.submit("relay", set_relay)

    @Slot()
    def beginClose(self) -> None:
        self.close()

    def close(self) -> None:
        self._unsubscribe()
        self._closed = True
