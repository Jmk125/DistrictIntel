"""Research framework interfaces and coordination."""

from districtintel.research.coordinator import ResearchCoordinator
from districtintel.research.interfaces import ResearchAgent, SourceProvider

__all__ = ["ResearchAgent", "ResearchCoordinator", "SourceProvider"]
