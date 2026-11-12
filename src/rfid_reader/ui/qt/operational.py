"""Apresentação Qt dos eventos do runtime; nenhuma regra RFID vive na UI."""

from collections.abc import Callable

from PySide6.QtCore import Property, QObject, Qt, Signal, Slot

from rfid_reader.domain import (
    ConnectionKind,
    ConnectionStatus,
    InventorySessionCompleted,
    InventoryStatus,
    InventoryStatusChanged,
    TagLookupChanged,
    TagLookupSessionStarted,
    TagLookupSessionSummary,
    TagLookupStatus,
)
from rfid_reader.runtime import ApplicationRuntime, CommandFinished, RuntimeEvent
from rfid_reader.services.automatic_inventory import OPERATIONAL_CONNECTIONS
from rfid_reader.services.waveshare_diagnostic import DiagnosticEvent, DiagnosticEventKind
from rfid_reader.ui.qt.audio import AudioNotificationService
from rfid_reader.ui.qt.mock_data import PrototypeTheme
from rfid_reader.ui.qt.models import TagTableModel
from rfid_reader.ui.qt.simulation import simulated_result
from rfid_reader.ui.qt.status_bridge import CONNECTION_LABELS, STATE_COLORS


class OperationalBridge(QObject):
    changed = Signal()
    eventReceived = Signal(object)

    def __init__(
        self,
        runtime: ApplicationRuntime,
        theme: PrototypeTheme,
        *,
        audio_enabled: bool = True,
        audio_interval_ms: int = 300,
        simulation_completion_notifier: Callable[[int], bool] | None = None,
        operational_completion_notifier: Callable[[int], bool] | None = None,
    ) -> None:
        super().__init__()
        self._theme = theme
        self._closed = False
        self._states: dict[ConnectionKind, ConnectionStatus] = {}
        self._model = TagTableModel(self)
        self._simulation_model = TagTableModel(self)
        self._summary = TagLookupSessionSummary()
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
        self._simulation_session_id = 0
        self._simulation_sequence = 0
        self._simulation_active = False
        self._simulation_presenting = False
        self._simulation_summary = TagLookupSessionSummary()
        self._simulation_completion_notifier = simulation_completion_notifier
        self._operational_completion_notifier = operational_completion_notifier
        self._announced_operational_sessions: set[int] = set()
        self._audio = AudioNotificationService(
            enabled=audio_enabled,
            interval_ms=audio_interval_ms,
            parent=self,
        )
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
    tagModel = Property(
        QObject,
        lambda self: self._simulation_model if self._simulation_presenting else self._model,
        notify=changed,
    )
    simulationTagModel = Property(QObject, lambda self: self._simulation_model, constant=True)
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
        if self._automatic and self._ready():
            return "Pronto para leitura"
        return "Leitura parada"

    def _operation_description(self) -> str:
        if self._message:
            return self._message
        if self._inventory is InventoryStatus.READING:
            return "Inventário ativo · saída DI5 → DI2 · limite de 60 segundos."
        if self._automatic and self._ready():
            return "Modo automático habilitado · aguardando entrada DI1 → DI4."
        return "Leitura desabilitada ou aguardando conexões operacionais."

    def _active_summary(self) -> TagLookupSessionSummary:
        return self._simulation_summary if self._simulation_presenting else self._summary

    bannerText = Property(str, lambda self: "OPERAÇÃO RFID", constant=True)
    operationState = Property(str, _operation_state, notify=changed)
    operationTitle = Property(str, _operation_title, notify=changed)
    operationDescription = Property(str, _operation_description, notify=changed)
    foundCount = Property(int, lambda self: self._active_summary().total, notify=changed)
    extraBoxCount = Property(
        int, lambda self: self._active_summary().extra_box_total, notify=changed
    )
    simulationActive = Property(bool, lambda self: self._simulation_active, notify=changed)
    simulationPresenting = Property(bool, lambda self: self._simulation_presenting, notify=changed)
    simulationFoundCount = Property(
        int, lambda self: self._simulation_summary.total, notify=changed
    )
    simulationExtraBoxCount = Property(
        int, lambda self: self._simulation_summary.extra_box_total, notify=changed
    )
    startEnabled = Property(
        bool,
        lambda self: (
            not self._closed
            and not self._command_pending
            and not self._automatic
            and not self._simulation_active
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
        elif isinstance(value, InventorySessionCompleted):
            if (
                value.found_count > 0
                and value.session_id not in self._announced_operational_sessions
                and self._operational_completion_notifier is not None
            ):
                self._announced_operational_sessions.add(value.session_id)
                self._operational_completion_notifier(value.found_count)
        elif event.channel == "automatic" and isinstance(value, bool):
            self._automatic = value
        elif isinstance(value, TagLookupSessionStarted):
            self._session_id = value.session_id
            self._summary.reset()
            self._model.start_session(value.session_id)
            self._message = ""
            self._audio.begin_session()
        elif isinstance(value, TagLookupChanged):
            if value.session_id != self._session_id:
                return
            self._summary.update(value.result)
            self._model.upsert(value.result, value.session_id)
            if value.result.status is TagLookupStatus.FOUND:
                self._audio.request(value.result.epc)
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
            self._audio.cancel()

    @Slot(bool, int)
    def setAudioSettings(self, enabled: bool, interval_ms: int) -> None:
        self._audio.configure(enabled, interval_ms)

    @Slot(result=bool)
    def startSimulation(self) -> bool:
        if self._closed or self._inventory is InventoryStatus.READING or self._automatic:
            self._message = "Finalize a leitura real antes de iniciar a simulação."
            self.changed.emit()
            return False
        self._simulation_session_id += 1
        self._simulation_sequence = 0
        self._simulation_active = True
        self._simulation_presenting = True
        self._simulation_summary.reset()
        self._simulation_model.start_session(self._simulation_session_id)
        self._audio.begin_session()
        self.changed.emit()
        return True

    def _add_simulation(self, extra_box: bool) -> bool:
        if not self._simulation_active:
            return False
        self._simulation_sequence += 1
        result = simulated_result(self._simulation_sequence, extra_box=extra_box)
        self._simulation_summary.update(result)
        self._simulation_model.upsert(result, self._simulation_session_id)
        if not extra_box:
            self._audio.request(result.epc)
        self.changed.emit()
        return True

    @Slot(result=bool)
    def simulateFound(self) -> bool:
        return self._add_simulation(False)

    @Slot(result=bool)
    def simulateExtraBox(self) -> bool:
        return self._add_simulation(True)

    @Slot()
    def finishSimulation(self) -> None:
        self._finish_simulation(announce=True)

    def _finish_simulation(self, *, announce: bool) -> None:
        if not self._simulation_active:
            return
        found_count = self._simulation_summary.total
        self._simulation_active = False
        self._audio.cancel()
        if announce and found_count > 0 and self._simulation_completion_notifier is not None:
            self._simulation_completion_notifier(found_count)
        self.changed.emit()

    @Slot()
    def closeSimulation(self) -> None:
        self._finish_simulation(announce=False)
        self._simulation_presenting = False
        self._simulation_session_id += 1
        self._simulation_summary.reset()
        self._simulation_model.start_session(self._simulation_session_id)
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
        self._audio.close()
        self._unsubscribe()
        self._closed = True
