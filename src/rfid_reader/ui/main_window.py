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
    ReaderConfigurationFeedback,
    ReaderConnectionSettings,
    TagLookupChanged,
    TagLookupEvent,
    TagLookupSessionStarted,
    TagLookupSessionSummary,
    WaveshareConfigurationFeedback,
    WaveshareConnectionSettings,
)
from rfid_reader.ui.components import (
    APP_BACKGROUND,
    ConnectionBar,
    ContentArea,
    Header,
    Sidebar,
)
from rfid_reader.ui.navigation import NavigationState, PageId
from rfid_reader.ui.pages import RFIDSettingsPage, SystemStatusPage


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
        lookup_updates: queue.SimpleQueue[TagLookupEvent],
        configuration_updates: queue.SimpleQueue[ReaderConfigurationFeedback],
        waveshare_configuration_updates: queue.SimpleQueue[WaveshareConfigurationFeedback],
        on_close: Callable[[], None],
        on_start_inventory: Callable[[], object],
        on_stop_inventory: Callable[[], object],
        get_reader_settings: Callable[[], ReaderConnectionSettings],
        on_test_connection: Callable[[str, str, str], object],
        on_save_configuration: Callable[[str, str, str], object],
        get_waveshare_settings: Callable[[], WaveshareConnectionSettings],
        on_test_waveshare: Callable[[str, str, str, str, str, str], object],
        on_save_waveshare: Callable[[str, str, str, str, str, str], object],
    ) -> None:
        self._updates = updates
        self._inventory_updates = inventory_updates
        self._lookup_updates = lookup_updates
        self._configuration_updates = configuration_updates
        self._waveshare_configuration_updates = waveshare_configuration_updates
        self._lookup_session_id = 0
        self._lookup_summary = TagLookupSessionSummary()
        self._on_close = on_close
        self._get_reader_settings = get_reader_settings
        self._get_waveshare_settings = get_waveshare_settings
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
            on_start_inventory,
            on_stop_inventory,
        )
        self._settings_page = RFIDSettingsPage(
            self._content,
            get_reader_settings(),
            on_test_connection,
            on_save_configuration,
            get_waveshare_settings(),
            on_test_waveshare,
            on_save_waveshare,
        )
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
        if page is PageId.RFID_SETTINGS:
            self._settings_page.set_settings(self._get_reader_settings())
            self._settings_page.set_waveshare_settings(self._get_waveshare_settings())
        self._content.show(page)

    def _drain_updates(self) -> None:
        while True:
            try:
                kind, status = self._updates.get_nowait()
            except queue.Empty:
                break
            self._set_status(kind, status)
        self._drain_inventory_updates()
        self._drain_lookup_updates()
        self._drain_configuration_updates()
        self._drain_waveshare_configuration_updates()
        if not self._closing:
            self._root.after(100, self._drain_updates)

    def _drain_inventory_updates(self) -> None:
        while True:
            try:
                event = self._inventory_updates.get_nowait()
            except queue.Empty:
                return
            if isinstance(event, InventoryCleared):
                self._reset_lookup_view()
            elif isinstance(event, InventoryStatusChanged):
                self._status_page.set_inventory_status(event.status)

    def _drain_lookup_updates(self) -> None:
        while True:
            try:
                event = self._lookup_updates.get_nowait()
            except queue.Empty:
                return
            if isinstance(event, TagLookupSessionStarted):
                self._lookup_session_id = event.session_id
                self._reset_lookup_view()
            elif (
                isinstance(event, TagLookupChanged) and event.session_id == self._lookup_session_id
            ):
                if self._lookup_summary.update(event.result):
                    self._status_page.set_tag_lookup(event.result)
                    self._status_page.set_summary(self._lookup_summary.total)

    def _reset_lookup_view(self) -> None:
        self._lookup_summary.reset()
        self._status_page.clear_tags()
        self._status_page.set_summary(self._lookup_summary.total)

    def _drain_configuration_updates(self) -> None:
        while True:
            try:
                event = self._configuration_updates.get_nowait()
            except queue.Empty:
                return
            self._settings_page.apply_feedback(event)

    def _drain_waveshare_configuration_updates(self) -> None:
        while True:
            try:
                event = self._waveshare_configuration_updates.get_nowait()
            except queue.Empty:
                return
            self._settings_page.apply_waveshare_feedback(event)

    def _set_status(self, kind: ConnectionKind, status: ConnectionStatus) -> None:
        self._connection_bar.set_status(kind, status)

    def _close(self) -> None:
        if self._closing:
            return
        self._closing = True
        self._on_close()
        self._root.destroy()

    def show(self) -> None:
        """Exibe a janela até o encerramento pelo usuário."""

        self._root.mainloop()
