"""Componentes persistentes do layout principal."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from functools import partial

from rfid_reader.domain import ConnectionKind, ConnectionStatus
from rfid_reader.ui.navigation import PageId

APP_BACKGROUND = "#F4F6F8"
HEADER_BACKGROUND = "#FFFFFF"
SIDEBAR_BACKGROUND = "#1F2937"
SIDEBAR_SELECTED_BACKGROUND = "#334E68"
TEXT_PRIMARY = "#172B4D"
TEXT_MUTED = "#64748B"
STATUS_COLORS = {
    ConnectionStatus.CHECKING: "#B26A00",
    ConnectionStatus.CONNECTED: "#16803C",
    ConnectionStatus.DISCONNECTED: "#B42318",
    ConnectionStatus.ERROR: "#C2410C",
}
CONNECTION_NAMES = {
    ConnectionKind.RFID: "RFID",
    ConnectionKind.INTERNET: "Internet",
}
PAGE_NAMES = {
    PageId.SYSTEM_STATUS: "Start",
    PageId.RFID_SETTINGS: "Configurações RFID",
}


class Header(tk.Frame):
    """Cabeçalho principal persistente."""

    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(
            parent,
            background=HEADER_BACKGROUND,
            height=64,
            padx=28,
            pady=16,
        )
        self.grid_propagate(False)
        tk.Label(
            self,
            text="Leitor RFID",
            background=HEADER_BACKGROUND,
            foreground=TEXT_PRIMARY,
            font=("Segoe UI", 18, "bold"),
        ).pack(anchor="w")


class ConnectionBar(tk.Frame):
    """Subcabeçalho com os estados globais das conexões."""

    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(
            parent,
            background="#EEF2F6",
            height=44,
            padx=28,
            pady=10,
        )
        self.grid_propagate(False)
        self._labels: dict[ConnectionKind, tk.Label] = {}
        for kind in ConnectionKind:
            label = tk.Label(
                self,
                text=self._status_text(kind, ConnectionStatus.CHECKING),
                background="#EEF2F6",
                foreground=STATUS_COLORS[ConnectionStatus.CHECKING],
                font=("Segoe UI", 9, "bold"),
            )
            label.pack(side="left", padx=(0, 32))
            self._labels[kind] = label

    def set_status(self, kind: ConnectionKind, status: ConnectionStatus) -> None:
        """Atualiza a indicação textual e visual de uma conexão."""

        self._labels[kind].configure(
            text=self._status_text(kind, status),
            foreground=STATUS_COLORS[status],
        )

    @staticmethod
    def _status_text(kind: ConnectionKind, status: ConnectionStatus) -> str:
        return f"● {CONNECTION_NAMES[kind]}: {status.value}"


class Sidebar(tk.Frame):
    """Menu lateral persistente com destaque da página atual."""

    def __init__(
        self,
        parent: tk.Misc,
        on_select: Callable[[PageId], None],
    ) -> None:
        super().__init__(
            parent,
            background=SIDEBAR_BACKGROUND,
            width=240,
            padx=12,
            pady=20,
        )
        self.grid_propagate(False)
        self._buttons: dict[PageId, tk.Button] = {}
        for page in PageId:
            button = tk.Button(
                self,
                text=PAGE_NAMES[page],
                command=partial(on_select, page),
                anchor="w",
                background=SIDEBAR_BACKGROUND,
                foreground="#CBD5E1",
                activebackground=SIDEBAR_SELECTED_BACKGROUND,
                activeforeground="#FFFFFF",
                borderwidth=0,
                cursor="hand2",
                font=("Segoe UI", 10),
                padx=16,
                pady=12,
            )
            button.pack(fill="x", pady=(0, 6))
            self._buttons[page] = button

    def select(self, selected_page: PageId) -> None:
        """Destaca apenas a opção correspondente à página aberta."""

        for page, button in self._buttons.items():
            is_selected = page is selected_page
            button.configure(
                background=(SIDEBAR_SELECTED_BACKGROUND if is_selected else SIDEBAR_BACKGROUND),
                foreground="#FFFFFF" if is_selected else "#CBD5E1",
                font=("Segoe UI", 10, "bold" if is_selected else "normal"),
            )


class ContentArea(tk.Frame):
    """Contêiner capaz de alternar o conteúdo sem recriar o layout global."""

    def __init__(
        self,
        parent: tk.Misc,
    ) -> None:
        super().__init__(parent, background=APP_BACKGROUND)
        self._pages: dict[PageId, tk.Frame] = {}
        self._visible_page: tk.Frame | None = None

    def add_page(self, page: PageId, frame: tk.Frame) -> None:
        """Registra uma página criada dentro desta área."""

        self._pages[page] = frame

    def show(self, page: PageId) -> None:
        """Exibe somente a página solicitada dentro da área central."""

        if self._visible_page is not None:
            self._visible_page.pack_forget()
        self._visible_page = self._pages[page]
        self._visible_page.pack(fill="both", expand=True)
