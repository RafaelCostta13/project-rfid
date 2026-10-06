"""Tela de diagnóstico manual da placa Waveshare."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from functools import partial

from rfid_reader.services.waveshare_diagnostic import DiagnosticEvent, DiagnosticEventKind
from rfid_reader.ui.components import APP_BACKGROUND, HEADER_BACKGROUND, TEXT_MUTED, TEXT_PRIMARY

ACTIVE_COLOR = "#16803C"
INACTIVE_COLOR = "#B42318"


def relay_grid_position(channel: int) -> tuple[int, int]:
    """Distribui CH1–CH8 em duas colunas de quatro canais."""

    if channel not in range(1, 9):
        raise ValueError("Canal de relé inválido.")
    return (channel - 1) % 4 + 1, (channel - 1) // 4 * 4


class WaveshareDiagnosticPage(tk.Frame):
    """Mostra estados confirmados e envia apenas ações manuais."""

    def __init__(
        self,
        parent: tk.Misc,
        on_connect: Callable[[], None],
        on_disconnect: Callable[[], None],
        on_relay: Callable[[int, bool], None],
        on_back: Callable[[], None],
        on_automatic: Callable[[], None] | None = None,
    ) -> None:
        super().__init__(parent, background=APP_BACKGROUND, padx=32, pady=16)
        self._connected = False
        self._connecting = False
        self._automatic = False
        self._status: tk.Label
        self._message: tk.Label
        self._connect_button: tk.Button
        self._disconnect_button: tk.Button
        self._input_labels: dict[int, tk.Label] = {}
        self._relay_labels: dict[int, tk.Label] = {}
        self._relay_buttons: list[tk.Button] = []
        self._build(on_connect, on_disconnect, on_relay, on_back)
        self._automatic_button: tk.Button | None = None
        if on_automatic is not None:
            self._automatic_button = tk.Button(
                self,
                text="Conectar em modo automático",
                command=on_automatic,
            )
            self._automatic_button.pack(anchor="w", pady=8)

    def _build(
        self,
        on_connect: Callable[[], None],
        on_disconnect: Callable[[], None],
        on_relay: Callable[[int, bool], None],
        on_back: Callable[[], None],
    ) -> None:
        tk.Label(
            self,
            text="Teste da Waveshare",
            background=APP_BACKGROUND,
            foreground=TEXT_PRIMARY,
            font=("Segoe UI", 20, "bold"),
        ).pack(anchor="w")
        tk.Button(
            self,
            text="Voltar",
            command=on_back,
            background="#E2E8F0",
            foreground=TEXT_PRIMARY,
            borderwidth=0,
            padx=16,
            pady=8,
        ).pack(anchor="w", pady=(8, 10))
        panel = tk.Frame(self, background=HEADER_BACKGROUND, padx=24, pady=12)
        panel.pack(fill="x", pady=(0, 10))
        self._status = tk.Label(
            panel,
            text="● Desconectado",
            background=HEADER_BACKGROUND,
            foreground=TEXT_MUTED,
            font=("Segoe UI", 11, "bold"),
        )
        self._status.pack(anchor="w")
        actions = tk.Frame(panel, background=HEADER_BACKGROUND)
        actions.pack(anchor="w", pady=(12, 0))
        self._connect_button = tk.Button(
            actions,
            text="Conectar",
            command=on_connect,
            background="#1D4ED8",
            foreground="#FFFFFF",
            borderwidth=0,
            padx=16,
            pady=8,
        )
        self._connect_button.pack(side="left", padx=(0, 10))
        self._disconnect_button = tk.Button(
            actions,
            text="Desconectar",
            command=on_disconnect,
            background="#B42318",
            foreground="#FFFFFF",
            borderwidth=0,
            padx=16,
            pady=8,
            state="disabled",
        )
        self._disconnect_button.pack(side="left")
        self._message = tk.Label(
            panel,
            text="",
            background=HEADER_BACKGROUND,
            foreground=INACTIVE_COLOR,
            font=("Segoe UI", 10),
            wraplength=650,
            justify="left",
        )
        self._message.pack(anchor="w", pady=(10, 0))

        inputs = tk.Frame(self, background=HEADER_BACKGROUND, padx=24, pady=12)
        inputs.pack(fill="x", pady=(0, 10))
        tk.Label(
            inputs,
            text="Entradas digitais",
            background=HEADER_BACKGROUND,
            foreground=TEXT_PRIMARY,
            font=("Segoe UI", 12, "bold"),
        ).grid(row=0, column=0, columnspan=5, sticky="w", pady=(0, 12))
        for channel in range(1, 6):
            cell = tk.Frame(inputs, background=HEADER_BACKGROUND)
            cell.grid(row=1, column=channel - 1, sticky="w", padx=(0, 32))
            tk.Label(
                cell,
                text=f"D{channel}",
                background=HEADER_BACKGROUND,
                foreground=TEXT_PRIMARY,
                font=("Segoe UI", 10, "bold"),
            ).pack(anchor="w")
            label = tk.Label(
                cell,
                text="Desconhecido",
                background=HEADER_BACKGROUND,
                foreground=TEXT_MUTED,
            )
            label.pack(anchor="w")
            self._input_labels[channel] = label

        relays = tk.Frame(self, background=HEADER_BACKGROUND, padx=24, pady=12)
        relays.pack(fill="both", expand=True)
        tk.Label(
            relays,
            text="Teste dos relés",
            background=HEADER_BACKGROUND,
            foreground=TEXT_PRIMARY,
            font=("Segoe UI", 12, "bold"),
        ).grid(row=0, column=0, columnspan=8, sticky="w", pady=(0, 8))
        for channel in range(1, 9):
            row, group_column = relay_grid_position(channel)
            tk.Label(
                relays,
                text=f"CH{channel}",
                background=HEADER_BACKGROUND,
                foreground=TEXT_PRIMARY,
                font=("Segoe UI", 10, "bold"),
            ).grid(row=row, column=group_column, sticky="w", pady=2, padx=(0, 12))
            label = tk.Label(
                relays,
                text="Desconhecido",
                background=HEADER_BACKGROUND,
                foreground=TEXT_MUTED,
                width=12,
                anchor="w",
            )
            label.grid(row=row, column=group_column + 1, sticky="w")
            self._relay_labels[channel] = label
            for offset, enabled, text, color in (
                (2, True, "Ligar", ACTIVE_COLOR),
                (3, False, "Desligar", INACTIVE_COLOR),
            ):
                button = tk.Button(
                    relays,
                    text=text,
                    command=partial(on_relay, channel, enabled),
                    background=color,
                    foreground="#FFFFFF",
                    borderwidth=0,
                    padx=8,
                    pady=3,
                    state="disabled",
                )
                button.grid(row=row, column=group_column + offset, padx=(0, 6), pady=2)
                self._relay_buttons.append(button)

    def reset(self) -> None:
        self.apply(DiagnosticEvent(DiagnosticEventKind.DISCONNECTED))

    def apply(self, event: DiagnosticEvent) -> None:
        """Aplica um evento na thread gráfica, sem acessar Modbus."""

        if event.kind is DiagnosticEventKind.CONNECTING:
            self._automatic = False
            self._connecting = True
            self._status.configure(text="● Conectando...", foreground="#B26A00")
            self._message.configure(text="")
        elif event.kind is DiagnosticEventKind.CONNECTED:
            self._connecting = False
            self._connected = True
            self._status.configure(text="● Conectado", foreground=ACTIVE_COLOR)
        elif event.kind is DiagnosticEventKind.DISCONNECTED:
            self._automatic = False
            self._connecting = False
            self._connected = False
            self._status.configure(text="● Desconectado", foreground=TEXT_MUTED)
            self._message.configure(text=event.message)
            for label in (*self._input_labels.values(), *self._relay_labels.values()):
                label.configure(text="Desconhecido", foreground=TEXT_MUTED)
        elif event.kind is DiagnosticEventKind.AUTOMATIC:
            self._automatic = True
            self._status.configure(text="● Automático — DI ativa = feixe livre")
            self._message.configure(text=event.message)
        elif event.kind is DiagnosticEventKind.INPUTS:
            for channel, state in enumerate(event.states, start=1):
                self._input_labels[channel].configure(
                    text="Ativado" if state else "Desativado",
                    foreground=ACTIVE_COLOR if state else INACTIVE_COLOR,
                )
        elif event.kind is DiagnosticEventKind.RELAYS:
            states = (
                ((event.channel, event.states[0]),) if event.channel else enumerate(event.states, 1)
            )
            for channel, state in states:
                self._relay_labels[channel].configure(
                    text="ON" if state else "OFF",
                    foreground=ACTIVE_COLOR if state else INACTIVE_COLOR,
                )
            self._message.configure(text="")
        elif event.kind is DiagnosticEventKind.RELAY_ERROR:
            self._relay_labels[event.channel].configure(text="Desconhecido", foreground=TEXT_MUTED)
            self._message.configure(text=event.message)
        self._connect_button.configure(
            state="disabled" if self._connected or self._connecting else "normal"
        )
        self._disconnect_button.configure(
            state="normal" if self._connected or self._connecting else "disabled"
        )
        for index, button in enumerate(self._relay_buttons):
            blocked = self._automatic and index < 6
            button.configure(state="normal" if self._connected and not blocked else "disabled")
        if self._automatic_button is not None:
            self._automatic_button.configure(
                state="disabled" if self._connected or self._connecting else "normal"
            )
