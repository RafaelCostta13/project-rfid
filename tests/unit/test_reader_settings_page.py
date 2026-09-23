import queue

import pytest

from rfid_reader.domain import (
    ReaderConfigurationAction,
    ReaderConfigurationFeedback,
    ReaderConfigurationOutcome,
    ReaderConnectionSettings,
    WaveshareConfigurationAction,
    WaveshareConfigurationFeedback,
    WaveshareConfigurationOutcome,
    WaveshareConnectionSettings,
)
from rfid_reader.ui import pages as pages_module
from rfid_reader.ui.main_window import MainWindow
from rfid_reader.ui.pages import (
    RFID_SETTINGS_FIELDS,
    SAVE_CONFIGURATION_BUTTON_TEXT,
    TEST_CONNECTION_BUTTON_TEXT,
    WAVESHARE_SETTINGS_FIELDS,
    RFIDSettingsPage,
    WaveshareSettingsPanel,
)


class RecordingVariable:
    def __init__(self, value: str = "") -> None:
        self.value = value

    def get(self) -> str:
        return self.value

    def set(self, value: str) -> None:
        self.value = value


class RecordingWidget:
    def __init__(self) -> None:
        self.options: dict[str, str] = {}

    def configure(self, **options: str) -> None:
        self.options.update(options)


def page_without_tk() -> RFIDSettingsPage:
    page = object.__new__(RFIDSettingsPage)
    page._reader_name_var = RecordingVariable()
    page._reader_host_var = RecordingVariable()
    page._reader_port_var = RecordingVariable()
    page._test_button = RecordingWidget()
    page._feedback_label = RecordingWidget()
    page._on_test_connection = lambda name, host, port: None
    page._on_save = lambda name, host, port: None
    return page


def waveshare_panel_without_tk() -> WaveshareSettingsPanel:
    panel = object.__new__(WaveshareSettingsPanel)
    panel._serial_port_var = RecordingVariable()
    panel._baud_rate_var = RecordingVariable()
    panel._data_bits_var = RecordingVariable()
    panel._parity_var = RecordingVariable()
    panel._stop_bits_var = RecordingVariable()
    panel._device_id_var = RecordingVariable()
    panel._test_button = RecordingWidget()
    panel._feedback_label = RecordingWidget()
    panel._on_test_connection = lambda *values: None
    panel._on_save = lambda *values: None
    return panel


def test_settings_page_exposes_required_fields_and_buttons() -> None:
    assert RFID_SETTINGS_FIELDS == ("Nome do reader", "Endereço IP", "Porta")
    assert TEST_CONNECTION_BUTTON_TEXT == "Testar conexão"
    assert SAVE_CONFIGURATION_BUTTON_TEXT == "Salvar configurações"
    assert WAVESHARE_SETTINGS_FIELDS == (
        "Porta COM",
        "Baud rate",
        "Data bits",
        "Paridade",
        "Stop bits",
        "Device ID",
    )


