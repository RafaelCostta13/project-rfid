"""Conversão segura do EPC técnico para a Tag apresentada ao usuário."""

from __future__ import annotations

import logging
import string

LOGGER = logging.getLogger(__name__)
INVALID_TAG_TEXT = "Tag inválida"
NON_ASCII_TAG_TEXT = "Tag não ASCII"
HEX_DIGITS = frozenset(string.hexdigits)


def epc_hex_to_ascii(epc: str) -> str:
    """Converte hexadecimal ASCII sem modificar ou descartar o EPC original."""

    if not epc or len(epc) % 2 != 0 or any(character not in HEX_DIGITS for character in epc):
        LOGGER.warning("tag_ascii_invalid_hex epc=%s", epc)
        return INVALID_TAG_TEXT

    raw_tag = bytes.fromhex(epc)
    try:
        decoded = raw_tag.decode("ascii")
    except UnicodeDecodeError:
        LOGGER.warning("tag_ascii_non_ascii_bytes epc=%s", epc)
        return NON_ASCII_TAG_TEXT

    tag = decoded.strip(" ")
    if not tag or any(not character.isprintable() for character in tag):
        LOGGER.warning("tag_ascii_non_printable epc=%s", epc)
        return INVALID_TAG_TEXT
    return tag
