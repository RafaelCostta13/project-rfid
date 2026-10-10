"""Simuladores isolados dos transportes; nenhum socket ou porta COM é aberto."""

import json
import threading
from collections.abc import Callable
from datetime import UTC, datetime
from urllib.request import Request

from rfid_reader.domain import ConnectionStatus, TagRead
from rfid_reader.integrations.backend_client import HttpResponse
from rfid_reader.integrations.waveshare_modbus import (
    WavesharePortBusyError,
    WaveshareSerialGate,
    WaveshareTimeoutError,
)
from rfid_reader.readers.base import ReaderConnectionError

EPC = "E280691500005029EEA6A275"


class Reader:
    def __init__(self) -> None:
        self.connected = False
        self.reading = False
        self.starts = 0
        self.stops = 0
        self.connections = 0
        self.fail_start = False
        self.fail_connect = False
        self.callback: Callable[[TagRead], None] = lambda tag: None
        self.on_disconnect: Callable[[], None] = lambda: None

    def connect(self) -> None:
        if self.fail_connect:
            raise ReaderConnectionError("simulado")
        if not self.connected:
            self.connections += 1
        self.connected = True

    def disconnect(self) -> None:
        self.connected = False
        self.reading = False
        self.on_disconnect()

    def is_connected(self) -> bool:
        return self.connected

    def is_inventorying(self) -> bool:
        return self.reading

    def configure_connection(self, host: str, port: int, reader_id: str) -> None:
        pass

    def set_disconnect_callback(self, callback: Callable[[], None]) -> None:
        self.on_disconnect = callback

    def start_inventory(self, callback: Callable[[TagRead], None]) -> bool:
        self.starts += 1
        self.callback = callback
        self.reading = not self.fail_start
        return self.reading

    def stop_inventory(self) -> bool:
        self.stops += 1
        self.reading = False
        return True

    def emit(self, epc: str = EPC) -> None:
        self.callback(TagRead(epc, "simulated", 1, datetime.now(UTC)))


class Timer:
    def __init__(self, seconds: float, callback: Callable[[], None]) -> None:
        assert seconds == 60
        self.callback = callback
        self.cancelled = False
        self.started = False

    def start(self) -> None:
        self.started = True

    def cancel(self) -> None:
        self.cancelled = True


class Port:
    def __init__(self) -> None:
        self.inputs = (True, True, False, True, False)
        self.relays = [False] * 8
        self.writes: list[tuple[int, bool]] = []
        self.opens = 0
        self.closed = False
        self.samples = 0
        self.fail = False

    def connect(self) -> tuple[bool, ...]:
        self.opens += 1
        self.closed = False
        return self.read_inputs()

    def read_inputs(self) -> tuple[bool, ...]:
        if self.fail:
            raise WaveshareTimeoutError("simulado")
        self.samples += 1
        return self.inputs

    def read_relays(self) -> tuple[bool, ...]:
        return tuple(self.relays)

    def set_relay(self, channel: int, enabled: bool) -> bool:
        self.writes.append((channel, enabled))
        self.relays[channel - 1] = enabled
        return enabled

    def close(self) -> None:
        self.closed = True


class Tester:
    def __init__(self, gate: WaveshareSerialGate, port: Port) -> None:
        self.gate = gate
        self.port = port

    def test(self, settings: object) -> None:
        if self.gate.is_locked():
            raise WavesharePortBusyError("simulado")
        if self.port.fail:
            raise WaveshareTimeoutError("simulado")


class Internet:
    def check(self) -> ConnectionStatus:
        return ConnectionStatus.CONNECTED

    def close(self) -> None:
        pass


class Backend:
    def __init__(self) -> None:
        self.requests: list[Request] = []
        self.system = "ok"
        self.database = "ok"
        self.get_status: int | str = 200
        self.post_status: int | str = 200
        self.block: str | None = None
        self.entered = threading.Event()
        self.release = threading.Event()

    def transport(self, request: Request, timeout: float) -> HttpResponse:
        self.requests.append(request)
        if request.full_url.endswith("/health"):
            return self.response(200, {"status": self.system, "database": self.database})
        method = request.get_method()
        if self.block == method:
            self.entered.set()
            assert self.release.wait(5), "HTTP simulado não foi liberado"
        status = self.get_status if method == "GET" else self.post_status
        if status == "timeout":
            raise TimeoutError("simulado")
        if status != 200:
            return self.response(int(status), {"found": False, "error": "epc_not_found"})
        if method == "GET":
            record: dict[str, object] = {
                field: ""
                for field in (
                    "datahora",
                    "volume",
                    "pedido",
                    "notafiscal",
                    "destinatario",
                    "endereco",
                    "numero",
                    "cidade",
                    "uf",
                    "doca",
                    "fornecedor",
                    "status",
                )
            }
            record.update(
                epc=EPC,
                tag=None,
                first_read_at=None,
                last_read_at=None,
                read_count=0,
                status="pendente",
                destinatario="Cliente real do contrato",
                pedido="00042",
                notafiscal="00123",
                volume="2/4",
                doca="DOCA 35",
            )
            return self.response(200, {"found": True, "data": record})
        assert json.loads(request.data) == {"epc": EPC}
        return self.response(
            200,
            {
                "success": True,
                "epc": EPC,
                "first_read": True,
                "duplicate": False,
                "status": "lido",
                "read_count": 1,
                "first_read_at": "2026-10-09T12:00:00Z",
                "last_read_at": "2026-10-09T12:00:00Z",
            },
        )

    @staticmethod
    def response(status: int, document: dict[str, object]) -> HttpResponse:
        return HttpResponse(status, json.dumps(document).encode())

    def count(self, method: str) -> int:
        return sum(
            request.get_method() == method and not request.full_url.endswith("/health")
            for request in self.requests
        )
