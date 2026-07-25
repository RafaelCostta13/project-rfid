from urllib.error import URLError

from rfid_reader.domain import ConnectionStatus
from rfid_reader.services.internet import (
    DEFAULT_CONNECTIVITY_URL,
    InternetConnectionChecker,
)


class FakeResponse:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


def test_reports_connected_and_closes_https_response() -> None:
    response = FakeResponse()
    requests: list[tuple[str, float]] = []

    def request_factory(url: str, timeout: float) -> FakeResponse:
        requests.append((url, timeout))
        return response

    checker = InternetConnectionChecker(
        1.0,
        request_factory=request_factory,
    )

    assert checker.check() is ConnectionStatus.CONNECTED
    assert requests == [(DEFAULT_CONNECTIVITY_URL, 1.0)]
    assert response.closed


def test_reports_disconnected_when_probe_fails() -> None:
    def fail_request(url: str, timeout: float) -> FakeResponse:
        raise URLError("rede indisponível")

    checker = InternetConnectionChecker(
        1.0,
        request_factory=fail_request,
    )

    assert checker.check() is ConnectionStatus.DISCONNECTED


def test_close_prevents_new_probes() -> None:
    request_attempted = False

    def request_factory(url: str, timeout: float) -> FakeResponse:
        nonlocal request_attempted
        request_attempted = True
        return FakeResponse()

    checker = InternetConnectionChecker(
        1.0,
        request_factory=request_factory,
    )
    checker.close()

    assert checker.check() is ConnectionStatus.DISCONNECTED
    assert not request_attempted
