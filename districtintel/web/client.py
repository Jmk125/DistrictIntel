"""Safe reusable web client."""

from __future__ import annotations

from collections.abc import Callable
from http.client import HTTPResponse
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from districtintel.web.models import FetchResult

DEFAULT_TIMEOUT_SECONDS = 10.0
DEFAULT_USER_AGENT = "DistrictIntel/0.1 (+https://github.com/)"

UrlOpen = Callable[..., HTTPResponse]


class WebClient:
    """Fetch URLs and return normalized FetchResult objects.

    The client intentionally does not parse, scrape, persist, or interpret fetched
    content. It only performs a safe HTTP GET with a small in-memory cache for the
    lifetime of this client instance.
    """

    def __init__(
        self,
        *,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        user_agent: str = DEFAULT_USER_AGENT,
        opener: UrlOpen = urlopen,
    ) -> None:
        self._timeout_seconds = timeout_seconds
        self._user_agent = user_agent
        self._opener = opener
        self._cache: dict[str, FetchResult] = {}

    def fetch(self, url: str) -> FetchResult:
        """Fetch a URL or return the in-memory cached result."""

        if url in self._cache:
            return self._cache[url]

        request = Request(url, headers={"User-Agent": self._user_agent})
        try:
            with self._opener(request, timeout=self._timeout_seconds) as response:
                result = _result_from_response(url, response)
        except HTTPError as exc:
            result = _result_from_http_error(url, exc)
        except TimeoutError as exc:
            result = FetchResult(url=url, error_message=f"Request timed out: {exc}")
        except URLError as exc:
            result = FetchResult(url=url, error_message=f"Request failed: {exc.reason}")
        except OSError as exc:
            result = FetchResult(url=url, error_message=f"Request failed: {exc}")

        self._cache[url] = result
        return result


def _result_from_response(url: str, response: HTTPResponse) -> FetchResult:
    body = response.read()
    content_type = response.headers.get("Content-Type")
    return FetchResult(
        url=url,
        final_url=response.geturl(),
        status_code=response.status,
        content_type=content_type,
        text=_decode_body(body, content_type),
    )


def _result_from_http_error(url: str, error: HTTPError) -> FetchResult:
    body = error.read()
    content_type = error.headers.get("Content-Type") if error.headers else None
    return FetchResult(
        url=url,
        final_url=error.geturl(),
        status_code=error.code,
        content_type=content_type,
        text=_decode_body(body, content_type),
        error_message=f"HTTP error {error.code}: {error.reason}",
    )


def _decode_body(body: bytes, content_type: str | None) -> str:
    encoding = _encoding_from_content_type(content_type) or "utf-8"
    return body.decode(encoding, errors="replace")


def _encoding_from_content_type(content_type: str | None) -> str | None:
    if content_type is None:
        return None
    parts = [part.strip() for part in content_type.split(";")]
    for part in parts[1:]:
        key, separator, value = part.partition("=")
        if separator and key.lower() == "charset" and value:
            return value.strip('"')
    return None
