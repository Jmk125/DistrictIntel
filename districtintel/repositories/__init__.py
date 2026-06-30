"""Repository layer for DistrictIntel persistence."""

from districtintel.repositories.districts import DistrictRepository
from districtintel.repositories.research import ResearchJobRepository, ResearchResultRepository
from districtintel.repositories.schools import SchoolRepository

__all__ = [
    "DistrictRepository",
    "ResearchJobRepository",
    "ResearchResultRepository",
    "SchoolRepository",
]
