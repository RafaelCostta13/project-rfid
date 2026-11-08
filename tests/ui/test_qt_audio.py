from pathlib import Path

import pytest

pytest.importorskip("PySide6")

from PySide6.QtTest import QTest

from rfid_reader.ui.qt.audio import DEFAULT_SOUND_PATH, AudioNotificationService


def test_default_sound_is_bip2_resource() -> None:
    assert DEFAULT_SOUND_PATH.name == "bip2.wav"
    assert DEFAULT_SOUND_PATH.is_file()


def test_audio_requests_are_deduplicated_and_spaced(qt_application: object, tmp_path: Path) -> None:
    sound = tmp_path / "bip.wav"
    sound.write_bytes(b"wav")
    started: list[Path] = []
    service = AudioNotificationService(
        interval_ms=200,
        sound_path=sound,
        player=started.append,
    )

    assert service.request("EPC-A")
    assert not service.request("EPC-A")
    assert service.request("EPC-B")
    QTest.qWait(20)
    assert started == [sound]
    QTest.qWait(230)
    assert started == [sound, sound]
    service.close()


def test_audio_disabled_or_cancelled_never_plays_pending(
    qt_application: object, tmp_path: Path
) -> None:
    sound = tmp_path / "bip.wav"
    sound.write_bytes(b"wav")
    started: list[Path] = []
    service = AudioNotificationService(
        interval_ms=200,
        sound_path=sound,
        player=started.append,
    )
    assert service.request("EPC-A")
    assert service.request("EPC-B")
    QTest.qWait(20)
    service.cancel()
    QTest.qWait(230)
    assert len(started) == 1
    service.configure(False, 200)
    assert not service.request("EPC-C")
    assert len(started) == 1
    service.close()
