"""Web client tests."""

from __future__ import annotations

from io import BytesIO
from urllib.error import URLError
from urllib.request import Request

from districtintel.web import WebClient


class FakeResponse:
    """Minimal context-manager response for WebClient tests."""

    def __init__(
        self,
        *,
        body: bytes,
        url: str = "https://example.test/final",
        status: int = 200,
        content_type: str = "text/html; charset=utf-8",
    ) -> None:
        self._body = BytesIO(body)
        self._url = url
        self.status = status
        self.headers = {"Content-Type": content_type}

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        return None

    def read(self) -> bytes:
        return self._body.read()

    def geturl(self) -> str:
        return self._url


class RecordingOpener:
    """Callable opener that records requests for assertions."""

    def __init__(self, response: FakeResponse) -> None:
        self._response = response
        self.calls: list[tuple[Request, float]] = []

    def __call__(self, request: Request, *, timeout: float) -> FakeResponse:
        self.calls.append((request, timeout))
        return self._response


def test_web_client_successful_fetch() -> None:
    """Successful fetches return normalized FetchResult values."""

    opener = RecordingOpener(FakeResponse(body=b"<html>ok</html>"))
    client = WebClient(timeout_seconds=3.5, user_agent="DistrictIntel Test", opener=opener)

    result = client.fetch("https://example.test/page")

    assert result.succeeded is True
    assert result.url == "https://example.test/page"
    assert result.final_url == "https://example.test/final"
    assert result.status_code == 200
    assert result.content_type == "text/html; charset=utf-8"
    assert result.text == "<html>ok</html>"
    assert opener.calls[0][0].headers["User-agent"] == "DistrictIntel Test"
    assert opener.calls[0][1] == 3.5


def test_web_client_records_redirect_final_url() -> None:
    """Redirect handling exposes the final response URL."""

    opener = RecordingOpener(
        FakeResponse(
            body=b"redirected",
            url="https://example.test/final-page",
            status=200,
        )
    )
    client = WebClient(opener=opener)

    result = client.fetch("https://example.test/start")

    assert result.succeeded is True
    assert result.url == "https://example.test/start"
    assert result.final_url == "https://example.test/final-page"


def test_web_client_timeout_returns_failed_result() -> None:
    """Timeout errors are captured instead of raised."""

    def timeout_opener(request: Request, *, timeout: float) -> FakeResponse:
        raise TimeoutError("timed out")

    client = WebClient(opener=timeout_opener)

    result = client.fetch("https://example.test/slow")

    assert result.succeeded is False
    assert result.status_code is None
    assert result.error_message == "Request timed out: timed out"


def test_web_client_request_error_returns_failed_result() -> None:
    """Common URL errors are captured instead of raised."""

    def failing_opener(request: Request, *, timeout: float) -> FakeResponse:
        raise URLError("name resolution failed")

    client = WebClient(opener=failing_opener)

    result = client.fetch("https://example.invalid/")

    assert result.succeeded is False
    assert result.error_message == "Request failed: name resolution failed"


def test_web_client_reuses_in_memory_cache() -> None:
    """Fetching the same URL twice in one client instance uses the cache."""

    opener = RecordingOpener(FakeResponse(body=b"cached"))
    client = WebClient(opener=opener)

    first = client.fetch("https://example.test/cache")
    second = client.fetch("https://example.test/cache")

    assert first is second
    assert first.text == "cached"
    assert len(opener.calls) == 1
