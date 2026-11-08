import threading
from collections.abc import Sequence

from rfid_reader.services.voice_notification import (
    VoiceNotificationEvent,
    VoiceNotificationService,
    VoiceNotificationState,
    voice_message,
)


def test_voice_message_uses_correct_singular_plural_and_validates_range() -> None:
    assert voice_message(0) == "Passou 0 caixas"
    assert voice_message(1) == "Passou 1 caixa"
    assert voice_message(25) == "Passou 25 caixas"
    for value in (-1, 10_000, True):
        try:
            voice_message(value)
        except ValueError:
            continue
        raise AssertionError(f"Valor inválido aceito: {value!r}")


def test_voice_service_reports_missing_maria_without_overlap() -> None:
    events: list[VoiceNotificationEvent] = []
    completed = threading.Event()
    started = threading.Event()
    release = threading.Event()

    def listener(event: VoiceNotificationEvent) -> None:
        events.append(event)
        if event.state is VoiceNotificationState.ERROR:
            completed.set()

    def runner(command: Sequence[str], message: str) -> int:
        assert "Microsoft Maria Desktop" in " ".join(command)
        assert message == "Passou 10 caixas"
        started.set()
        assert release.wait(1)
        return 3

    service = VoiceNotificationService(listener, runner=runner, platform="win32")
    try:
        assert service.speak(10)
        assert started.wait(1)
        assert not service.speak(10)
        release.set()
        assert completed.wait(1)
        assert events[0] == VoiceNotificationEvent(
            VoiceNotificationState.STARTED, "Passou 10 caixas"
        )
        assert events[-1] == VoiceNotificationEvent(
            VoiceNotificationState.ERROR,
            "A voz Microsoft Maria Desktop não está instalada neste Windows.",
        )
    finally:
        release.set()
        service.close()


def test_voice_service_rejects_non_windows_without_starting_process() -> None:
    events: list[VoiceNotificationEvent] = []
    service = VoiceNotificationService(events.append, platform="linux")
    try:
        assert not service.speak(1)
        assert events == [
            VoiceNotificationEvent(
                VoiceNotificationState.ERROR,
                "A síntese de voz está disponível apenas no Windows.",
            )
        ]
    finally:
        service.close()
