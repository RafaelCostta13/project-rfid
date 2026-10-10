"""Composição operacional compartilhada, independente de toolkit gráfico."""

from __future__ import annotations

import logging
import threading
from collections.abc import Callable, Mapping
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from rfid_reader.config import Settings, validate_reader_connection, validate_waveshare_connection
from rfid_reader.domain import (
    ConnectionKind,
    ConnectionStatus,
    InventoryCleared,
    InventoryEvent,
    InventoryStatus,
    InventoryStatusChanged,
    ReaderConfigurationFeedback,
    TagLookupEvent,
    TagReceived,
    WaveshareConfigurationFeedback,
)
from rfid_reader.integrations.backend_client import BackendRFIDClient
from rfid_reader.integrations.waveshare_modbus import (
    PymodbusWaveshareConnectionTester,
    WaveshareDiagnosticPort,
    WaveshareSerialGate,
)
from rfid_reader.readers import ZebraFX9600Reader
from rfid_reader.readers.base import RFIDReader
from rfid_reader.services.automatic_inventory import (
    AutomaticInventoryController,
    CycleTimer,
    create_timer,
)
from rfid_reader.services.backend import BackendConfigurationService, BackendHealthChecker
from rfid_reader.services.connection_monitor import ConnectionChecker, ConnectionMonitor
from rfid_reader.services.internet import InternetConnectionChecker
from rfid_reader.services.manual_inventory import ManualInventoryService
from rfid_reader.services.reader_configuration import (
    DotEnvReaderConfigurationStore,
    ReaderConfigurationService,
)
from rfid_reader.services.reader_connection import ReaderConnectionChecker
from rfid_reader.services.station_configuration import StationConfigurationService
from rfid_reader.services.tag_lookup import TagLookupService
from rfid_reader.services.waveshare_configuration import (
    DotEnvWaveshareConfigurationStore,
    WaveshareConfigurationService,
    WaveshareConnectionTester,
)
from rfid_reader.services.waveshare_connection import WaveshareConnectionChecker
from rfid_reader.services.waveshare_diagnostic import (
    DiagnosticEvent,
    DiagnosticPort,
    WaveshareDiagnosticService,
)

LOGGER = logging.getLogger(__name__)


def configure_logging(level: str) -> None:
    """Configura o logging compartilhado pelas entradas gráficas."""

    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s %(message)s")


class OperationalReader(RFIDReader, Protocol):
    def configure_connection(self, host: str, port: int, reader_id: str) -> None: ...


class RuntimeShutdownError(RuntimeError):
    """Os recursos foram encerrados, mas uma ou mais operações de limpeza falharam."""


@dataclass(frozen=True, slots=True)
class RuntimeEvent:
    channel: str
    value: object


@dataclass(frozen=True, slots=True)
class CommandFinished:
    command: str
    success: bool
    message: str = ""


@dataclass(frozen=True, slots=True)
class RuntimeDependencies:
    """Pontos de injeção dos simuladores; os serviços operacionais são os mesmos."""

    reader: OperationalReader | None = None
    backend_factory: Callable[[str, float], BackendRFIDClient] = BackendRFIDClient
    port_factory: Callable[..., DiagnosticPort] = WaveshareDiagnosticPort
    tester_factory: Callable[[WaveshareSerialGate], WaveshareConnectionTester] = lambda gate: (
        PymodbusWaveshareConnectionTester(serial_gate=gate)
    )
    timer_factory: Callable[[float, Callable[[], None]], CycleTimer] = create_timer
    checkers: Mapping[ConnectionKind, ConnectionChecker] | None = None


class _SharedReaderChecker:
    def __init__(self, reader: OperationalReader, gate: threading.Lock) -> None:
        self._checker = ReaderConnectionChecker(reader)
        self._gate = gate

    def check(self) -> ConnectionStatus:
        with self._gate:
            return self._checker.check()

    def close(self) -> None:
        self._checker.close()


