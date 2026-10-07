import errno

import pytest
from pymodbus.exceptions import ModbusIOException

from rfid_reader.domain import WaveshareConnectionSettings
from rfid_reader.integrations.waveshare_modbus import (
    PymodbusWaveshareConnectionTester,
    WavesharePortBusyError,
    WavesharePortOpenError,
    WaveshareProtocolError,
    WaveshareTimeoutError,
)


def connection_settings() -> WaveshareConnectionSettings:
    return WaveshareConnectionSettings("COM5", 9600, 8, "None", 1, 1)


class FakeResponse:
    def __init__(self, error: bool = False) -> None:
        self._error = error

    def isError(self) -> bool:  # noqa: N802 - API do PyModbus
        return self._error


class FakeClient:
    def __init__(
        self,
        *,
        connected: bool = True,
        connect_error: OSError | None = None,
        read_error: Exception | None = None,
        response: FakeResponse | None = None,
    ) -> None:
        self.connected = connected
        self.connect_error = connect_error
        self.read_error = read_error
        self.response = response or FakeResponse()
        self.read_calls: list[tuple[int, int, int]] = []
        self.close_calls = 0

    def connect(self) -> bool:
        if self.connect_error is not None:
            raise self.connect_error
        return self.connected

    def read_discrete_inputs(
        self,
        address: int,
        *,
        count: int,
        device_id: int,
    ) -> FakeResponse:
        self.read_calls.append((address, count, device_id))
        if self.read_error is not None:
            raise self.read_error
        return self.response

    def close(self) -> None:
        self.close_calls += 1


def make_tester(client: FakeClient) -> PymodbusWaveshareConnectionTester:
    def factory(settings: WaveshareConnectionSettings, timeout: float) -> FakeClient:
        return client

    return PymodbusWaveshareConnectionTester(factory)


def test_connection_reads_discrete_inputs_without_writing_and_closes() -> None:
    client = FakeClient()

    make_tester(client).test(connection_settings())

    assert client.read_calls == [(0, 2, 1)]
    assert client.close_calls == 1
    assert not hasattr(client, "write_coil")


@pytest.mark.parametrize(
    ("client", "expected_error"),
    [
        (FakeClient(connected=False), WavesharePortOpenError),
        (
            FakeClient(connect_error=OSError(errno.ENOENT, "porta inexistente")),
            WavesharePortOpenError,
        ),
        (
            FakeClient(connect_error=OSError(errno.EACCES, "access is denied")),
            WavesharePortBusyError,
        ),
        (
            FakeClient(read_error=ModbusIOException("sem resposta")),
            WaveshareTimeoutError,
        ),
        (FakeClient(response=FakeResponse(error=True)), WaveshareProtocolError),
    ],
)
def test_connection_translates_failures_and_always_closes(
    client: FakeClient,
    expected_error: type[Exception],
) -> None:
    with pytest.raises(expected_error):
        make_tester(client).test(connection_settings())

    assert client.close_calls == 1
