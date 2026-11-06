"""Verificação de acesso à internet."""

from __future__ import annotations

import logging
import threading
from collections.abc import Callable
from typing import Protocol, cast
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, urlunsplit
from urllib.request import Request, urlopen

from rfid_reader.domain import ConnectionStatus

LOGGER = logging.getLogger(__name__)
BACKEND_HEALTH_PATH = "/api/v1/health"


class ResponseLike(Protocol):
    def close(self) -> None: ...


RequestFactory = Callable[[str, float], ResponseLike]


def _open_url(url: str, timeout: float) -> ResponseLike:
    request = Request(
        url,
        headers={"User-Agent": "rfid-reader/0.1"},
        method="GET",
    )
    try:
        return cast(ResponseLike, urlopen(request, timeout=timeout))
    except HTTPError as error:
        # Uma resposta HTTP, mesmo 4xx/5xx, confirma que a internet está acessível.
        return error


def backend_health_url(base_url: str) -> str:
    """Monta a URL HTTPS de health a partir da URL base configurada do Backend."""

    value = base_url.strip()
    if not value:
        return ""
    parsed = urlsplit(value if "://" in value else f"https://{value}")
    if not parsed.hostname:
        return ""
    path = f"{parsed.path.rstrip('/')}{BACKEND_HEALTH_PATH}"
    return urlunsplit(("https", parsed.netloc, path, "", ""))


class InternetConnectionChecker:
    """Testa conectividade por uma requisição HTTPS curta."""

    def __init__(
        self,
        timeout_seconds: float,
        *,
        url: str,
        request_factory: RequestFactory = _open_url,
    ) -> None:
        self._timeout_seconds = timeout_seconds
        self._url = url
        self._request_factory = request_factory
        self._lock = threading.Lock()
        self._active_response: ResponseLike | None = None
        self._closed = threading.Event()

    def check(self) -> ConnectionStatus:
        if self._closed.is_set():
            return ConnectionStatus.DISCONNECTED
        if not self._url:
            LOGGER.debug("internet_connection_unavailable reason=backend_url_not_configured")
            return ConnectionStatus.DISCONNECTED
        try:
            response = self._request_factory(self._url, self._timeout_seconds)
        except (TimeoutError, OSError, URLError) as error:
            LOGGER.debug(
                "internet_connection_unavailable target=%s error=%s",
                self._url,
                error,
            )
            return ConnectionStatus.DISCONNECTED

        with self._lock:
            if self._closed.is_set():
                response.close()
                return ConnectionStatus.DISCONNECTED
            self._active_response = response
        try:
            return ConnectionStatus.CONNECTED
        finally:
            with self._lock:
                self._active_response = None
            try:
                response.close()
            except OSError:
                LOGGER.debug("internet_response_close_failed", exc_info=True)

    def close(self) -> None:
        self._closed.set()
        with self._lock:
            response = self._active_response
        if response is not None:
            try:
                response.close()
            except OSError:
                LOGGER.debug("internet_response_close_failed", exc_info=True)
