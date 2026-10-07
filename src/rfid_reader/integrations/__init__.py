"""Integrações externas da aplicação."""

from rfid_reader.integrations.sharepoint_sync_client import PowerAutomateSyncClient
from rfid_reader.integrations.waveshare_modbus import PymodbusWaveshareConnectionTester

__all__ = [
    "PowerAutomateSyncClient",
    "PymodbusWaveshareConnectionTester",
]
