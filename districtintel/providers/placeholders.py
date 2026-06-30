"""Placeholder source providers for future implementations."""

from __future__ import annotations

from districtintel.models import Evidence, ProviderContext, School


class EmptySourceProvider:
    """Base placeholder provider that performs no work and no network calls."""

    name = "empty-source-provider"

    def collect_evidence(
        self,
        school: School,
        context: ProviderContext,
    ) -> tuple[Evidence, ...]:
        """Return no evidence until a real provider is implemented."""

        return ()


class CountyAuditorProvider(EmptySourceProvider):
    """Placeholder for future county auditor evidence collection."""

    name = "county-auditor"


class DistrictWebsiteProvider(EmptySourceProvider):
    """Placeholder for future district website evidence collection."""

    name = "district-website"


class OfccProvider(EmptySourceProvider):
    """Placeholder for future OFCC evidence collection."""

    name = "ofcc"


class BoardMinutesProvider(EmptySourceProvider):
    """Placeholder for future board minutes evidence collection."""

    name = "board-minutes"


class LocalNewsProvider(EmptySourceProvider):
    """Placeholder for future local news evidence collection."""

    name = "local-news"