def test_constructor_preserves_tk_internal_widget_name(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    internal_widget_name = "!rfidsettingspage"

    def fake_frame_init(
        frame: RFIDSettingsPage,
        parent: object,
        **options: object,
    ) -> None:
        frame._name = internal_widget_name

    monkeypatch.setattr(pages_module.tk.Frame, "__init__", fake_frame_init)
    monkeypatch.setattr(pages_module.tk, "StringVar", RecordingVariable)
    monkeypatch.setattr(RFIDSettingsPage, "_build", lambda page: None)

    page = RFIDSettingsPage(
        object(),  # type: ignore[arg-type]
        ReaderConnectionSettings("Reader Doca", "192.168.0.214", 5084),
        lambda name, host, port: None,
        lambda name, host, port: None,
        WaveshareConnectionSettings("", 9600, 8, "None", 1, 1),
        lambda *values: None,
        lambda *values: None,
    )

    assert page._name == internal_widget_name
    assert page._name in {internal_widget_name: page}


def test_settings_page_loads_current_values() -> None:
    page = page_without_tk()

    page.set_settings(ReaderConnectionSettings("Reader Doca", "192.168.0.214", 5084))

    assert page._values() == ("Reader Doca", "192.168.0.214", "5084")


def test_test_feedback_disables_button_while_running_and_enables_after_result() -> None:
    page = page_without_tk()

    page.apply_feedback(
        ReaderConfigurationFeedback(
            ReaderConfigurationAction.TEST,
            ReaderConfigurationOutcome.IN_PROGRESS,
            "Testando conexão...",
        )
    )
    assert page._test_button.options["state"] == "disabled"
    assert page._feedback_label.options["text"] == "Testando conexão..."

    page.apply_feedback(
        ReaderConfigurationFeedback(
            ReaderConfigurationAction.TEST,
            ReaderConfigurationOutcome.SUCCESS,
            "Conexão realizada com sucesso.",
        )
    )
    assert page._test_button.options["state"] == "normal"
    assert page._feedback_label.options["text"] == "Conexão realizada com sucesso."


def test_save_success_keeps_normalized_values_in_form() -> None:
    page = page_without_tk()
    saved = ReaderConnectionSettings("Reader Novo", "reader-novo", 6000)

    page.apply_feedback(
        ReaderConfigurationFeedback(
            ReaderConfigurationAction.SAVE,
            ReaderConfigurationOutcome.SUCCESS,
            "Configurações salvas com sucesso.",
            saved,
        )
    )

    assert page._values() == ("Reader Novo", "reader-novo", "6000")


def test_validation_error_preserves_typed_values() -> None:
    page = page_without_tk()
    page._reader_name_var.set("  Reader digitado  ")
    page._reader_host_var.set("192.168.0.999")
    page._reader_port_var.set("abc")

    page.apply_feedback(
        ReaderConfigurationFeedback(
            ReaderConfigurationAction.SAVE,
            ReaderConfigurationOutcome.ERROR,
            "Endereço IP ou hostname inválido.",
        )
    )

    assert page._values() == ("  Reader digitado  ", "192.168.0.999", "abc")


def test_main_window_delivers_configuration_feedback_from_queue() -> None:
    page = page_without_tk()
    updates: queue.SimpleQueue[ReaderConfigurationFeedback] = queue.SimpleQueue()
    event = ReaderConfigurationFeedback(
        ReaderConfigurationAction.TEST,
        ReaderConfigurationOutcome.IN_PROGRESS,
        "Testando conexão...",
    )
    updates.put(event)
    window = object.__new__(MainWindow)
    window._configuration_updates = updates
    window._settings_page = page

    window._drain_configuration_updates()

    assert page._feedback_label.options["text"] == "Testando conexão..."
    assert page._test_button.options["state"] == "disabled"


def test_waveshare_panel_loads_defaults_including_empty_port() -> None:
    panel = waveshare_panel_without_tk()

    panel.set_settings(WaveshareConnectionSettings("", 9600, 8, "None", 1, 1))

    assert panel._values() == ("", "9600", "8", "None", "1", "1")


def test_waveshare_feedback_controls_only_its_test_button() -> None:
    panel = waveshare_panel_without_tk()

    panel.apply_feedback(
        WaveshareConfigurationFeedback(
            WaveshareConfigurationAction.TEST,
            WaveshareConfigurationOutcome.IN_PROGRESS,
            "Testando conexão com a Waveshare...",
        )
    )
    assert panel._test_button.options["state"] == "disabled"

    saved = WaveshareConnectionSettings("COM5", 9600, 8, "None", 1, 1)
    panel.apply_feedback(
        WaveshareConfigurationFeedback(
            WaveshareConfigurationAction.SAVE,
            WaveshareConfigurationOutcome.SUCCESS,
            "Configurações da Waveshare salvas com sucesso.",
            saved,
        )
    )
    assert panel._values() == ("COM5", "9600", "8", "None", "1", "1")


def test_main_window_delivers_waveshare_feedback_from_its_queue() -> None:
    panel = waveshare_panel_without_tk()
    updates: queue.SimpleQueue[WaveshareConfigurationFeedback] = queue.SimpleQueue()
    updates.put(
        WaveshareConfigurationFeedback(
            WaveshareConfigurationAction.TEST,
            WaveshareConfigurationOutcome.SUCCESS,
            "Conexão com a Waveshare realizada com sucesso.",
        )
    )
    page = page_without_tk()
    page._waveshare_panel = panel
    window = object.__new__(MainWindow)
    window._waveshare_configuration_updates = updates
    window._settings_page = page

    window._drain_waveshare_configuration_updates()

    assert panel._feedback_label.options["text"] == (
        "Conexão com a Waveshare realizada com sucesso."
    )
