import queue
from collections.abc import Callable

import pytest

from rfid_reader.services.waveshare_diagnostic import DiagnosticEvent, DiagnosticEventKind
from rfid_reader.ui import waveshare_diagnostic_page as page_module
from rfid_reader.ui.components import PAGE_NAMES
from rfid_reader.ui.main_window import MainWindow
from rfid_reader.ui.navigation import NavigationState, PageId
from rfid_reader.ui.waveshare_diagnostic_page import (
    WaveshareDiagnosticPage,
    relay_grid_position,
)


class Label:
    def __init__(self) -> None:
        self.options: dict[str, str] = {}

    def configure(self, **options: str) -> None:
        self.options.update(options)


def page_without_tk() -> WaveshareDiagnosticPage:
    page = object.__new__(WaveshareDiagnosticPage)
    page._connected = False
    page._connecting = False
    page._automatic = False
    page._automatic_button = None
    page._status = Label()
    page._message = Label()
    page._connect_button = Label()
    page._disconnect_button = Label()
    page._input_labels = {channel: Label() for channel in range(1, 6)}
    page._relay_labels = {channel: Label() for channel in range(1, 9)}
    page._relay_buttons = [Label() for _ in range(16)]
    return page


def test_page_shows_all_inputs_and_relays_only_after_real_events() -> None:
    page = page_without_tk()
    page.reset()
    assert {label.options["text"] for label in page._input_labels.values()} == {"Desconhecido"}
    assert {label.options["text"] for label in page._relay_labels.values()} == {"Desconhecido"}

    page.apply(DiagnosticEvent(DiagnosticEventKind.CONNECTED))
    page.apply(DiagnosticEvent(DiagnosticEventKind.INPUTS, states=(True, False, True, False, True)))
    page.apply(DiagnosticEvent(DiagnosticEventKind.RELAYS, states=(True, False) * 4))

    assert [label.options["text"] for label in page._input_labels.values()] == [
        "Ativado",
        "Desativado",
        "Ativado",
        "Desativado",
        "Ativado",
    ]
    assert [label.options["text"] for label in page._relay_labels.values()] == [
        "ON",
        "OFF",
        "ON",
        "OFF",
        "ON",
        "OFF",
        "ON",
        "OFF",
    ]
    assert all(button.options["state"] == "normal" for button in page._relay_buttons)

    page.apply(DiagnosticEvent(DiagnosticEventKind.DISCONNECTED, "Comunicação perdida"))
    assert all(button.options["state"] == "disabled" for button in page._relay_buttons)
    assert {label.options["text"] for label in page._relay_labels.values()} == {"Desconhecido"}


def test_failed_relay_command_never_shows_requested_state() -> None:
    page = page_without_tk()
    page.reset()
    page.apply(DiagnosticEvent(DiagnosticEventKind.CONNECTED))
    page.apply(
        DiagnosticEvent(DiagnosticEventKind.RELAY_ERROR, "Falha ao controlar CH5.", channel=5)
    )

    assert page._relay_labels[5].options["text"] == "Desconhecido"
    assert page._message.options["text"] == "Falha ao controlar CH5."


@pytest.mark.parametrize(
    ("channel", "position", "address"),
    [(6, (2, 4), 5), (7, (3, 4), 6), (8, (4, 4), 7)],
)
def test_last_three_relay_positions_and_modbus_addresses(
    channel: int, position: tuple[int, int], address: int
) -> None:
    assert relay_grid_position(channel) == position
    assert channel - 1 == address


@pytest.mark.parametrize("channel", [6, 7, 8])
def test_last_three_relays_change_visual_state_only_on_confirmation(channel: int) -> None:
    page = page_without_tk()
    page.reset()
    page.apply(DiagnosticEvent(DiagnosticEventKind.CONNECTED))

    page.apply(DiagnosticEvent(DiagnosticEventKind.RELAYS, states=(True,), channel=channel))
    assert page._relay_labels[channel].options["text"] == "ON"
    page.apply(DiagnosticEvent(DiagnosticEventKind.RELAYS, states=(False,), channel=channel))
    assert page._relay_labels[channel].options["text"] == "OFF"
    assert all(
        label.options["text"] == "Desconhecido"
        for other_channel, label in page._relay_labels.items()
        if other_channel != channel
    )


