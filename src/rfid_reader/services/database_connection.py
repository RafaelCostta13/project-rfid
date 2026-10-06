"""Compatibilidade para o status remoto antigo removido pelo RF014.

Use LocalDatabaseConnectionChecker para a base operacional local e
SyncConnectionChecker para o endpoint remoto de sincronização.
"""

from rfid_reader.services.local_database_connection import (
    LocalDatabaseConnectionChecker,
    SyncConnectionChecker,
)

__all__ = ["LocalDatabaseConnectionChecker", "SyncConnectionChecker"]
