"""Provider interfaces."""

from __future__ import annotations

from typing import Protocol

from districtintel.models import Evidence, ProviderContext, School


class SourceProvider(Protocol):
    """Collects evidence for a school without persistence, facts, or AI calls."""

    name: str

    def collect_evidence(
        self,
        school: School,
        context: ProviderContext,
    ) -> tuple[Evidence, ...]:
        """Collect candidate evidence for a school."""
