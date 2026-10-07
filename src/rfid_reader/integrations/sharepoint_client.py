"""Compatibilidade para o endpoint remoto por EPC removido pelo RF014."""

from __future__ import annotations

from dataclasses import dataclass


class TagLookupClientError(RuntimeError):
    """Endpoint remoto por EPC desativado."""


class TagLookupTimeoutError(TagLookupClientError):
    """Mantido apenas para compatibilidade de imports antigos."""


class TagLookupHttpError(TagLookupClientError):
    """Mantido apenas para compatibilidade de imports antigos."""

    def __init__(self, status_code: int) -> None:
        super().__init__(f"resposta HTTP {status_code}")
        self.status_code = status_code


class TagLookupResponseError(TagLookupClientError):
    """Mantido apenas para compatibilidade de imports antigos."""


@dataclass(frozen=True, slots=True)
class HttpResponse:
    """Resposta mínima preservada para testes externos legados."""

    status_code: int
    body: bytes
