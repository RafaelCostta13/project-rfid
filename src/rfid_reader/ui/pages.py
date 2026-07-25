"""Páginas exibidas na área central da aplicação."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from datetime import UTC, datetime
from tkinter import ttk

from rfid_reader.domain import (
    ConnectionKind,
    ConnectionStatus,
    InventoryStatus,
    TagLookupKey,
    TagLookupResult,
    TagLookupStatus,
)
from rfid_reader.ui.components import (
    APP_BACKGROUND,
    CONNECTION_NAMES,
    HEADER_BACKGROUND,
    STATUS_COLORS,
    TEXT_MUTED,
    TEXT_PRIMARY,
)

TAG_TABLE_HEADINGS = (
    ("tag", "Tag"),
    ("status", "Status"),
    ("customer", "Cliente"),
    ("invoice_number", "Nota fiscal"),
    ("volume", "Volume"),
    ("order_number", "Pedido"),
    ("dock", "Doca"),
)
TAG_TABLE_COLUMNS = tuple(column for column, heading in TAG_TABLE_HEADINGS)


def tag_lookup_values(result: TagLookupResult) -> tuple[str, ...]:
    """Converte o modelo normalizado para a ordem visual da tabela."""

    return (
        result.tag,
        result.status.value,
        result.customer,
        result.invoice_number,
        result.volume,
        result.order_number,
        result.dock,
    )


class SystemStatusPage(tk.Frame):
    """Resumo do reader e das conexões atuais."""

    def __init__(
        self,
        parent: tk.Misc,
        reader_name: str,
        reader_host: str,
        reader_port: int,
        on_start_inventory: Callable[[], object],
        on_stop_inventory: Callable[[], object],
    ) -> None:
        super().__init__(parent, background=APP_BACKGROUND, padx=32, pady=28)
        self._status_labels: dict[ConnectionKind, tk.Label] = {}
        self._last_checked_label: tk.Label
        self._inventory_status_label: tk.Label
        self._start_button: tk.Button
        self._stop_button: tk.Button
        self._tag_table: ttk.Treeview
        self._tag_rows: dict[TagLookupKey, str] = {}
        self._next_tag_row = 0
        self._build(
            reader_name,
            reader_host,
            reader_port,
            on_start_inventory,
            on_stop_inventory,
        )

    def _build(
        self,
        reader_name: str,
        reader_host: str,
        reader_port: int,
        on_start_inventory: Callable[[], object],
        on_stop_inventory: Callable[[], object],
    ) -> None:
        tk.Label(
            self,
            text="Status do sistema",
            background=APP_BACKGROUND,
            foreground=TEXT_PRIMARY,
            font=("Segoe UI", 20, "bold"),
        ).pack(anchor="w")
        tk.Label(
            self,
            text="Informações atuais do reader e dos serviços essenciais.",
            background=APP_BACKGROUND,
            foreground=TEXT_MUTED,
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(4, 24))

        reader_card = tk.Frame(
            self,
            background=HEADER_BACKGROUND,
            padx=24,
            pady=20,
        )
        reader_card.pack(fill="x", pady=(0, 16))
        self._detail(reader_card, "Reader configurado", reader_name, 0)
        self._detail(reader_card, "Endereço LLRP", f"{reader_host}:{reader_port}", 1)

        connections = tk.Frame(self, background=APP_BACKGROUND)
        connections.pack(fill="x", pady=(0, 18))
        for column, kind in enumerate(ConnectionKind):
            connections.columnconfigure(column, weight=1, uniform="connection")
            card = tk.Frame(
                connections,
                background=HEADER_BACKGROUND,
                padx=22,
                pady=18,
            )
            card.grid(
                row=0,
                column=column,
                padx=(0, 8) if column == 0 else (8, 0),
                sticky="nsew",
            )
            tk.Label(
                card,
                text=CONNECTION_NAMES[kind],
                background=HEADER_BACKGROUND,
                foreground=TEXT_MUTED,
                font=("Segoe UI", 9),
            ).pack(anchor="w")
            status_label = tk.Label(
                card,
                text=ConnectionStatus.CHECKING.value,
                background=HEADER_BACKGROUND,
                foreground=STATUS_COLORS[ConnectionStatus.CHECKING],
                font=("Segoe UI", 12, "bold"),
            )
            status_label.pack(anchor="w", pady=(8, 0))
            self._status_labels[kind] = status_label

        self._last_checked_label = tk.Label(
            self,
            text="Última verificação: aguardando",
            background=APP_BACKGROUND,
            foreground=TEXT_MUTED,
            font=("Segoe UI", 9),
        )
        self._last_checked_label.pack(anchor="w")
        self._build_inventory(on_start_inventory, on_stop_inventory)

    def _build_inventory(
        self,
        on_start_inventory: Callable[[], object],
        on_stop_inventory: Callable[[], object],
    ) -> None:
        inventory = tk.Frame(
            self,
            background=HEADER_BACKGROUND,
            padx=24,
            pady=20,
        )
        inventory.pack(fill="both", expand=True, pady=(24, 0))
        controls = tk.Frame(inventory, background=HEADER_BACKGROUND)
        controls.pack(fill="x")
        tk.Label(
            controls,
            text="Inventário RFID manual",
            background=HEADER_BACKGROUND,
            foreground=TEXT_PRIMARY,
            font=("Segoe UI", 12, "bold"),
        ).pack(side="left")
        self._inventory_status_label = tk.Label(
            controls,
            text=f"● {InventoryStatus.STOPPED.value}",
            background=HEADER_BACKGROUND,
            foreground=TEXT_MUTED,
            font=("Segoe UI", 9, "bold"),
        )
        self._inventory_status_label.pack(side="right")

        actions = tk.Frame(inventory, background=HEADER_BACKGROUND)
        actions.pack(fill="x", pady=(18, 16))
        self._start_button = tk.Button(
            actions,
            text="Iniciar leitura",
            command=on_start_inventory,
            background="#16803C",
            foreground="#FFFFFF",
            activebackground="#126B33",
            activeforeground="#FFFFFF",
            borderwidth=0,
            cursor="hand2",
            font=("Segoe UI", 10, "bold"),
            padx=16,
            pady=9,
        )
        self._start_button.pack(side="left", padx=(0, 10))
        self._stop_button = tk.Button(
            actions,
            text="Parar leitura",
            command=on_stop_inventory,
            background="#B42318",
            foreground="#FFFFFF",
            activebackground="#921D14",
            activeforeground="#FFFFFF",
            borderwidth=0,
            cursor="hand2",
            font=("Segoe UI", 10, "bold"),
            padx=16,
            pady=9,
            state="disabled",
        )
        self._stop_button.pack(side="left")

        tk.Label(
            inventory,
            text="Etiquetas lidas",
            background=HEADER_BACKGROUND,
            foreground=TEXT_MUTED,
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(0, 7))
        list_container = tk.Frame(inventory, background=HEADER_BACKGROUND)
        list_container.pack(fill="both", expand=True)
        scrollbar = ttk.Scrollbar(list_container, orient="vertical")
        scrollbar.pack(side="right", fill="y")
        self._tag_table = ttk.Treeview(
            list_container,
            columns=TAG_TABLE_COLUMNS,
            show="headings",
            yscrollcommand=scrollbar.set,
        )
        for column, heading in TAG_TABLE_HEADINGS:
            self._tag_table.heading(column, text=heading)
        self._tag_table.column("tag", width=180, minwidth=140, stretch=True)
        self._tag_table.column("status", width=120, minwidth=110, stretch=False)
        self._tag_table.column("customer", width=180, minwidth=130, stretch=True)
        self._tag_table.column("invoice_number", width=110, minwidth=90, stretch=False)
        self._tag_table.column("volume", width=80, minwidth=65, stretch=False)
        self._tag_table.column("order_number", width=130, minwidth=100, stretch=False)
        self._tag_table.column("dock", width=80, minwidth=65, stretch=False)
        self._tag_table.tag_configure(TagLookupStatus.CONSULTING.value, foreground="#1D4ED8")
        self._tag_table.tag_configure(TagLookupStatus.FOUND.value, foreground="#16803C")
        self._tag_table.tag_configure(TagLookupStatus.NOT_FOUND.value, foreground="#B45309")
        self._tag_table.tag_configure(TagLookupStatus.ERROR.value, foreground="#B42318")
        self._tag_table.pack(side="left", fill="both", expand=True)
        scrollbar.configure(command=self._tag_table.yview)

    @staticmethod
    def _detail(
        parent: tk.Misc,
        label: str,
        value: str,
        column: int,
    ) -> None:
        detail = tk.Frame(parent, background=HEADER_BACKGROUND)
        detail.pack(side="left", fill="x", expand=True, padx=(0, 24) if column == 0 else 0)
        tk.Label(
            detail,
            text=label,
            background=HEADER_BACKGROUND,
            foreground=TEXT_MUTED,
            font=("Segoe UI", 9),
        ).pack(anchor="w")
        tk.Label(
            detail,
            text=value,
            background=HEADER_BACKGROUND,
            foreground=TEXT_PRIMARY,
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w", pady=(5, 0))

    def set_status(
        self,
        kind: ConnectionKind,
        status: ConnectionStatus,
        checked_at: datetime | None = None,
    ) -> None:
        """Atualiza o status da página a partir da fonte global."""

        timestamp = datetime.now(UTC) if checked_at is None else checked_at.astimezone(UTC)
        self._status_labels[kind].configure(
            text=status.value,
            foreground=STATUS_COLORS[status],
        )
        self._last_checked_label.configure(
            text=f"Última verificação: {timestamp:%d/%m/%Y %H:%M:%S} UTC"
        )

    def set_inventory_status(self, status: InventoryStatus) -> None:
        """Atualiza o estado e a disponibilidade dos controles."""

        colors = {
            InventoryStatus.STOPPED: TEXT_MUTED,
            InventoryStatus.READING: STATUS_COLORS[ConnectionStatus.CONNECTED],
            InventoryStatus.ERROR: STATUS_COLORS[ConnectionStatus.ERROR],
        }
        reading = status is InventoryStatus.READING
        self._inventory_status_label.configure(
            text=f"● {status.value}",
            foreground=colors[status],
        )
        self._start_button.configure(state="disabled" if reading else "normal")
        self._stop_button.configure(state="normal" if reading else "disabled")

    def clear_tags(self) -> None:
        """Remove todas as leituras da sessão anterior."""

        rows = self._tag_table.get_children()
        if rows:
            self._tag_table.delete(*rows)
        self._tag_rows.clear()
        self._next_tag_row = 0

    def set_tag_lookup(self, key: TagLookupKey, result: TagLookupResult) -> None:
        """Inclui ou atualiza o resultado associado à etiqueta correta."""

        values = tag_lookup_values(result)
        row_id = self._tag_rows.get(key)
        if row_id is None:
            self._next_tag_row += 1
            row_id = f"tag-{self._next_tag_row}"
            self._tag_rows[key] = row_id
            self._tag_table.insert(
                "",
                tk.END,
                iid=row_id,
                values=values,
                tags=(result.status.value,),
            )
        else:
            self._tag_table.item(row_id, values=values, tags=(result.status.value,))
        self._tag_table.see(row_id)


class RFIDSettingsPlaceholderPage(tk.Frame):
    """Espaço reservado sem operações reais de configuração."""

    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent, background=APP_BACKGROUND, padx=32, pady=28)
        tk.Label(
            self,
            text="Configurações RFID",
            background=APP_BACKGROUND,
            foreground=TEXT_PRIMARY,
            font=("Segoe UI", 20, "bold"),
        ).pack(anchor="w")
        tk.Label(
            self,
            text="As configurações do reader serão disponibilizadas em uma próxima etapa.",
            background=APP_BACKGROUND,
            foreground=TEXT_MUTED,
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(12, 0))
