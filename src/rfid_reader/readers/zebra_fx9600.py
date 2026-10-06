"""Reader persistente Zebra FX9600 utilizando LLRP."""

from __future__ import annotations

import logging
import threading
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol, cast

from rfid_reader.domain import TagRead
from rfid_reader.readers.base import (
    DisconnectCallback,
    ReaderConnectionError,
    ReaderProtocolError,
    ReaderTimeoutError,
    TagCallback,
)

LOGGER = logging.getLogger(__name__)


class SllurpMessage(Protocol):
    def isSuccess(self) -> bool | None: ...


class SllurpLowLevelClient(Protocol):
    def startInventory(self, force_regen_rospec: bool = False) -> object: ...

    def stopPolitely(self, onCompletion: Callable[..., None] | None = None) -> object: ...

    def setState(self, state: int) -> None: ...


class SllurpReaderClient(Protocol):
    llrp: SllurpLowLevelClient

    def add_state_callback(self, state: int, callback: Callable[..., None]) -> None: ...

    def add_message_callback(
        self,
        message_type: str,
        callback: Callable[..., None],
    ) -> None: ...

    def add_tag_report_callback(self, callback: Callable[..., None]) -> None: ...

    def add_disconnected_callback(self, callback: Callable[..., None]) -> None: ...

    def connect(self) -> None: ...

    def disconnect(self, timeout: float = 0) -> None: ...

    def hard_disconnect(self) -> None: ...

    def is_alive(self) -> bool: ...

    def join(self, timeout: float | None = None) -> object: ...


@dataclass(frozen=True, slots=True)
class SllurpStateIds:
    """Estados da biblioteca mantidos dentro da camada readers."""

    connected: int
    inventorying: int


ClientFactory = Callable[
    [str, int, float, int],
    tuple[SllurpReaderClient, SllurpStateIds],
]


def _create_client(
    host: str,
    port: int,
    timeout_seconds: float,
    antenna_id: int,
) -> tuple[SllurpReaderClient, SllurpStateIds]:
    from sllurp.llrp import LLRPReaderClient, LLRPReaderConfig, LLRPReaderState

    config = LLRPReaderConfig(
        {
            "antennas": [antenna_id],
            "start_inventory": False,
            "reset_on_connect": False,
            "reconnect": False,
            "keepalive_interval": 0,
            "report_every_n_tags": 1,
            "session": 0,
        }
    )
    client = LLRPReaderClient(
        host,
        port=port,
        config=config,
        timeout=timeout_seconds,
    )
    return (
        cast(SllurpReaderClient, client),
        SllurpStateIds(
            connected=LLRPReaderState.STATE_CONNECTED,
            inventorying=LLRPReaderState.STATE_INVENTORYING,
        ),
    )


