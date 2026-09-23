"""Integrações externas da aplicação."""

from rfid_reader.integrations.sharepoint_client import SharePointLookupClient
from rfid_reader.integrations.waveshare_modbus import PymodbusWaveshareConnectionTester

__all__ = [
    "PymodbusWaveshareConnectionTester",
    "SharePointLookupClient",
]
