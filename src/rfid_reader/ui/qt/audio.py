"""Notificação sonora auxiliar, isolada do processamento RFID."""

from __future__ import annotations

import logging
import sys
import time
from collections import deque
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PySide6.QtCore import QObject, QTimer

LOGGER = logging.getLogger(__name__)
MAX_PENDING_NOTIFICATIONS = 100
DEFAULT_SOUND_PATH = (
    Path(__file__).resolve().parent.parent / "qml" / "assets" / "sounds" / "bip2.wav"
)


class AudioNotificationService(QObject):
    """Enfileira bips sem bloquear a GUI, inventário ou consultas HTTP."""

    def __init__(
        self,
        *,
        enabled: bool = True,
        interval_ms: int = 300,
        sound_path: Path = DEFAULT_SOUND_PATH,
        player: Callable[[Path], None] | None = None,
        clock: Callable[[], float] = time.monotonic,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._enabled = enabled
        self._interval_ms = interval_ms
        self._sound_path = sound_path
        self._player = player or self._play_windows_sound
        self._clock = clock
        self._seen: set[str] = set()
        self._pending: deque[str] = deque()
        self._last_started: float | None = None
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._drain)
        self._missing_reported = False
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="audio-notification")

    @property
    def pending_count(self) -> int:
        return len(self._pending)

    def begin_session(self) -> None:
        self.cancel()
        self._seen.clear()

    def configure(self, enabled: bool, interval_ms: int) -> None:
        self._enabled = enabled
        self._interval_ms = interval_ms
        if not enabled:
            self.cancel()

    def request(self, epc: str) -> bool:
        """Solicita um único som por EPC na sessão atual."""

        if not self._enabled or epc in self._seen:
            return False
        self._seen.add(epc)
        if len(self._pending) >= MAX_PENDING_NOTIFICATIONS:
            LOGGER.warning("audio_notification_queue_full discarded_epc=%s", epc)
            return False
        self._pending.append(epc)
        self._drain()
        return True

    def cancel(self) -> None:
        self._pending.clear()
        self._timer.stop()

    def close(self) -> None:
        self.cancel()
        self._executor.shutdown(wait=False, cancel_futures=True)

    def _drain(self) -> None:
        if not self._enabled or not self._pending:
            return
        if self._last_started is not None:
            elapsed_ms = (self._clock() - self._last_started) * 1000
            remaining_ms = self._interval_ms - elapsed_ms
            if remaining_ms > 0:
                self._timer.start(max(1, round(remaining_ms)))
                return
        self._pending.popleft()
        self._last_started = self._clock()
        self._play()
        if self._pending:
            self._timer.start(self._interval_ms)

    def _play(self) -> None:
        if not self._sound_path.is_file():
            if not self._missing_reported:
                LOGGER.warning("audio_notification_file_missing path=%s", self._sound_path)
                self._missing_reported = True
            return
        self._executor.submit(self._invoke_player, self._sound_path)

    def _invoke_player(self, path: Path) -> None:
        try:
            self._player(path)
        except (OSError, RuntimeError):
            LOGGER.warning("audio_notification_playback_failed", exc_info=True)

    @staticmethod
    def _play_windows_sound(path: Path) -> None:
        if sys.platform != "win32":
            return
        import winsound

        winsound.PlaySound(str(path), winsound.SND_FILENAME)
