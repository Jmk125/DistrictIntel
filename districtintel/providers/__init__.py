"""Source provider framework."""

from districtintel.providers.capabilities import ProviderCapability
from districtintel.providers.coordinator import ProviderCoordinator
from districtintel.providers.interfaces import SourceProvider
from districtintel.providers.placeholders import (
    BoardMinutesProvider,
    CountyAuditorProvider,
    DistrictWebsiteProvider,
    LocalNewsProvider,
    OfccProvider,
)
from districtintel.providers.registry import ProviderRegistry, register_provider

__all__ = [
    "BoardMinutesProvider",
    "CountyAuditorProvider",
    "DistrictWebsiteProvider",
    "LocalNewsProvider",
    "OfccProvider",
    "ProviderCapability",
    "ProviderCoordinator",
    "ProviderRegistry",
    "SourceProvider",
    "register_provider",
]
