"""Verificador periódico da disponibilidade Modbus da Waveshare."""

from __future__ import annotations

from rfid_reader.domain import ConnectionStatus
from rfid_reader.services.waveshare_diagnostic import (
    WaveshareConnectionTester,
    WaveshareDiagnosticService,
)


class WaveshareConnectionChecker:
    """Reutiliza a configuração e respeita a sessão de diagnóstico ativa."""

    def __init__(
        self,
        diagnostic: WaveshareDiagnosticService,
        tester: WaveshareConnectionTester,
    ) -> None:
        self._diagnostic = diagnostic
        self._tester = tester

    def check(self) -> ConnectionStatus:
        return self._diagnostic.probe_status(self._tester)

    def close(self) -> None:
        """O cliente temporário é fechado a cada verificação."""
