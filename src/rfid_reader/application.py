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
from rfid_reader.integrations import PowerAutomateSyncClient, PymodbusWaveshareConnectionTester
from rfid_reader.integrations.waveshare_modbus import WaveshareSerialGate
from rfid_reader.readers import ZebraFX9600Reader
from rfid_reader.services import (
    ConnectionMonitor,
    DotEnvReaderConfigurationStore,
    DotEnvWaveshareConfigurationStore,
    LocalDatabaseConnectionChecker,
    LocalTagRepository,
    ManualInventoryService,
    ReaderConfigurationService,
    ReaderConnectionChecker,
    SyncConnectionChecker,
    TagLookupService,
    TagSyncService,
    WaveshareConfigurationService,
)
from rfid_reader.services.automatic_inventory import AutomaticInventoryController
from rfid_reader.services.internet import InternetConnectionChecker
from rfid_reader.services.station_configuration import (
    StationConfigurationFeedback,
    StationConfigurationService,
)
from rfid_reader.services.tag_sync import TagSyncLocalError, TagSyncRemoteError
from rfid_reader.services.waveshare_connection import WaveshareConnectionChecker
from rfid_reader.services.waveshare_diagnostic import DiagnosticEvent, WaveshareDiagnosticService


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
    automatic_mode_updates: queue.SimpleQueue[bool] = queue.SimpleQueue()
    reader = ZebraFX9600Reader(
        settings.reader_host,
        settings.reader_port,
        settings.reader_name,
        settings.antennas[0],
        settings.connection_timeout_seconds,
    )
    local_tags = LocalTagRepository(settings.local_database_path)
    local_tags.initialize()
    station_configuration = StationConfigurationService(
        settings, DotEnvReaderConfigurationStore(configuration_path)
    )
    sync_client = PowerAutomateSyncClient(
        settings.sharepoint_sync_url,
        settings.sharepoint_sync_timeout_seconds,
    )
    tag_sync = TagSyncService(sync_client, local_tags, station_configuration.current)
    lookup = TagLookupService(
        local_tags,
        station_configuration.current,
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
    database_sync_commands = ThreadPoolExecutor(max_workers=1, thread_name_prefix="database-sync")

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
            ConnectionKind.DATABASE: LocalDatabaseConnectionChecker(
                local_tags,
                station_configuration.current,
            ),
            ConnectionKind.SYNC: SyncConnectionChecker(
                tag_sync,
                lambda: monitor.statuses()[ConnectionKind.INTERNET],
                settings.sync_check_interval_seconds,
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
        database_sync_commands.shutdown(wait=True, cancel_futures=True)
        inventory_commands.shutdown(wait=True, cancel_futures=True)
        reader_configuration.close()
        waveshare_configuration.close()
        inventory.close()
        lookup.close()

    def refresh_database_status() -> None:
        on_connection_status(
            ConnectionKind.DATABASE,
            (
                ConnectionStatus.CONNECTED
                if local_tags.is_operational(station_configuration.current())
                else ConnectionStatus.ERROR
            ),
        )

    def sync_current_dock() -> None:
        try:
            tag_sync.sync_current_dock()
        except TagSyncRemoteError:
            on_connection_status(ConnectionKind.SYNC, ConnectionStatus.ERROR)
        except TagSyncLocalError:
            on_connection_status(ConnectionKind.SYNC, ConnectionStatus.CONNECTED)
        except Exception:
            on_connection_status(ConnectionKind.SYNC, ConnectionStatus.ERROR)
        else:
            on_connection_status(ConnectionKind.SYNC, ConnectionStatus.CONNECTED)
        refresh_database_status()

    def save_station_dock(dock: str) -> StationConfigurationFeedback:
        feedback = station_configuration.save(dock)
        if feedback.success:
            refresh_database_status()
            database_sync_commands.submit(sync_current_dock)
        return feedback

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
        )
    except Exception as error:
        inventory_commands.shutdown(wait=True, cancel_futures=True)
        database_sync_commands.shutdown(wait=True, cancel_futures=True)
        monitor.stop()
        reader_configuration.close()
        waveshare_configuration.close()
        diagnostic.close()
        lookup.close()
        inventory.close()
        raise ApplicationError(f"não foi possível criar a janela principal: {error}") from error

    diagnostic.connect_automatic()
    monitor.start()
    database_sync_commands.submit(sync_current_dock)
    try:
        window.show()
    finally:
        shutdown()