def test_last_three_relays_have_visible_controls_with_correct_callbacks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class Widget:
        def __init__(self, parent: object, **options: object) -> None:
            self.options = options
            self.grid_options: dict[str, object] = {}
            widgets.append(self)

        def pack(self, **options: object) -> None:
            pass

        def grid(self, **options: object) -> None:
            self.grid_options = options

        def configure(self, **options: object) -> None:
            self.options.update(options)

    widgets: list[Widget] = []

    def no_frame_init(frame: object, parent: object, **options: object) -> None:
        pass

    def no_frame_layout(frame: object, **options: object) -> None:
        pass

    monkeypatch.setattr(page_module.tk.Frame, "__init__", no_frame_init)
    monkeypatch.setattr(page_module.tk.Frame, "pack", no_frame_layout)
    monkeypatch.setattr(page_module.tk.Frame, "grid", no_frame_layout)
    monkeypatch.setattr(page_module.tk, "Label", Widget)
    monkeypatch.setattr(page_module.tk, "Button", Widget)
    commands: list[tuple[int, bool]] = []
    page = WaveshareDiagnosticPage(
        object(),
        lambda: None,
        lambda: None,
        lambda channel, enabled: commands.append((channel, enabled)),
        lambda: None,
    )
    page.apply(DiagnosticEvent(DiagnosticEventKind.CONNECTED))

    for channel in (6, 7, 8):
        row, column = relay_grid_position(channel)
        label = next(widget for widget in widgets if widget.options.get("text") == f"CH{channel}")
        assert label.grid_options["row"] == row
        assert label.grid_options["column"] == column
        for offset, text, _enabled in ((2, "Ligar", True), (3, "Desligar", False)):
            button = next(
                widget
                for widget in widgets
                if widget.options.get("text") == text
                and widget.grid_options.get("row") == row
                and widget.grid_options.get("column") == column + offset
            )
            assert button.options["state"] == "normal"
            command = button.options["command"]
            assert isinstance(command, Callable)
            command()

    assert commands == [
        (6, True),
        (6, False),
        (7, True),
        (7, False),
        (8, True),
        (8, False),
    ]


def test_diagnostic_page_opens_from_settings_without_sidebar_entry() -> None:
    class Sidebar:
        selected: PageId | None = None

        def select(self, page: PageId) -> None:
            self.selected = page

    class Content:
        shown: PageId | None = None

        def show(self, page: PageId) -> None:
            self.shown = page

    window = object.__new__(MainWindow)
    window._is_automatic = lambda: False
    window._navigation = NavigationState(PageId.RFID_SETTINGS)
    window._diagnostic_updates = queue.SimpleQueue()
    window._sidebar = Sidebar()
    window._content = Content()
    window._diagnostic_page = page_without_tk()

    window._open_waveshare_diagnostic()

    assert window._navigation.current_page is PageId.WAVESHARE_DIAGNOSTIC
    assert window._content.shown is PageId.WAVESHARE_DIAGNOSTIC
    assert window._sidebar.selected is PageId.RFID_SETTINGS
    assert PageId.WAVESHARE_DIAGNOSTIC not in PAGE_NAMES


@pytest.mark.parametrize("automatic", [False, True])
def test_returning_to_settings_requests_disconnect(automatic: bool) -> None:
    class Sidebar:
        def select(self, page: PageId) -> None:
            self.selected = page

    class Content:
        def show(self, page: PageId) -> None:
            self.shown = page

    class Settings:
        def set_settings(self, settings: object) -> None:
            pass

        def set_waveshare_settings(self, settings: object) -> None:
            pass

        def set_station_dock(self, dock: str) -> None:
            self.dock = dock

    disconnected: list[bool] = []
    window = object.__new__(MainWindow)
    window._is_automatic = lambda: automatic
    window._navigation = NavigationState(PageId.WAVESHARE_DIAGNOSTIC)
    window._sidebar = Sidebar()
    window._content = Content()
    window._settings_page = Settings()
    window._get_reader_settings = lambda: object()
    window._get_waveshare_settings = lambda: object()
    window._get_station_dock = lambda: "D05"
    window._diagnostic_page = page_without_tk()
    window._on_disconnect_diagnostic = lambda: disconnected.append(True)

    window._back_from_waveshare_diagnostic()

    assert disconnected == ([] if automatic else [True])
    assert window._settings_page.dock == "D05"
    assert window._navigation.current_page is PageId.RFID_SETTINGS
    if not automatic:
        assert window._diagnostic_page._status.options["text"] == "● Desconectado"


def test_automatic_mode_disables_only_ch1_to_ch3() -> None:
    page = page_without_tk()
    page.apply(DiagnosticEvent(DiagnosticEventKind.CONNECTED))
    page.apply(DiagnosticEvent(DiagnosticEventKind.AUTOMATIC))
    assert all(button.options["state"] == "disabled" for button in page._relay_buttons[:6])
    assert all(button.options["state"] == "normal" for button in page._relay_buttons[6:])
