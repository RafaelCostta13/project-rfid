import queue

import pytest

from rfid_reader.domain import (
    ReaderConfigurationAction,
    ReaderConfigurationFeedback,
    ReaderConfigurationOutcome,
    ReaderConnectionSettings,
)
from rfid_reader.ui import pages as pages_module
from rfid_reader.ui.main_window import MainWindow
from rfid_reader.ui.pages import (
    RFID_SETTINGS_FIELDS,
    SAVE_CONFIGURATION_BUTTON_TEXT,
    TEST_CONNECTION_BUTTON_TEXT,
    RFIDSettingsPage,
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


def test_settings_page_exposes_required_fields_and_buttons() -> None:
    assert RFID_SETTINGS_FIELDS == ("Nome do reader", "Endereço IP", "Porta")
    assert TEST_CONNECTION_BUTTON_TEXT == "Testar conexão"
    assert SAVE_CONFIGURATION_BUTTON_TEXT == "Salvar configurações"


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
