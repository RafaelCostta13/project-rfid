"""Ponte Qt da prévia visual; não instancia controllers ou serviços reais."""

import logging

from PySide6.QtCore import Property, QObject, Qt, Signal, Slot

from rfid_reader.ui.qt.mock_data import (
    MOCK_RECORDS,
    PrototypeScenario,
    PrototypeTheme,
    preview_snapshot,
)
from rfid_reader.ui.qt.models import TagTableModel

LOGGER = logging.getLogger(__name__)


class PrototypeBridge(QObject):
    changed = Signal()
    scenarioRequested = Signal(str)

    def __init__(
        self,
        theme: PrototypeTheme = PrototypeTheme.CORPORATE,
        scenario: PrototypeScenario = PrototypeScenario.READY,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._theme = theme
        self._snapshot = preview_snapshot(scenario)
        self._automatic_enabled = scenario is PrototypeScenario.READING
        self._session_id = 0
        self._model = TagTableModel(self)
        self._load_records()
        self.scenarioRequested.connect(self.selectScenario, Qt.ConnectionType.QueuedConnection)

    def _load_records(self) -> None:
        self._session_id += 1
        self._model.start_session(self._session_id)
        if self._snapshot.scenario is not PrototypeScenario.EMPTY:
            for result in MOCK_RECORDS:
                self._model.upsert(result, self._session_id)

    def _get_theme(self) -> str:
        return self._theme.value

    def _get_scenario(self) -> str:
        return self._snapshot.scenario.value

    def _get_state(self) -> str:
        return self._snapshot.state

    def _get_title(self) -> str:
        if self._automatic_enabled and self._snapshot.scenario is not PrototypeScenario.READING:
            return "Aguardando DI1"
        return self._snapshot.title

    def _get_description(self) -> str:
        if self._automatic_enabled and self._snapshot.scenario is not PrototypeScenario.READING:
            return "Modo automático habilitado · simulação, sem sensores reais"
        return self._snapshot.description

    def _get_connections(self) -> list[dict[str, str]]:
        return [
            {"label": item.label, "state": item.state, "description": item.description}
            for item in self._snapshot.connections
        ]

    def _get_count(self) -> int:
        return self._model.rowCount()

    def _get_model(self) -> QObject:
        return self._model

    def _get_start_enabled(self) -> bool:
        return self._snapshot.state == "ok" and not self._automatic_enabled

    def _get_stop_enabled(self) -> bool:
        return self._automatic_enabled

    theme = Property(str, _get_theme, notify=changed)
    scenario = Property(str, _get_scenario, notify=changed)
    operationState = Property(str, _get_state, notify=changed)
    operationTitle = Property(str, _get_title, notify=changed)
    operationDescription = Property(str, _get_description, notify=changed)
    connections = Property(list, _get_connections, notify=changed)
    foundCount = Property(int, _get_count, notify=changed)
    tagModel = Property(QObject, _get_model, constant=True)
    startEnabled = Property(bool, _get_start_enabled, notify=changed)
    stopEnabled = Property(bool, _get_stop_enabled, notify=changed)
    simulated = Property(bool, lambda self: True, constant=True)
    bannerText = Property(str, lambda self: "PRÉVIA QML · DADOS SIMULADOS", constant=True)

    @Slot(str, result=bool)
    def selectTheme(self, name: str) -> bool:
        try:
            theme = PrototypeTheme(name)
        except ValueError:
            LOGGER.warning("qt_preview_unknown_theme")
            return False
        if theme != self._theme:
            self._theme = theme
            self.changed.emit()
        return True

    @Slot(str, result=bool)
    def selectScenario(self, name: str) -> bool:
        try:
            scenario = PrototypeScenario(name)
        except ValueError:
            LOGGER.warning("qt_preview_unknown_scenario")
            return False
        if scenario != self._snapshot.scenario:
            self._snapshot = preview_snapshot(scenario)
            self._automatic_enabled = scenario is PrototypeScenario.READING
            self._load_records()
            self.changed.emit()
        return True

    def queue_scenario(self, name: str) -> None:
        """Permite testar entrega segura de um cenário fictício vindo de um worker."""

        self.scenarioRequested.emit(name)

    @Slot()
    def requestStart(self) -> None:
        """Habilita apenas a representação do modo automático; não inicia RFID."""

        if self._get_start_enabled():
            self._automatic_enabled = True
            self.changed.emit()

    @Slot()
    def requestStop(self) -> None:
        """Encerra a simulação visual, mantendo as cinco linhas da sessão."""

        if not self._automatic_enabled:
            return
        self._automatic_enabled = False
        if self._snapshot.scenario is PrototypeScenario.READING:
            self._snapshot = preview_snapshot(PrototypeScenario.READY)
        self.changed.emit()
