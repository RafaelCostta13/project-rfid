"""Modelos de domínio da aplicação."""

from rfid_reader.domain.connection_status import ConnectionKind, ConnectionStatus
from rfid_reader.domain.inventory import (
    InventoryCleared,
    InventoryEvent,
    InventoryStatus,
    InventoryStatusChanged,
    TagReceived,
)
from rfid_reader.domain.local_tag import LocalTagRecord, SyncControl
from rfid_reader.domain.reader_configuration import (
    ReaderConfigurationAction,
    ReaderConfigurationFeedback,
    ReaderConfigurationOutcome,
    ReaderConnectionSettings,
)
from rfid_reader.domain.rfid_read import RfidReadResult
from rfid_reader.domain.tag_lookup import (
    TagLookupChanged,
    TagLookupEvent,
    TagLookupKey,
    TagLookupResult,
    TagLookupSessionStarted,
    TagLookupSessionSummary,
    TagLookupStatus,
)
from rfid_reader.domain.tag_read import TagRead
from rfid_reader.domain.waveshare_configuration import (
    WaveshareConfigurationAction,
    WaveshareConfigurationFeedback,
    WaveshareConfigurationOutcome,
    WaveshareConnectionSettings,
)

__all__ = [
    "ConnectionKind",
    "ConnectionStatus",
    "InventoryCleared",
    "InventoryEvent",
    "InventoryStatus",
    "InventoryStatusChanged",
    "LocalTagRecord",
    "ReaderConfigurationAction",
    "ReaderConfigurationFeedback",
    "ReaderConfigurationOutcome",
    "ReaderConnectionSettings",
    "RfidReadResult",
    "SyncControl",
    "TagRead",
    "TagReceived",
    "TagLookupChanged",
    "TagLookupEvent",
    "TagLookupKey",
    "TagLookupResult",
    "TagLookupSessionSummary",
    "TagLookupSessionStarted",
    "TagLookupStatus",
    "WaveshareConfigurationAction",
    "WaveshareConfigurationFeedback",
    "WaveshareConfigurationOutcome",
    "WaveshareConnectionSettings",
]
