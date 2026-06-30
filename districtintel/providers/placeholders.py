"""Placeholder source providers for future implementations."""

from __future__ import annotations

from districtintel.models import Evidence, ProviderContext, School
from districtintel.providers.capabilities import ProviderCapability


class EmptySourceProvider:
    """Base placeholder provider that performs no work and no network calls."""

    name = "empty-source-provider"
    capabilities: tuple[ProviderCapability, ...] = ()

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
    capabilities = (
        ProviderCapability.YEAR_BUILT,
        ProviderCapability.SQUARE_FOOTAGE,
    )


class DistrictWebsiteProvider(EmptySourceProvider):
    """Placeholder for future district website evidence collection."""

    name = "district-website"
    capabilities = (
        ProviderCapability.CONTACT_INFORMATION,
        ProviderCapability.ARCHITECT,
    )


class OfccProvider(EmptySourceProvider):
    """Placeholder for future OFCC evidence collection."""

    name = "ofcc"
    capabilities = (ProviderCapability.OFCC_INFORMATION,)


class BoardMinutesProvider(EmptySourceProvider):
    """Placeholder for future board minutes evidence collection."""

    name = "board-minutes"
    capabilities = (
        ProviderCapability.BOARD_DISCUSSIONS,
        ProviderCapability.BOND_HISTORY,
        ProviderCapability.LEVY_HISTORY,
    )


class LocalNewsProvider(EmptySourceProvider):
    """Placeholder for future local news evidence collection."""

    name = "local-news"
    capabilities = (ProviderCapability.NEWS,)
