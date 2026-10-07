"""Repositório SQLite para a base operacional local de etiquetas."""

from __future__ import annotations

import logging
import sqlite3
import threading
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path

from rfid_reader.domain import LocalTagRecord, SyncControl, TagLookupResult, TagLookupStatus

LOGGER = logging.getLogger(__name__)


class LocalDatabaseError(RuntimeError):
    """Falha esperada ao abrir, validar ou gravar o SQLite local."""


class LocalTagRepository:
    """Centraliza schema, sincronização transacional e consulta local por EPC."""

    def __init__(self, database_path: Path) -> None:
        self._database_path = database_path
        self._lock = threading.Lock()

    @property
    def database_path(self) -> Path:
        return self._database_path

    def initialize(self) -> None:
        """Cria diretório e schema local se ainda não existirem."""

        try:
            self._database_path.parent.mkdir(parents=True, exist_ok=True)
            with self._connect() as connection:
                self._create_schema(connection)
        except sqlite3.Error as error:
            raise LocalDatabaseError("falha ao inicializar o SQLite local") from error
        except OSError as error:
            raise LocalDatabaseError("falha ao criar o diretório do SQLite local") from error

    def find_by_epc(self, epc: str, dock: str) -> TagLookupResult | None:
        """Consulta a etiqueta operacionalmente válida para a Doca configurada."""

        if not dock:
            LOGGER.warning("local_tag_lookup_without_dock epc=%s", epc)
            return None
        try:
            with self._connect() as connection:
                row = connection.execute(
                    """
                    SELECT epc, status, cliente, nota_fiscal, volume, pedido, doca
                    FROM etiquetas
                    WHERE epc = ? AND doca = ?
                    LIMIT 1
                    """,
                    (epc, dock),
                ).fetchone()
        except sqlite3.Error as error:
            raise LocalDatabaseError("falha ao consultar EPC no SQLite local") from error

        if row is None:
            return None
        status = str(row["status"])
        if status.strip().lower() == "inativo":
            LOGGER.debug("local_tag_inactive_ignored epc=%s dock=%s", epc, dock)
            return None
        return TagLookupResult(
            epc=str(row["epc"]),
            status=TagLookupStatus.FOUND,
            message="Etiqueta encontrada na base local.",
            customer=str(row["cliente"]),
            invoice_number=str(row["nota_fiscal"]),
            volume=str(row["volume"]),
            order_number=str(row["pedido"]),
            dock=str(row["doca"]),
        )

    def sync_control(self, dock: str) -> SyncControl | None:
        """Obtém o cursor salvo para a Doca, sem misturar estações."""

        try:
            with self._connect() as connection:
                row = connection.execute(
                    """
                    SELECT doca, last_sync, last_full_sync, last_success_at, initialized
                    FROM sync_control
                    WHERE doca = ?
                    """,
                    (dock,),
                ).fetchone()
        except sqlite3.Error as error:
            raise LocalDatabaseError("falha ao consultar controle de sincronização") from error
        if row is None:
            return None
        return SyncControl(
            dock=str(row["doca"]),
            last_sync=str(row["last_sync"]),
            last_full_sync=str(row["last_full_sync"]),
            last_success_at=str(row["last_success_at"]),
            initialized=bool(row["initialized"]),
        )

    def is_operational(self, dock: str) -> bool:
        """Valida schema, abertura e carga inicial confirmada para a Doca."""

        if not dock:
            return False
        try:
            with self._connect() as connection:
                self._assert_schema(connection)
                row = connection.execute(
                    "SELECT initialized FROM sync_control WHERE doca = ?",
                    (dock,),
                ).fetchone()
        except sqlite3.Error:
            LOGGER.exception("local_database_check_failed")
            return False
        return row is not None and bool(row["initialized"])

    def apply_sync(
        self,
        dock: str,
        items: Sequence[LocalTagRecord],
        sync_until: str,
        *,
        full_sync: bool,
    ) -> None:
        """Grava todos os itens e avança o cursor somente no mesmo COMMIT."""

        synced_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")
        last_full_sync = sync_until if full_sync else self._last_full_sync(dock)
        with self._lock:
            try:
                with self._connect() as connection:
                    self._create_schema(connection)
                    connection.execute("BEGIN")
                    try:
                        for item in items:
                            connection.execute(
                                """
                                INSERT INTO etiquetas (
                                    sharepoint_id,
                                    epc,
                                    status,
                                    cliente,
                                    nota_fiscal,
                                    volume,
                                    pedido,
                                    doca,
                                    sharepoint_modified,
                                    synced_at
                                )
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                ON CONFLICT(sharepoint_id) DO UPDATE SET
                                    epc = excluded.epc,
                                    status = excluded.status,
                                    cliente = excluded.cliente,
                                    nota_fiscal = excluded.nota_fiscal,
                                    volume = excluded.volume,
                                    pedido = excluded.pedido,
                                    doca = excluded.doca,
                                    sharepoint_modified = excluded.sharepoint_modified,
                                    synced_at = excluded.synced_at
                                """,
                                (
                                    item.sharepoint_id,
                                    item.epc,
                                    item.status,
                                    item.customer,
                                    item.invoice_number,
                                    item.volume,
                                    item.order_number,
                                    item.dock,
                                    item.sharepoint_modified,
                                    synced_at,
                                ),
                            )
                        connection.execute(
                            """
                            INSERT INTO sync_control (
                                doca,
                                last_sync,
                                last_full_sync,
                                last_success_at,
                                initialized
                            )
                            VALUES (?, ?, ?, ?, 1)
                            ON CONFLICT(doca) DO UPDATE SET
                                last_sync = excluded.last_sync,
                                last_full_sync = excluded.last_full_sync,
                                last_success_at = excluded.last_success_at,
                                initialized = 1
                            """,
                            (dock, sync_until, last_full_sync, synced_at),
                        )
                    except Exception:
                        connection.rollback()
                        raise
                    else:
                        connection.commit()
            except sqlite3.Error as error:
                raise LocalDatabaseError(
                    "falha ao aplicar sincronização no SQLite local"
                ) from error

    def _last_full_sync(self, dock: str) -> str:
        control = self.sync_control(dock)
        return "" if control is None else control.last_full_sync

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._database_path, timeout=5.0)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    @staticmethod
    def _create_schema(connection: sqlite3.Connection) -> None:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS etiquetas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sharepoint_id INTEGER NOT NULL,
                epc TEXT NOT NULL,
                status TEXT NOT NULL,
                cliente TEXT NOT NULL,
                nota_fiscal TEXT NOT NULL,
                volume TEXT NOT NULL,
                pedido TEXT NOT NULL,
                doca TEXT NOT NULL,
                sharepoint_modified TEXT NOT NULL,
                synced_at TEXT NOT NULL,
                UNIQUE(sharepoint_id),
                UNIQUE(doca, epc)
            )
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_etiquetas_doca_epc
            ON etiquetas(doca, epc)
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS sync_control (
                doca TEXT PRIMARY KEY,
                last_sync TEXT NOT NULL,
                last_full_sync TEXT NOT NULL,
                last_success_at TEXT NOT NULL,
                initialized INTEGER NOT NULL CHECK(initialized IN (0, 1))
            )
            """
        )

    @staticmethod
    def _assert_schema(connection: sqlite3.Connection) -> None:
        tables = {
            str(row["name"])
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }
        missing = {"etiquetas", "sync_control"} - tables
        if missing:
            raise sqlite3.DatabaseError("schema local incompleto")
