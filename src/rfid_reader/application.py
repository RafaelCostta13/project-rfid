"""Composição da tela principal e dos serviços de conectividade."""

from __future__ import annotations

import logging
import queue
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from rfid_reader.config import Settings
from rfid_reader.domain import (
    ConnectionKind,
    ConnectionStatus,
    InventoryCleared,
    InventoryEvent,
    InventoryStatus,
    InventoryStatusChanged,
    ReaderConfigurationFeedback,
    ReaderConnectionSettings,
    TagLookupEvent,
    TagReceived,
    WaveshareConfigurationFeedback,
)
from rfid_reader.integrations import (
    BackendRFIDClient,
    PymodbusWaveshareConnectionTester,
)
from rfid_reader.integrations.waveshare_modbus import WaveshareSerialGate
from rfid_reader.readers import ZebraFX9600Reader
from rfid_reader.services import (
    ConnectionMonitor,
    DotEnvReaderConfigurationStore,
    DotEnvWaveshareConfigurationStore,
    ManualInventoryService,
    ReaderConfigurationService,
    ReaderConnectionChecker,
    TagLookupService,
    WaveshareConfigurationService,
)
from rfid_reader.services.automatic_inventory import AutomaticInventoryController
from rfid_reader.services.backend import BackendConfigurationService, BackendHealthChecker
from rfid_reader.services.internet import InternetConnectionChecker
from rfid_reader.services.station_configuration import (
    StationConfigurationFeedback,
    StationConfigurationService,
)
from rfid_reader.services.waveshare_connection import WaveshareConnectionChecker
from rfid_reader.services.waveshare_diagnostic import DiagnosticEvent, WaveshareDiagnosticService

LOGGER = logging.getLogger(__name__)


class ApplicationError(RuntimeError):
    """Indica que a interface gráfica não pôde ser iniciada."""


