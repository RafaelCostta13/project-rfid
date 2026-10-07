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
from rfid_reader.services.station_configuration import StationConfigurationFeedback
from rfid_reader.services.waveshare_diagnostic import DiagnosticEvent
from rfid_reader.ui.components import (
    APP_BACKGROUND,
    ConnectionBar,
    ContentArea,
    Header,
    Sidebar,
)
from rfid_reader.ui.navigation import NavigationState, PageId
from rfid_reader.ui.pages import RFIDSettingsPage, SystemStatusPage
from rfid_reader.ui.waveshare_diagnostic_page import WaveshareDiagnosticPage


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
        automatic_mode_updates: queue.SimpleQueue[bool],
        on_close: Callable[[], None],
        on_start_inventory: Callable[[], object],
        on_stop_inventory: Callable[[], object],
        get_reader_settings: Callable[[], ReaderConnectionSettings],
        on_test_connection: Callable[[str, str, str], object],
        on_save_configuration: Callable[[str, str, str], object],
        get_waveshare_settings: Callable[[], WaveshareConnectionSettings],
        on_test_waveshare: Callable[[str, str, str, str, str, str], object],
        on_save_waveshare: Callable[[str, str, str, str, str, str], object],
        diagnostic_updates: queue.SimpleQueue[DiagnosticEvent],
        on_connect_diagnostic: Callable[[], None],
        on_disconnect_diagnostic: Callable[[], None],
        on_diagnostic_relay: Callable[[int, bool], None],
        on_connect_automatic: Callable[[], None] | None = None,
        is_automatic: Callable[[], bool] = lambda: False,
        *,
        get_station_dock: Callable[[], str] = lambda: "",
        on_save_station_dock: Callable[[str], StationConfigurationFeedback] | None = None,
        get_backend_url: Callable[[], str] = lambda: "",
        on_test_backend: Callable[[str], object] = lambda value: None,
        on_save_backend: Callable[[str], bool] = lambda value: False,
        backend_updates: queue.SimpleQueue[str] | None = None,
    ) -> None:
        self._updates = updates
        self._inventory_updates = inventory_updates
        self._lookup_updates = lookup_updates
        self._configuration_updates = configuration_updates
        self._waveshare_configuration_updates = waveshare_configuration_updates
        self._automatic_mode_updates = automatic_mode_updates
        self._diagnostic_updates = diagnostic_updates
        self._backend_updates = backend_updates or queue.SimpleQueue()
        self._on_disconnect_diagnostic = on_disconnect_diagnostic
        self._is_automatic = is_automatic
        self._lookup_session_id = 0
        self._lookup_summary = TagLookupSessionSummary()
        self._on_close = on_close
        self._get_reader_settings = get_reader_settings
        self._get_waveshare_settings = get_waveshare_settings
        self._get_station_dock = get_station_dock
        self._get_backend_url = get_backend_url
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
            self._open_waveshare_diagnostic,
            station_dock=get_station_dock(),
            on_save_station_dock=on_save_station_dock,
            backend_url=get_backend_url(),
            on_test_backend=on_test_backend,
            on_save_backend=on_save_backend,
        )
        self._diagnostic_page = WaveshareDiagnosticPage(
            self._content,
            on_connect_diagnostic,
            on_disconnect_diagnostic,
            on_diagnostic_relay,
            self._back_from_waveshare_diagnostic,
            on_connect_automatic,
        )
        self._content.add_page(
            PageId.SYSTEM_STATUS,
            self._status_page,
        )
        self._content.add_page(
            PageId.RFID_SETTINGS,
            self._settings_page,
        )
        self._content.add_page(PageId.WAVESHARE_DIAGNOSTIC, self._diagnostic_page)
        self._select_page(PageId.SYSTEM_STATUS)
        maximize_window(self._root)
        self._root.after_idle(maximize_window, self._root)
        self._root.after(100, self._drain_updates)

    def _select_page(self, page: PageId) -> None:
        if (
            self._navigation.current_page is PageId.WAVESHARE_DIAGNOSTIC
            and page is not PageId.WAVESHARE_DIAGNOSTIC
            and not self._is_automatic()
        ):
            self._on_disconnect_diagnostic()
            self._diagnostic_page.reset()
        self._navigation.select(page)
        self._sidebar.select(PageId.RFID_SETTINGS if page is PageId.WAVESHARE_DIAGNOSTIC else page)
        if page is PageId.RFID_SETTINGS:
            self._settings_page.set_settings(self._get_reader_settings())
            self._settings_page.set_waveshare_settings(self._get_waveshare_settings())
            self._settings_page.set_station_dock(self._get_station_dock())
            set_backend_url = getattr(self._settings_page, "set_backend_url", None)
            if set_backend_url is not None:
                set_backend_url(self._get_backend_url())
        self._content.show(page)

    def _open_waveshare_diagnostic(self) -> None:
        if self._is_automatic():
            self._select_page(PageId.WAVESHARE_DIAGNOSTIC)
            return
        while True:
            try:
                self._diagnostic_updates.get_nowait()
            except queue.Empty:
                break
        self._diagnostic_page.reset()
        self._select_page(PageId.WAVESHARE_DIAGNOSTIC)

    def _back_from_waveshare_diagnostic(self) -> None:
        self._select_page(PageId.RFID_SETTINGS)

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
        self._drain_backend_updates()
        self._drain_automatic_mode_updates()
        self._drain_diagnostic_updates()
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

    def _drain_backend_updates(self) -> None:
        while True:
            try:
                message = self._backend_updates.get_nowait()
            except queue.Empty:
                return
            self._settings_page.show_backend_feedback(message)

    def _drain_automatic_mode_updates(self) -> None:
        while True:
            try:
                enabled = self._automatic_mode_updates.get_nowait()
            except queue.Empty:
                return
            self._status_page.set_automatic_enabled(enabled)

    def _drain_diagnostic_updates(self) -> None:
        while True:
            try:
                event = self._diagnostic_updates.get_nowait()
            except queue.Empty:
                return
            if self._navigation.current_page is PageId.WAVESHARE_DIAGNOSTIC or self._is_automatic():
                self._diagnostic_page.apply(event)

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