class ZebraFX9600Reader:
    """Mantém uma sessão LLRP compartilhada e controla um inventário manual."""

    def __init__(
        self,
        host: str,
        port: int,
        reader_id: str,
        antenna_id: int,
        timeout_seconds: float,
        *,
        client_factory: ClientFactory = _create_client,
    ) -> None:
        self._host = host
        self._port = port
        self._reader_id = reader_id
        self._next_host = host
        self._next_port = port
        self._next_reader_id = reader_id
        self._antenna_id = antenna_id
        self._timeout_seconds = timeout_seconds
        self._client_factory = client_factory
        self._client: SllurpReaderClient | None = None
        self._states: SllurpStateIds | None = None
        self._tag_callback: TagCallback | None = None
        self._disconnect_callback: DisconnectCallback = lambda: None
        self._lock = threading.Lock()
        self._operation_lock = threading.RLock()
        self._configured = threading.Event()
        self._configuration_failed = threading.Event()
        self._inventorying = threading.Event()
        self._inventory_requested = False
        self._accept_reports = False
        self._stop_complete = threading.Event()
        self._stop_complete.set()

    def connect(self) -> None:
        """Abre a sessão e aguarda a configuração transitória do cliente LLRP."""

        with self._operation_lock:
            if self.is_connected():
                return
            with self._lock:
                self._host = self._next_host
                self._port = self._next_port
                self._reader_id = self._next_reader_id
            self._configured.clear()
            self._configuration_failed.clear()
            client, states = self._client_factory(
                self._host,
                self._port,
                self._timeout_seconds,
                self._antenna_id,
            )
            with self._lock:
                self._client = client
                self._states = states
            client.add_message_callback(
                "SET_READER_CONFIG_RESPONSE",
                self._on_configuration_response,
            )
            client.add_state_callback(states.inventorying, self._on_inventorying)
            client.add_tag_report_callback(self._on_tag_report)
            client.add_disconnected_callback(self._on_disconnected)
            try:
                client.connect()
            except TimeoutError as error:
                self._clear_client(client)
                raise ReaderTimeoutError(
                    f"timeout ao conectar a {self._host}:{self._port}"
                ) from error
            except OSError as error:
                self._clear_client(client)
                raise ReaderConnectionError(
                    f"não foi possível conectar a {self._host}:{self._port}"
                ) from error
            except Exception as error:
                self._clear_client(client)
                raise ReaderProtocolError("falha ao iniciar a sessão LLRP") from error

            if not self._configured.wait(self._timeout_seconds):
                self._disconnect_client(client)
                self._clear_client(client)
                raise ReaderTimeoutError("timeout ao preparar a sessão LLRP")
            if self._configuration_failed.is_set() or not client.is_alive():
                self._disconnect_client(client)
                self._clear_client(client)
                raise ReaderProtocolError("o reader rejeitou a sessão LLRP")
            LOGGER.info(
                "reader_connected reader_id=%s reader_host=%s reader_port=%s",
                self._reader_id,
                self._host,
                self._port,
            )

    def configure_connection(self, host: str, port: int, reader_id: str) -> None:
        """Prepara valores que serão usados somente na próxima conexão."""

        with self._lock:
            self._next_host = host
            self._next_port = port
            self._next_reader_id = reader_id
        LOGGER.info(
            "reader_next_connection_configured reader_id=%s reader_host=%s reader_port=%s",
            reader_id,
            host,
            port,
        )

    def _on_configuration_response(
        self,
        client: SllurpReaderClient,
        message: SllurpMessage,
    ) -> None:
        with self._lock:
            if client is not self._client:
                return
        if not message.isSuccess():
            self._configuration_failed.set()
        self._configured.set()

    def is_connected(self) -> bool:
        with self._lock:
            client = self._client
        return bool(
            client is not None
            and self._configured.is_set()
            and not self._configuration_failed.is_set()
            and client.is_alive()
        )

    def start_inventory(self, callback: TagCallback) -> bool:
        """Solicita um único inventário na antena configurada."""

        with self._operation_lock:
            if not self.is_connected():
                raise ReaderConnectionError("o reader não está conectado")
            with self._lock:
                if self._inventory_requested:
                    return False
                client = self._client
                self._tag_callback = callback
                self._inventory_requested = True
                self._accept_reports = True
                self._stop_complete.clear()
                self._inventorying.clear()
            if client is None:
                raise ReaderConnectionError("o reader não está conectado")
            try:
                client.llrp.startInventory(force_regen_rospec=True)
            except Exception as error:
                with self._lock:
                    self._inventory_requested = False
                    self._accept_reports = False
                    self._tag_callback = None
                    self._stop_complete.set()
                raise ReaderProtocolError("não foi possível iniciar o inventário") from error
            LOGGER.info(
                "inventory_start_requested reader_id=%s antenna=%s",
                self._reader_id,
                self._antenna_id,
            )
            if not self._inventorying.wait(self._timeout_seconds) or not self.is_connected():
                self.disconnect()
                raise ReaderTimeoutError("timeout ao confirmar o início do inventário")
            return True

    def _on_inventorying(self, client: SllurpReaderClient, state: int) -> None:
        with self._lock:
            if client is not self._client or not self._inventory_requested:
                return
            self._inventorying.set()
        LOGGER.info(
            "inventory_started reader_id=%s antenna=%s",
            self._reader_id,
            self._antenna_id,
        )

    def stop_inventory(self) -> bool:
        """Bloqueia relatórios e remove o ROSpec transitório."""

        with self._operation_lock:
            with self._lock:
                if not self._inventory_requested:
                    return False
                client = self._client
                states = self._states
                self._inventory_requested = False
                self._accept_reports = False
                self._tag_callback = None
                self._inventorying.clear()
            if client is None or states is None or not client.is_alive():
                self._stop_complete.set()
                return False

            stop_succeeded = threading.Event()

            def on_stopped(state: int, is_success: bool, *args: object) -> None:
                if is_success:
                    client.llrp.setState(states.connected)
                    stop_succeeded.set()
                self._stop_complete.set()

            try:
                client.llrp.stopPolitely(onCompletion=on_stopped)
            except Exception as error:
                self._stop_complete.set()
                raise ReaderProtocolError("não foi possível parar o inventário") from error

            if not self._stop_complete.wait(self._timeout_seconds):
                raise ReaderProtocolError("timeout ao parar o inventário")
            if not stop_succeeded.is_set():
                raise ReaderProtocolError("o reader rejeitou a parada do inventário")
            LOGGER.info(
                "inventory_stopped reader_id=%s antenna=%s",
                self._reader_id,
                self._antenna_id,
            )
            return True

    def is_inventorying(self) -> bool:
        return self._inventorying.is_set()

    def _on_tag_report(
        self,
        client: SllurpReaderClient,
        tags: object,
    ) -> None:
        with self._lock:
            if client is not self._client or not self._accept_reports or not isinstance(tags, list):
                return
            callback = self._tag_callback
        if callback is None:
            return
        for raw_tag in tags:
            if not isinstance(raw_tag, dict):
                LOGGER.warning("invalid_tag_report reader_id=%s", self._reader_id)
                continue
            tag = self._to_tag_read(raw_tag)
            if tag is not None:
                callback(tag)

    def _to_tag_read(self, raw_tag: dict[object, object]) -> TagRead | None:
        raw_epc = raw_tag.get("EPC")
        if isinstance(raw_epc, bytes):
            try:
                epc = raw_epc.decode("ascii")
            except UnicodeDecodeError:
                LOGGER.warning("invalid_epc_encoding reader_id=%s", self._reader_id)
                return None
        elif isinstance(raw_epc, str):
            epc = raw_epc
        else:
            LOGGER.warning("missing_epc reader_id=%s", self._reader_id)
            return None
        antenna = raw_tag.get("AntennaID")
        seen_count = raw_tag.get("TagSeenCount")
        return TagRead(
            epc=epc,
            reader_id=self._reader_id,
            antenna_id=antenna if isinstance(antenna, int) else None,
            read_at=datetime.now(UTC),
            seen_count=seen_count if isinstance(seen_count, int) else None,
        )

    def set_disconnect_callback(self, callback: DisconnectCallback) -> None:
        with self._lock:
            self._disconnect_callback = callback

    def _on_disconnected(self, client: SllurpReaderClient) -> None:
        with self._lock:
            if client is not self._client:
                return
            was_inventorying = self._inventory_requested
            self._inventory_requested = False
            self._accept_reports = False
            self._tag_callback = None
            callback = self._disconnect_callback
        self._configured.clear()
        self._inventorying.clear()
        self._stop_complete.set()
        LOGGER.warning(
            "reader_disconnected reader_id=%s reader_host=%s inventory_active=%s",
            self._reader_id,
            self._host,
            was_inventorying,
        )
        callback()

    def disconnect(self) -> None:
        """Encerra inventário, thread e socket da sessão compartilhada."""

        with self._operation_lock:
            if self._inventory_requested:
                try:
                    self.stop_inventory()
                except ReaderProtocolError:
                    LOGGER.exception("inventory_stop_before_disconnect_failed")
            with self._lock:
                client = self._client
                self._accept_reports = False
                self._tag_callback = None
            if client is None:
                return
            self._disconnect_client(client)
            self._clear_client(client)
            LOGGER.info(
                "reader_disconnected_by_application reader_id=%s reader_host=%s",
                self._reader_id,
                self._host,
            )

    def _disconnect_client(self, client: SllurpReaderClient) -> None:
        try:
            client.disconnect(timeout=self._timeout_seconds)
            if client.is_alive():
                client.hard_disconnect()
                client.join(self._timeout_seconds)
        except Exception:
            LOGGER.exception(
                "reader_disconnect_failed reader_id=%s reader_host=%s",
                self._reader_id,
                self._host,
            )
            try:
                client.hard_disconnect()
            except Exception:
                LOGGER.exception(
                    "reader_hard_disconnect_failed reader_id=%s",
                    self._reader_id,
                )

    def _clear_client(self, client: SllurpReaderClient) -> None:
        with self._lock:
            if client is self._client:
                self._client = None
                self._states = None
                self._inventory_requested = False
                self._accept_reports = False
                self._tag_callback = None
        self._configured.clear()
        self._configuration_failed.clear()
        self._inventorying.clear()
        self._stop_complete.set()