def configure_logging(level: str) -> None:
    """Configura logs técnicos da aplicação."""

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def run_application(settings: Settings, configuration_path: Path) -> None:
    """Cria os componentes, exibe a tela e garante o encerramento."""

    try:
        from rfid_reader.ui.main_window import MainWindow
    except ImportError as error:
        raise ApplicationError(
            "Tkinter não está disponível. Instale o suporte Tk do Python para abrir a tela."
        ) from error

    configure_logging(settings.log_level)
    updates: queue.SimpleQueue[tuple[ConnectionKind, ConnectionStatus]] = queue.SimpleQueue()
    inventory_updates: queue.SimpleQueue[InventoryEvent] = queue.SimpleQueue()
    lookup_updates: queue.SimpleQueue[TagLookupEvent] = queue.SimpleQueue()
    configuration_updates: queue.SimpleQueue[ReaderConfigurationFeedback] = queue.SimpleQueue()
    waveshare_configuration_updates: queue.SimpleQueue[WaveshareConfigurationFeedback] = (
        queue.SimpleQueue()
    )
    diagnostic_updates: queue.SimpleQueue[DiagnosticEvent] = queue.SimpleQueue()
    backend_updates: queue.SimpleQueue[str] = queue.SimpleQueue()
    automatic_mode_updates: queue.SimpleQueue[bool] = queue.SimpleQueue()
    reader = ZebraFX9600Reader(
        settings.reader_host,
        settings.reader_port,
        settings.reader_name,
        settings.antennas[0],
        settings.connection_timeout_seconds,
    )
    backend_configuration = BackendConfigurationService(
        settings, DotEnvReaderConfigurationStore(configuration_path)
    )
    station_configuration = StationConfigurationService(
        settings, DotEnvReaderConfigurationStore(configuration_path)
    )
    lookup = TagLookupService(
        lambda: BackendRFIDClient(
            backend_configuration.current(), settings.connection_timeout_seconds
        ),
        settings.tag_lookup_queue_size,
        lookup_updates.put,
    )

    def on_inventory_event(event: InventoryEvent) -> None:
        if isinstance(event, InventoryCleared):
            lookup.start_session()
        elif isinstance(event, TagReceived):
            lookup.submit(event.tag)
            return
        elif (
            isinstance(event, InventoryStatusChanged)
            and event.status is not InventoryStatus.READING
        ):
            lookup.stop_accepting()
        inventory_updates.put(event)

    inventory = ManualInventoryService(reader, on_inventory_event)
    automatic = AutomaticInventoryController(inventory, mode_listener=automatic_mode_updates.put)
    inventory_commands = ThreadPoolExecutor(max_workers=1, thread_name_prefix="inventory-command")

    def temporary_reader(connection: ReaderConnectionSettings) -> ZebraFX9600Reader:
        return ZebraFX9600Reader(
            connection.host,
            connection.port,
            connection.name,
            settings.antennas[0],
            settings.connection_timeout_seconds,
        )

    reader_configuration = ReaderConfigurationService(
        settings,
        DotEnvReaderConfigurationStore(configuration_path),
        reader,
        temporary_reader,
        lambda: inventory.status is InventoryStatus.READING,
        configuration_updates.put,
    )
    waveshare_serial_gate = WaveshareSerialGate()
    waveshare_tester = PymodbusWaveshareConnectionTester(serial_gate=waveshare_serial_gate)
    waveshare_configuration = WaveshareConfigurationService(
        settings,
        DotEnvWaveshareConfigurationStore(configuration_path),
        waveshare_tester,
        waveshare_configuration_updates.put,
    )
    diagnostic = WaveshareDiagnosticService(
        waveshare_configuration.current,
        diagnostic_updates.put,
        serial_gate=waveshare_serial_gate,
        automatic=automatic,
    )

    def on_connection_status(kind: ConnectionKind, status: ConnectionStatus) -> None:
        automatic.update_connection_status(kind, status)
        updates.put((kind, status))
        if kind is ConnectionKind.WAVESHARE and status is ConnectionStatus.CONNECTED:
            diagnostic.connect_automatic()

    monitor = ConnectionMonitor(
        {
            ConnectionKind.RFID: ReaderConnectionChecker(reader),
            ConnectionKind.INTERNET: InternetConnectionChecker(settings.connection_timeout_seconds),
            ConnectionKind.WAVESHARE: WaveshareConnectionChecker(diagnostic, waveshare_tester),
            ConnectionKind.SYSTEM: BackendHealthChecker(
                lambda: BackendRFIDClient(
                    backend_configuration.current(), settings.connection_timeout_seconds
                )
            ),
        },
        settings.status_check_interval_seconds,
        on_connection_status,
    )

    def stop_automatic() -> bool:
        return automatic.disable()

    def shutdown() -> None:
        automatic.disable()
        monitor.stop()
        diagnostic.close()
        inventory_commands.shutdown(wait=True, cancel_futures=True)
        reader_configuration.close()
        waveshare_configuration.close()
        inventory.close()
        lookup.close()

    def save_station_dock(dock: str) -> StationConfigurationFeedback:
        return station_configuration.save(dock)

    def start_automatic() -> None:
        inventory_commands.submit(automatic.enable)

    def stop_automatic_async() -> None:
        inventory_commands.submit(stop_automatic)

    try:
        window = MainWindow(
            updates,
            inventory_updates,
            lookup_updates,
            configuration_updates,
            waveshare_configuration_updates,
            automatic_mode_updates,
            shutdown,
            start_automatic,
            stop_automatic_async,
            reader_configuration.current,
            reader_configuration.test_connection,
            reader_configuration.save,
            waveshare_configuration.current,
            waveshare_configuration.test_connection,
            waveshare_configuration.save,
            diagnostic_updates,
            diagnostic.connect,
            diagnostic.disconnect,
            diagnostic.set_relay,
            None,
            lambda: automatic.enabled,
            get_station_dock=station_configuration.current,
            on_save_station_dock=lambda dock: save_station_dock(dock),
            get_backend_url=backend_configuration.current,
            on_test_backend=lambda value: backend_configuration.test_connection(
                value, backend_updates.put
            ),
            on_save_backend=backend_configuration.save,
            backend_updates=backend_updates,
        )
    except Exception as error:
        inventory_commands.shutdown(wait=True, cancel_futures=True)
        monitor.stop()
        reader_configuration.close()
        waveshare_configuration.close()
        diagnostic.close()
        lookup.close()
        inventory.close()
        raise ApplicationError(f"não foi possível criar a janela principal: {error}") from error

    diagnostic.connect_automatic()
    monitor.start()
    try:
        window.show()
    finally:
        shutdown()
