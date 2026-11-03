"""Validação, persistência e snapshot do filtro de prefixos EPC."""

from __future__ import annotations

import re
import threading
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, replace
from typing import Protocol

from rfid_reader.config import Settings

DEFAULT_EPC_PREFIXES = (
    "445543",
    "474143",
    "47574D",
    "484C44",
    "4A4554",
    "4D5743",
    "4F4D44",
    "534143",
    "424D57",
)
EPC_PREFIX_PATTERN = re.compile(r"^[0-9A-F]{6}$")


class EpcFilterValidationError(ValueError):
    """Indica uma configuração inválida do filtro de EPC."""


class EpcFilterConfigurationStore(Protocol):
    def save_values(self, values: dict[str, str]) -> None: ...


@dataclass(frozen=True, slots=True)
class EpcFilterState:
    """Snapshot imutável usado durante uma sessão de inventário."""

    enabled: bool
    prefixes: frozenset[str]

    def __init__(self, enabled: bool, prefixes: Iterable[str]) -> None:
        object.__setattr__(self, "enabled", enabled)
        object.__setattr__(self, "prefixes", frozenset(prefixes))

    def allows(self, epc: str) -> bool:
        return not self.enabled or epc.strip().upper()[:6] in self.prefixes


def normalize_epc_prefix(value: str) -> str:
    """Normaliza e valida um prefixo hexadecimal de exatamente três bytes."""

    normalized = value.strip().upper()
    if not EPC_PREFIX_PATTERN.fullmatch(normalized):
        raise EpcFilterValidationError(
            f"Prefixo EPC inválido: {value!r}. Use exatamente 6 caracteres hexadecimais."
        )
    return normalized


def validate_epc_prefixes(values: Sequence[str]) -> tuple[str, ...]:
    """Valida prefixos, preservando a ordem e rejeitando duplicidades."""

    normalized: list[str] = []
    seen: set[str] = set()
    for value in values:
        prefix = normalize_epc_prefix(value)
        if prefix in seen:
            raise EpcFilterValidationError(f"Prefixo EPC duplicado: {prefix}.")
        seen.add(prefix)
        normalized.append(prefix)
    if not normalized:
        raise EpcFilterValidationError("Informe ao menos um prefixo EPC autorizado.")
    return tuple(normalized)


def parse_epc_prefixes(raw_value: str) -> tuple[str, ...]:
    values = tuple(value for value in re.split(r"[,;\s]+", raw_value.strip()) if value)
    return validate_epc_prefixes(values)


class EpcFilterConfigurationService:
    """Mantém a configuração válida e grava apenas suas chaves no .env."""

    def __init__(self, settings: Settings, store: EpcFilterConfigurationStore) -> None:
        self._settings = settings
        self._store = store
        self._lock = threading.Lock()

    def current(self) -> EpcFilterState:
        with self._lock:
            return EpcFilterState(
                self._settings.epc_filter_enabled,
                self._settings.epc_allowed_prefixes,
            )

    def prefixes(self) -> list[str]:
        with self._lock:
            return list(self._settings.epc_allowed_prefixes)

    def save(self, enabled: bool, prefixes: Sequence[str]) -> tuple[bool, str]:
        if enabled:
            validated = validate_epc_prefixes(prefixes)
        else:
            validated = tuple(normalize_epc_prefix(value) for value in prefixes)
            if len(set(validated)) != len(validated):
                raise EpcFilterValidationError("A lista contém prefixos EPC duplicados.")
        self._store.save_values(
            {
                "RFID_EPC_FILTER_ENABLED": "true" if enabled else "false",
                "RFID_EPC_ALLOWED_PREFIXES": ",".join(validated),
            }
        )
        with self._lock:
            self._settings = replace(
                self._settings,
                epc_filter_enabled=enabled,
                epc_allowed_prefixes=validated,
            )
        return True, "Filtro de EPC salvo. Será aplicado no próximo inventário."
