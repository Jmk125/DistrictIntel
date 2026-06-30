"""Web fetch result models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True, slots=True)
class FetchResult:
    """Normalized result returned by the web fetch layer."""

    url: str
    final_url: str | None = None
    status_code: int | None = None
    content_type: str | None = None
    text: str | None = None
    fetched_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    error_message: str | None = None

    @property
    def succeeded(self) -> bool:
        """Return whether the fetch completed with a successful HTTP status."""

        return (
            self.error_message is None
            and self.status_code is not None
            and 200 <= self.status_code < 400
        )