class ApplicationRuntime:
    """Possui uma sessão Zebra, uma sessão serial, um lookup e um monitor.

    Construir não abre equipamentos. start/close controlam workers e conexões.
    Os eventos são entregues aos assinantes, incluindo a ponte Qt.
    """

    def __init__(
        self,
        settings: Settings,
        path: Path,
        dependencies: RuntimeDependencies | None = None,
    ) -> None:
        deps = dependencies or RuntimeDependencies()
        self._lock = threading.RLock()
        self._reader_gate = threading.Lock()
        self._started = False
        self._closing = False
        self._closed = threading.Event()
        self._listeners: list[Callable[[RuntimeEvent], None]] = []
        self._statuses: dict[ConnectionKind, ConnectionStatus] = {}
        self._backend_factory = deps.backend_factory
        self._timeout = settings.connection_timeout_seconds
        self.reader = deps.reader or ZebraFX9600Reader(
            settings.reader_host,
            settings.reader_port,
            settings.reader_name,
            settings.antennas[0],
            settings.connection_timeout_seconds,
        )
        store = DotEnvReaderConfigurationStore(path)
        self.backend_configuration = BackendConfigurationService(settings, store)
        self.station_configuration = StationConfigurationService(settings, store)
        self.lookup = TagLookupService(
            self.backend_client,
            settings.tag_lookup_queue_size,
            self._on_lookup,
            autostart=False,
        )
        self.inventory = ManualInventoryService(self.reader, self._on_inventory)
        self.automatic = AutomaticInventoryController(
            self.inventory, deps.timer_factory, self._on_mode
        )
        self.commands = ThreadPoolExecutor(max_workers=1, thread_name_prefix="application-command")
        self.reader_configuration = ReaderConfigurationService(
            settings,
            store,
            self.reader,
            None,
            lambda: self.automatic.enabled,
            self._on_reader_config,
        )
        self.serial_gate = WaveshareSerialGate()
        self.waveshare_tester = deps.tester_factory(self.serial_gate)
        self.waveshare_configuration = WaveshareConfigurationService(
            settings,
            DotEnvWaveshareConfigurationStore(path),
            self.waveshare_tester,
            self._on_waveshare_config,
        )
        self.diagnostic = WaveshareDiagnosticService(
            self.waveshare_configuration.current,
            self._on_diagnostic,
            port_factory=deps.port_factory,
            serial_gate=self.serial_gate,
            automatic=self.automatic,
        )
        checkers: dict[ConnectionKind, ConnectionChecker] = {
            ConnectionKind.RFID: _SharedReaderChecker(self.reader, self._reader_gate),
            ConnectionKind.INTERNET: InternetConnectionChecker(self._timeout),
            ConnectionKind.WAVESHARE: WaveshareConnectionChecker(
                self.diagnostic, self.waveshare_tester
            ),
            ConnectionKind.SYSTEM: BackendHealthChecker(self.backend_client, include_database=True),
        }
        if deps.checkers is not None:
            checkers.update(deps.checkers)
        self.monitor = ConnectionMonitor(
            checkers,
            settings.status_check_interval_seconds,
            self._on_connection,
            additional_kinds=(ConnectionKind.DATABASE,),
        )

    def backend_client(self) -> BackendRFIDClient:
        return self._backend_factory(self.backend_configuration.current(), self._timeout)

    def subscribe(self, listener: Callable[[RuntimeEvent], None]) -> Callable[[], None]:
        with self._lock:
            self._listeners.append(listener)

        def unsubscribe() -> None:
            with self._lock:
                if listener in self._listeners:
                    self._listeners.remove(listener)

        return unsubscribe

    def _publish(self, channel: str, value: object) -> None:
        with self._lock:
            listeners = tuple(self._listeners) if not self._closing else ()
        for listener in listeners:
            try:
                listener(RuntimeEvent(channel, value))
            except Exception:
                LOGGER.exception("runtime_listener_failed channel=%s", channel)

    def _on_lookup(self, event: TagLookupEvent) -> None:
        self._publish("lookup", event)

    def _on_inventory(self, event: InventoryEvent) -> None:
        if isinstance(event, InventoryCleared):
            self.lookup.start_session()
        elif isinstance(event, TagReceived):
            self.lookup.submit(event.tag)
            return
        elif (
            isinstance(event, InventoryStatusChanged)
            and event.status is not InventoryStatus.READING
        ):
            self.lookup.stop_accepting()
        self._publish("inventory", event)

    def _on_mode(self, enabled: bool) -> None:
        self._publish("automatic", enabled)

    def _on_reader_config(self, event: ReaderConfigurationFeedback) -> None:
        self._publish("reader_configuration", event)

    def _on_waveshare_config(self, event: WaveshareConfigurationFeedback) -> None:
        self._publish("waveshare_configuration", event)

    def _on_diagnostic(self, event: DiagnosticEvent) -> None:
        self._publish("diagnostic", event)

    def _on_connection(self, kind: ConnectionKind, status: ConnectionStatus) -> None:
        with self._lock:
            if self._closing:
                return
            self._statuses[kind] = status
        if kind is ConnectionKind.RFID and status is ConnectionStatus.CONNECTED:
            self.inventory.connection_recovered()
        self.automatic.update_connection_status(kind, status)
        self._publish("connection", (kind, status))
        if kind is ConnectionKind.WAVESHARE and status is ConnectionStatus.CONNECTED:
            with self._lock:
                if not self._closing:
                    self.diagnostic.connect_automatic()

    def statuses(self) -> dict[ConnectionKind, ConnectionStatus]:
        with self._lock:
            return dict(self._statuses)

    def start(self) -> None:
        with self._lock:
            if self._closing or self._started:
                return
            self._started = True
            self.lookup.start()
            # SYSTEM deve ser observado antes que qualquer worker habilite aptidão.
            self._on_connection(ConnectionKind.SYSTEM, ConnectionStatus.CHECKING)
            self._on_connection(ConnectionKind.DATABASE, ConnectionStatus.CHECKING)
            self.diagnostic.connect_automatic()
            self.monitor.start()

    def submit(self, name: str, operation: Callable[[], object]) -> bool:
        """Serializa comandos e gravações; nunca executa I/O na thread gráfica."""

        with self._lock:
            if self._closing or not self._started:
                return False
            self.commands.submit(self._execute, name, operation)
            return True

    def _execute(self, name: str, operation: Callable[[], object]) -> None:
        try:
            result = operation()
            self._publish("command", CommandFinished(name, result is not False))
        except Exception:
            LOGGER.exception("runtime_command_failed command=%s", name)
            self._publish(
                "command", CommandFinished(name, False, "Não foi possível executar o comando.")
            )

    def start_automatic(self) -> bool:
        def enable() -> bool:
            # Devolve o diagnóstico à operação antes de armar DI1.
            self.diagnostic.resume_automatic()
            self.inventory.connection_recovered()
            return self.automatic.enable()

        return self.submit("start", enable)

    def stop_automatic(self) -> bool:
        return self.submit("stop", self.automatic.disable)

    def test_reader(self, name: str, host: str, port: str) -> bool:
        connection = validate_reader_connection(name, host, port)
        if self.automatic.enabled or self.inventory.status is InventoryStatus.READING:
            return False
        # O monitor e este teste compartilham a sessão e a exclusão de conexão.
        with self._reader_gate:
            saved = self.reader_configuration.current()
            try:
                self.reader.disconnect()
                self.reader.configure_connection(connection.host, connection.port, connection.name)
                self.reader.connect()
                return self.reader.is_connected()
            finally:
                self.reader.disconnect()
                self.reader.configure_connection(saved.host, saved.port, saved.name)
                self.reader.connect()

    def test_backend(self, url: str) -> bool:
        return self._backend_factory(url, self._timeout).health().system_ok

    def test_waveshare(self, values: tuple[str, ...]) -> bool:
        connection = validate_waveshare_connection(*values, require_serial_port=True)
        if connection == self.waveshare_configuration.current():
            return self.diagnostic.probe_status(self.waveshare_tester) is ConnectionStatus.CONNECTED
        self.waveshare_tester.test(connection)
        return True

    def close(self) -> None:
        """Bloqueia comandos, cancela ciclo e aguarda comunicação/HTTP em andamento."""

        with self._lock:
            if self._closing:
                wait = True
            else:
                self._closing = True
                wait = False
        if wait:
            self._closed.wait()
            return
        failures: list[tuple[str, Exception]] = []
        cleanup = (
            ("lookup_cancel", self.lookup.begin_close),
            ("automatic", self.automatic.close),
            ("commands", lambda: self.commands.shutdown(wait=True, cancel_futures=True)),
            ("monitor", self.monitor.stop),
            ("diagnostic", self.diagnostic.close),
            ("reader_configuration", self.reader_configuration.close),
            ("waveshare_configuration", self.waveshare_configuration.close),
            ("backend_configuration", self.backend_configuration.close),
            ("inventory", self.inventory.close),
            ("lookup", self.lookup.close),
        )
        try:
            for component, close in cleanup:
                try:
                    close()
                except Exception as error:
                    LOGGER.exception("runtime_shutdown_failed component=%s", component)
                    failures.append((component, error))
        finally:
            self._closed.set()
        if failures:
            raise RuntimeShutdownError(
                "Falha ao encerrar: " + ", ".join(component for component, error in failures)
            ) from failures[0][1]
