"""Source provider domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from districtintel.models.research import Evidence


@dataclass(frozen=True, slots=True)
class ProviderContext:
    """Context shared with source providers during evidence collection."""

    research_job_id: int | None = None
    requested_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ProviderResult:
    """Result of executing one source provider."""

    provider_name: str
    evidence: tuple[Evidence, ...] = field(default_factory=tuple)
    error_message: str | None = None

    @property
    def succeeded(self) -> bool:
        """Return whether the provider completed without an error."""

        return self.error_message is None
