"""Janela principal e composição do layout persistente."""

from __future__ import annotations

import queue
import sys
import tkinter as tk
from collections.abc import Callable

from rfid_reader.domain import (
    ConnectionKind,
    ConnectionStatus,
    InventoryCleared,
    InventoryEvent,
    InventoryStatusChanged,
    TagReceived,
)
from rfid_reader.ui.components import (
    APP_BACKGROUND,
    ConnectionBar,
    ContentArea,
    Header,
    Sidebar,
)
from rfid_reader.ui.navigation import NavigationState, PageId
from rfid_reader.ui.pages import RFIDSettingsPlaceholderPage, SystemStatusPage


def maximize_window(root: tk.Tk) -> None:
    """Maximiza a janela preservando os controles do sistema operacional."""

    try:
        if sys.platform.startswith("win"):
            root.state("zoomed")
        else:
            root.attributes("-zoomed", True)
    except tk.TclError:
        root.state("zoomed")


class MainWindow:
    """Compõe a estrutura global e consome atualizações thread-safe."""

    def __init__(
        self,
        updates: queue.SimpleQueue[tuple[ConnectionKind, ConnectionStatus]],
        inventory_updates: queue.SimpleQueue[InventoryEvent],
        on_close: Callable[[], None],
        on_start_inventory: Callable[[], object],
        on_stop_inventory: Callable[[], object],
        *,
        reader_name: str,
        reader_host: str,
        reader_port: int,
    ) -> None:
        self._updates = updates
        self._inventory_updates = inventory_updates
        self._on_close = on_close
        self._closing = False
        self._navigation = NavigationState()
        self._root = tk.Tk()
        self._root.title("Leitor RFID")
        self._root.geometry("1100x700")
        self._root.minsize(900, 600)
        self._root.configure(background=APP_BACKGROUND)
        self._root.protocol("WM_DELETE_WINDOW", self._close)
        self._root.grid_columnconfigure(1, weight=1)
        self._root.grid_rowconfigure(2, weight=1)

        self._header = Header(self._root)
        self._header.grid(row=0, column=0, columnspan=2, sticky="ew")
        self._connection_bar = ConnectionBar(self._root)
        self._connection_bar.grid(row=1, column=0, columnspan=2, sticky="ew")
        self._sidebar = Sidebar(self._root, self._select_page)
        self._sidebar.grid(row=2, column=0, sticky="nsw")

        self._content = ContentArea(self._root)
        self._content.grid(row=2, column=1, sticky="nsew")
        self._status_page = SystemStatusPage(
            self._content,
            reader_name,
            reader_host,
            reader_port,
            on_start_inventory,
            on_stop_inventory,
        )
        self._settings_page = RFIDSettingsPlaceholderPage(self._content)
        self._content.add_page(
            PageId.SYSTEM_STATUS,
            self._status_page,
        )
        self._content.add_page(
            PageId.RFID_SETTINGS,
            self._settings_page,
        )
        self._select_page(PageId.SYSTEM_STATUS)
        maximize_window(self._root)
        self._root.after_idle(maximize_window, self._root)
        self._root.after(100, self._drain_updates)

    def _select_page(self, page: PageId) -> None:
        self._navigation.select(page)
        self._sidebar.select(page)
        self._content.show(page)

    def _drain_updates(self) -> None:
        while True:
            try:
                kind, status = self._updates.get_nowait()
            except queue.Empty:
                break
            self._set_status(kind, status)
        self._drain_inventory_updates()
        if not self._closing:
            self._root.after(100, self._drain_updates)

    def _drain_inventory_updates(self) -> None:
        while True:
            try:
                event = self._inventory_updates.get_nowait()
            except queue.Empty:
                return
            if isinstance(event, InventoryCleared):
                self._status_page.clear_tags()
            elif isinstance(event, InventoryStatusChanged):
                self._status_page.set_inventory_status(event.status)
            elif isinstance(event, TagReceived):
                self._status_page.add_tag(event.tag)

    def _set_status(self, kind: ConnectionKind, status: ConnectionStatus) -> None:
        self._connection_bar.set_status(kind, status)
        self._status_page.set_status(kind, status)

    def _close(self) -> None:
        if self._closing:
            return
        self._closing = True
        self._on_close()
        self._root.destroy()

    def show(self) -> None:
        """Exibe a janela até o encerramento pelo usuário."""

        self._root.mainloop()
