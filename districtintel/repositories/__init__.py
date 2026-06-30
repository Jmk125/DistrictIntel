"""Repository layer for DistrictIntel persistence."""

from districtintel.repositories.districts import DistrictRepository
from districtintel.repositories.evidence import EvidenceRepository
from districtintel.repositories.facts import FactRepository
from districtintel.repositories.research import ResearchJobRepository, ResearchResultRepository
from districtintel.repositories.schools import SchoolRepository

__all__ = [
    "DistrictRepository",
    "EvidenceRepository",
    "FactRepository",
    "ResearchJobRepository",
    "ResearchResultRepository",
    "SchoolRepository",
]
