"""Síntese de voz Windows para testes locais, sem dependências externas."""

from __future__ import annotations

import logging
import subprocess
import sys
import threading
from collections.abc import Callable, Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from enum import StrEnum

LOGGER = logging.getLogger(__name__)
VOICE_NAME = "Microsoft Maria Desktop"
VOICE_LANGUAGE = "Português (Brasil)"
VOICE_VOLUME = 80
VOICE_RATE = 0
VOICE_TIMEOUT_SECONDS = 30.0
VOICE_UNAVAILABLE_MESSAGE = "A voz Microsoft Maria Desktop não está instalada neste Windows."
VOICE_FAILURE_MESSAGE = "Não foi possível reproduzir a notificação por voz."
WINDOWS_ONLY_MESSAGE = "A síntese de voz está disponível apenas no Windows."


class VoiceNotificationState(StrEnum):
    STARTED = "started"
    FINISHED = "finished"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class VoiceNotificationEvent:
    state: VoiceNotificationState
    message: str


VoiceEventListener = Callable[[VoiceNotificationEvent], None]
VoiceRunner = Callable[[Sequence[str], str], int]


def voice_message(quantity: int) -> str:
    """Valida a quantidade e cria a frase pt-BR a ser sintetizada."""

    if isinstance(quantity, bool) or not isinstance(quantity, int) or not 0 <= quantity <= 9999:
        raise ValueError("Quantidade de caixas deve ser um número inteiro entre 0 e 9999.")
    unit = "caixa" if quantity == 1 else "caixas"
    return f"Passou {quantity} {unit}"


class VoiceNotificationService:
    """Executa uma fala por vez usando exclusivamente a voz instalada no Windows."""

    def __init__(
        self,
        listener: VoiceEventListener,
        *,
        runner: VoiceRunner | None = None,
        platform: str = sys.platform,
    ) -> None:
        self._listener = listener
        self._runner = runner or _run_windows_speech
        self._platform = platform
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="voice-notification")
        self._lock = threading.Lock()
        self._speaking = False
        self._closed = False

    @property
    def speaking(self) -> bool:
        with self._lock:
            return self._speaking

    def speak(self, quantity: int) -> bool:
        """Agenda a fala; chamadas concorrentes são ignoradas enquanto houver reprodução."""

        try:
            message = voice_message(quantity)
        except ValueError as error:
            self._emit(VoiceNotificationState.ERROR, str(error))
            return False
        if self._platform != "win32":
            self._emit(VoiceNotificationState.ERROR, WINDOWS_ONLY_MESSAGE)
            return False
        with self._lock:
            if self._closed or self._speaking:
                return False
            self._speaking = True
        self._emit(VoiceNotificationState.STARTED, message)
        self._executor.submit(self._run, message)
        return True

    def _run(self, message: str) -> None:
        try:
            return_code = self._runner(_powershell_command(), message)
            if return_code == 3:
                self._emit(
                    VoiceNotificationState.ERROR,
                    VOICE_UNAVAILABLE_MESSAGE,
                )
            elif return_code:
                LOGGER.warning("voice_notification_failed return_code=%d", return_code)
                self._emit(VoiceNotificationState.ERROR, VOICE_FAILURE_MESSAGE)
            else:
                self._emit(VoiceNotificationState.FINISHED, "Notificação por voz concluída.")
        except (OSError, subprocess.SubprocessError):
            LOGGER.warning("voice_notification_process_failed", exc_info=True)
            self._emit(VoiceNotificationState.ERROR, VOICE_FAILURE_MESSAGE)
        finally:
            with self._lock:
                self._speaking = False

    def close(self) -> None:
        with self._lock:
            self._closed = True
        self._executor.shutdown(wait=False, cancel_futures=True)

    def _emit(self, state: VoiceNotificationState, message: str) -> None:
        self._listener(VoiceNotificationEvent(state, message))


def _powershell_command() -> tuple[str, ...]:
    """Retorna comando fixo; a frase chega via stdin, nunca interpolada no script."""

    script = (
        "Add-Type -AssemblyName System.Speech; "
        "$message = [Console]::In.ReadToEnd(); "
        "$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        "$voice = $synth.GetInstalledVoices() | Where-Object { "
        "$_.VoiceInfo.Name -eq 'Microsoft Maria Desktop' "
        "-and $_.VoiceInfo.Culture.Name -eq 'pt-BR' }; "
        "if ($null -eq $voice) { exit 3 }; "
        "$synth.SelectVoice('Microsoft Maria Desktop'); $synth.Volume = 80; $synth.Rate = 0; "
        "$synth.Speak($message)"
    )
    return (
        "powershell.exe",
        "-NoProfile",
        "-NonInteractive",
        "-WindowStyle",
        "Hidden",
        "-Command",
        script,
    )


def _run_windows_speech(command: Sequence[str], message: str) -> int:
    completed = subprocess.run(
        command,
        input=message,
        text=True,
        capture_output=True,
        timeout=VOICE_TIMEOUT_SECONDS,
        check=False,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    return completed.returncode
