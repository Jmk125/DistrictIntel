"""Interfaces for pluggable research components."""

from __future__ import annotations

from typing import Protocol

from districtintel.models import Evidence, ResearchResult, School


class SourceProvider(Protocol):
    """Collects evidence for a school without deciding the final result."""

    name: str

    def collect_evidence(self, school: School) -> tuple[Evidence, ...]:
        """Collect candidate evidence for a school."""


class ResearchAgent(Protocol):
    """Researches one question for one school."""

    name: str

    def research(self, school: School, evidence: tuple[Evidence, ...]) -> ResearchResult:
        """Research a school using already-collected evidence."""
