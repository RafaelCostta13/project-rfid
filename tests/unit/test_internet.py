from urllib.error import URLError
from urllib.request import Request

import pytest

from rfid_reader.domain import ConnectionStatus
from rfid_reader.services import internet
from rfid_reader.services.internet import (
    InternetConnectionChecker,
    _open_url,
    backend_health_url,
)


class FakeResponse:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


def test_health_probe_uses_https_get_request(monkeypatch: pytest.MonkeyPatch) -> None:
    response = FakeResponse()
    requests = []

    def fake_urlopen(request: Request, timeout: float) -> FakeResponse:
        requests.append((request, timeout))
        return response

    monkeypatch.setattr(internet, "urlopen", fake_urlopen)

    assert _open_url("https://backend.test/api/v1/health", 1.0) is response
    assert requests[0][0].full_url == "https://backend.test/api/v1/health"
    assert requests[0][0].get_method() == "GET"
    assert requests[0][1] == 1.0


def test_builds_https_health_url_from_backend_base_url() -> None:
    assert backend_health_url(" https://backend.test/ ") == "https://backend.test/api/v1/health"
    assert backend_health_url("http://backend.test") == "https://backend.test/api/v1/health"
    assert backend_health_url("") == ""
    assert backend_health_url("https://") == ""


def test_reports_connected_and_closes_backend_health_response() -> None:
    response = FakeResponse()
    requests: list[tuple[str, float]] = []

    def request_factory(url: str, timeout: float) -> FakeResponse:
        requests.append((url, timeout))
        return response

    checker = InternetConnectionChecker(
        1.0,
        url=backend_health_url("https://backend.test"),
        request_factory=request_factory,
    )

    assert checker.check() is ConnectionStatus.CONNECTED
    assert requests == [("https://backend.test/api/v1/health", 1.0)]
    assert response.closed


def test_reports_disconnected_when_probe_fails() -> None:
    def fail_request(url: str, timeout: float) -> FakeResponse:
        raise URLError("rede indisponível")

    checker = InternetConnectionChecker(
        1.0,
        url=backend_health_url("https://backend.test"),
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
        url=backend_health_url("https://backend.test"),
        request_factory=request_factory,
    )
    checker.close()

    assert checker.check() is ConnectionStatus.DISCONNECTED
    assert not request_attempted


def test_reports_disconnected_without_backend_url_without_request() -> None:
    request_attempted = False

    def request_factory(url: str, timeout: float) -> FakeResponse:
        nonlocal request_attempted
        request_attempted = True
        return FakeResponse()

    checker = InternetConnectionChecker(1.0, url="", request_factory=request_factory)

    assert checker.check() is ConnectionStatus.DISCONNECTED
    assert not request_attempted
