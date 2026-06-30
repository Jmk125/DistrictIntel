"""Interfaces for pluggable research components."""

from __future__ import annotations

from typing import Protocol

from districtintel.models import Evidence, ResearchResult, School
from districtintel.providers.interfaces import SourceProvider


class ResearchAgent(Protocol):
    """Researches one question for one school."""

    name: str

    def research(self, school: School, evidence: tuple[Evidence, ...]) -> ResearchResult:
        """Research a school using already-collected evidence."""


__all__ = ["ResearchAgent", "SourceProvider"]
