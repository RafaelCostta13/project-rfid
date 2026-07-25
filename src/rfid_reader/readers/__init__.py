"""Contratos e implementações de comunicação com readers RFID."""

from rfid_reader.readers.base import RFIDReader
from rfid_reader.readers.zebra_fx9600 import ZebraFX9600Reader

__all__ = ["RFIDReader", "ZebraFX9600Reader"]
