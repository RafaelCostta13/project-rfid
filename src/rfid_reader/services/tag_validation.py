"""Validação do EPC técnico recebido para consulta."""

from __future__ import annotations

import string

HEX_DIGITS = frozenset(string.hexdigits)


def is_valid_epc(epc: str) -> bool:
    """Informa se o EPC preserva a estrutura hexadecimal já aceita pelo fluxo."""

    return bool(epc) and len(epc) % 2 == 0 and all(character in HEX_DIGITS for character in epc)
