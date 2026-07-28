"""Páginas exibidas na área central da aplicação."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from tkinter import ttk

from rfid_reader.domain import (
    ConnectionStatus,
    InventoryStatus,
    ReaderConfigurationAction,
    ReaderConfigurationFeedback,
    ReaderConfigurationOutcome,
    ReaderConnectionSettings,
    TagLookupResult,
    TagLookupStatus,
)
from rfid_reader.ui.components import (
    APP_BACKGROUND,
    HEADER_BACKGROUND,
    STATUS_COLORS,
    TEXT_MUTED,
    TEXT_PRIMARY,
)

START_PAGE_TITLE = "Start"
SUMMARY_CARD_TITLE = "EPCs encontrados"
RFID_SETTINGS_FIELDS = ("Nome do reader", "Endereço IP", "Porta")
TEST_CONNECTION_BUTTON_TEXT = "Testar conexão"
SAVE_CONFIGURATION_BUTTON_TEXT = "Salvar configurações"
TAG_TABLE_HEADINGS = (
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
        result.status.value,
        result.customer,
        result.invoice_number,
        result.volume,
        result.order_number,
        result.dock,
    )


class SystemStatusPage(tk.Frame):
    """Controles e resultados da sessão atual de leitura."""

    def __init__(
        self,
        parent: tk.Misc,
        on_start_inventory: Callable[[], object],
        on_stop_inventory: Callable[[], object],
    ) -> None:
        super().__init__(parent, background=APP_BACKGROUND, padx=32, pady=28)
        self._found_count_label: tk.Label
        self._inventory_status_label: tk.Label
        self._start_button: tk.Button
        self._stop_button: tk.Button
        self._tag_table: ttk.Treeview
        self._tag_rows: dict[str, str] = {}
        self._next_tag_row = 0
        self._build(on_start_inventory, on_stop_inventory)

    def _build(
        self,
        on_start_inventory: Callable[[], object],
        on_stop_inventory: Callable[[], object],
    ) -> None:
        tk.Label(
            self,
            text=START_PAGE_TITLE,
            background=APP_BACKGROUND,
            foreground=TEXT_PRIMARY,
            font=("Segoe UI", 20, "bold"),
        ).pack(anchor="w")
        tk.Label(
            self,
            text="Resumo da sessão atual de leitura.",
            background=APP_BACKGROUND,
            foreground=TEXT_MUTED,
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(4, 24))
        self._build_summary()
        self._build_inventory(on_start_inventory, on_stop_inventory)

    def _build_summary(self) -> None:
        summary = tk.Frame(self, background=APP_BACKGROUND)
        summary.pack(fill="x", pady=(0, 16))
        summary.columnconfigure(0, weight=1)
        card = tk.Frame(
            summary,
            background=HEADER_BACKGROUND,
            padx=24,
            pady=20,
        )
        card.grid(row=0, column=0, sticky="nsew")
        tk.Label(
            card,
            text=SUMMARY_CARD_TITLE,
            background=HEADER_BACKGROUND,
            foreground=TEXT_MUTED,
            font=("Segoe UI", 10),
        ).pack(anchor="w")
        self._found_count_label = tk.Label(
            card,
            text="0",
            background=HEADER_BACKGROUND,
            foreground=TEXT_PRIMARY,
            font=("Segoe UI", 24, "bold"),
        )
        self._found_count_label.pack(pady=(14, 0))

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
        inventory.pack(fill="both", expand=True)
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
        self._tag_table.column("status", width=120, minwidth=110, stretch=False)
        self._tag_table.column("customer", width=180, minwidth=130, stretch=True)
        self._tag_table.column("invoice_number", width=110, minwidth=90, stretch=False)
        self._tag_table.column("volume", width=80, minwidth=65, stretch=False)
        self._tag_table.column("order_number", width=130, minwidth=100, stretch=False)
        self._tag_table.column("dock", width=80, minwidth=65, stretch=False)
        self._tag_table.tag_configure(TagLookupStatus.FOUND.value, foreground="#16803C")
        self._tag_table.pack(side="left", fill="both", expand=True)
        scrollbar.configure(command=self._tag_table.yview)

    def set_summary(self, found: int) -> None:
        """Exibe o total calculado pela coleção de encontrados da sessão."""

        self._found_count_label.configure(text=str(found))

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

    def set_tag_lookup(self, result: TagLookupResult) -> None:
        """Inclui ou atualiza um resultado encontrado pelo EPC técnico."""

        values = tag_lookup_values(result)
        row_id = self._tag_rows.get(result.epc)
        if row_id is None:
            self._next_tag_row += 1
            row_id = f"tag-{self._next_tag_row}"
            self._tag_rows[result.epc] = row_id
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


class RFIDSettingsPage(tk.Frame):
    """Formulário para testar e salvar a conexão do reader."""

    def __init__(
        self,
        parent: tk.Misc,
        settings: ReaderConnectionSettings,
        on_test_connection: Callable[[str, str, str], object],
        on_save: Callable[[str, str, str], object],
    ) -> None:
        super().__init__(parent, background=APP_BACKGROUND, padx=32, pady=28)
        self._reader_name_var = tk.StringVar(value=settings.name)
        self._reader_host_var = tk.StringVar(value=settings.host)
        self._reader_port_var = tk.StringVar(value=str(settings.port))
        self._on_test_connection = on_test_connection
        self._on_save = on_save
        self._test_button: tk.Button
        self._feedback_label: tk.Label
        self._build()

    def _build(self) -> None:
        tk.Label(
            self,
            text="Configurações RFID",
            background=APP_BACKGROUND,
            foreground=TEXT_PRIMARY,
            font=("Segoe UI", 20, "bold"),
        ).pack(anchor="w")
        tk.Label(
            self,
            text="Altere, teste e salve os dados usados para conectar ao reader.",
            background=APP_BACKGROUND,
            foreground=TEXT_MUTED,
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(4, 24))

        form = tk.Frame(
            self,
            background=HEADER_BACKGROUND,
            padx=24,
            pady=22,
        )
        form.pack(fill="x")
        variables = (
            self._reader_name_var,
            self._reader_host_var,
            self._reader_port_var,
        )
        for row, (label, variable) in enumerate(zip(RFID_SETTINGS_FIELDS, variables, strict=True)):
            tk.Label(
                form,
                text=label,
                background=HEADER_BACKGROUND,
                foreground=TEXT_MUTED,
                font=("Segoe UI", 9),
            ).grid(row=row * 2, column=0, sticky="w", pady=(0 if row == 0 else 14, 6))
            tk.Entry(
                form,
                textvariable=variable,
                background="#FFFFFF",
                foreground=TEXT_PRIMARY,
                relief="solid",
                borderwidth=1,
                font=("Segoe UI", 11),
            ).grid(row=row * 2 + 1, column=0, sticky="ew")
        form.columnconfigure(0, weight=1)

        actions = tk.Frame(form, background=HEADER_BACKGROUND)
        actions.grid(row=6, column=0, sticky="w", pady=(22, 0))
        self._test_button = tk.Button(
            actions,
            text=TEST_CONNECTION_BUTTON_TEXT,
            command=self._request_test,
            background="#1D4ED8",
            foreground="#FFFFFF",
            activebackground="#1E40AF",
            activeforeground="#FFFFFF",
            borderwidth=0,
            cursor="hand2",
            font=("Segoe UI", 10, "bold"),
            padx=16,
            pady=9,
        )
        self._test_button.pack(side="left", padx=(0, 10))
        tk.Button(
            actions,
            text=SAVE_CONFIGURATION_BUTTON_TEXT,
            command=self._request_save,
            background="#16803C",
            foreground="#FFFFFF",
            activebackground="#126B33",
            activeforeground="#FFFFFF",
            borderwidth=0,
            cursor="hand2",
            font=("Segoe UI", 10, "bold"),
            padx=16,
            pady=9,
        ).pack(side="left")

        self._feedback_label = tk.Label(
            form,
            text="",
            background=HEADER_BACKGROUND,
            foreground=TEXT_MUTED,
            font=("Segoe UI", 10, "bold"),
            wraplength=680,
            justify="left",
        )
        self._feedback_label.grid(row=7, column=0, sticky="w", pady=(18, 0))

    def _values(self) -> tuple[str, str, str]:
        return (
            self._reader_name_var.get(),
            self._reader_host_var.get(),
            self._reader_port_var.get(),
        )

    def _request_test(self) -> None:
        self._on_test_connection(*self._values())

    def _request_save(self) -> None:
        self._on_save(*self._values())

    def set_settings(self, settings: ReaderConnectionSettings) -> None:
        """Preenche o formulário com a configuração atual em memória."""

        self._reader_name_var.set(settings.name)
        self._reader_host_var.set(settings.host)
        self._reader_port_var.set(str(settings.port))

    def apply_feedback(self, event: ReaderConfigurationFeedback) -> None:
        """Apresenta na thread gráfica o evento produzido pelo serviço."""

        colors = {
            ReaderConfigurationOutcome.IN_PROGRESS: "#1D4ED8",
            ReaderConfigurationOutcome.SUCCESS: "#16803C",
            ReaderConfigurationOutcome.ERROR: "#B42318",
        }
        self._feedback_label.configure(
            text=event.message,
            foreground=colors[event.outcome],
        )
        if event.action is ReaderConfigurationAction.TEST:
            self._test_button.configure(
                state=(
                    "disabled"
                    if event.outcome is ReaderConfigurationOutcome.IN_PROGRESS
                    else "normal"
                )
            )
        if event.settings is not None:
            self.set_settings(event.settings)
