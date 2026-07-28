"""Modelos de domínio da aplicação."""

from rfid_reader.domain.connection_status import ConnectionKind, ConnectionStatus
from rfid_reader.domain.inventory import (
    InventoryCleared,
    InventoryEvent,
    InventoryStatus,
    InventoryStatusChanged,
    TagReceived,
)
from rfid_reader.domain.reader_configuration import (
    ReaderConfigurationAction,
    ReaderConfigurationFeedback,
    ReaderConfigurationOutcome,
    ReaderConnectionSettings,
)
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

__all__ = [
    "ConnectionKind",
    "ConnectionStatus",
    "InventoryCleared",
    "InventoryEvent",
    "InventoryStatus",
    "InventoryStatusChanged",
    "ReaderConfigurationAction",
    "ReaderConfigurationFeedback",
    "ReaderConfigurationOutcome",
    "ReaderConnectionSettings",
    "TagRead",
    "TagReceived",
    "TagLookupChanged",
    "TagLookupEvent",
    "TagLookupKey",
    "TagLookupResult",
    "TagLookupSessionSummary",
    "TagLookupSessionStarted",
    "TagLookupStatus",
]
