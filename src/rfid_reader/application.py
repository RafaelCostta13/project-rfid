"""Composição da tela principal e dos serviços de conectividade."""

from __future__ import annotations

import logging
import queue

from rfid_reader.config import Settings
from rfid_reader.domain import (
    ConnectionKind,
    ConnectionStatus,
    InventoryCleared,
    InventoryEvent,
    InventoryStatus,
    InventoryStatusChanged,
    TagLookupEvent,
    TagReceived,
)
from rfid_reader.integrations import SharePointLookupClient
from rfid_reader.readers import ZebraFX9600Reader
from rfid_reader.services import (
    ConnectionMonitor,
    ManualInventoryService,
    ReaderConnectionChecker,
    TagLookupService,
)
from rfid_reader.services.internet import InternetConnectionChecker


class ApplicationError(RuntimeError):
    """Indica que a interface gráfica não pôde ser iniciada."""


def configure_logging(level: str) -> None:
    """Configura logs técnicos da aplicação."""

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def run_application(settings: Settings) -> None:
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
    reader = ZebraFX9600Reader(
        settings.reader_host,
        settings.reader_port,
        settings.reader_name,
        settings.antennas[0],
        settings.connection_timeout_seconds,
    )
    lookup_client = SharePointLookupClient(
        settings.sharepoint_lookup_url,
        settings.sharepoint_lookup_timeout_seconds,
    )
    lookup = TagLookupService(
        lookup_client,
        settings.sharepoint_lookup_queue_size,
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
    monitor = ConnectionMonitor(
        {
            ConnectionKind.RFID: ReaderConnectionChecker(reader),
            ConnectionKind.INTERNET: InternetConnectionChecker(settings.connection_timeout_seconds),
        },
        settings.status_check_interval_seconds,
        lambda kind, status: updates.put((kind, status)),
    )

    def stop_inventory() -> bool:
        lookup.stop_accepting()
        return inventory.stop()

    def shutdown() -> None:
        stop_inventory()
        monitor.stop()
        inventory.close()
        lookup.close()

    try:
        window = MainWindow(
            updates,
            inventory_updates,
            lookup_updates,
            shutdown,
            inventory.start,
            stop_inventory,
            reader_name=settings.reader_name,
            reader_host=settings.reader_host,
            reader_port=settings.reader_port,
        )
    except Exception as error:
        monitor.stop()
        lookup.close()
        inventory.close()
        raise ApplicationError(f"não foi possível criar a janela principal: {error}") from error

    monitor.start()
    try:
        window.show()
    finally:
        shutdown()
