"""Research domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from districtintel.models.fact import Fact


class ConfidenceLevel(StrEnum):
    """Confidence assigned to a research result."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNKNOWN = "unknown"


class ResearchStatus(StrEnum):
    """Lifecycle status for a research job or result."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SourceType(StrEnum):
    """Controlled vocabulary for source categories."""

    COUNTY_AUDITOR = "county_auditor"
    OFCC = "ofcc"
    DISTRICT_FACILITY_PLAN = "district_facility_plan"
    DISTRICT_WEBSITE = "district_website"
    BOARD_MINUTES = "board_minutes"
    ARCHITECT_DOCUMENT = "architect_document"
    GOVERNMENT_PUBLICATION = "government_publication"
    LOCAL_NEWS = "local_news"
    OTHER = "other"


@dataclass(frozen=True, slots=True)
class Source:
    """A source that may support research evidence."""

    title: str
    url: str | None = None
    source_type: SourceType = SourceType.OTHER
    published_at: datetime | None = None
    accessed_at: datetime | None = None
    id: int | None = None


@dataclass(frozen=True, slots=True)
class Evidence:
    """A specific piece of evidence collected from a source."""

    source: Source
    excerpt: str
    notes: str | None = None
    id: int | None = None


@dataclass(frozen=True, slots=True)
class ResearchJob:
    """A unit of research work for one school and one agent."""

    school_id: int
    agent_name: str
    status: ResearchStatus = ResearchStatus.PENDING
    id: int | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error_message: str | None = None


@dataclass(frozen=True, slots=True)
class ResearchResult:
    """Structured output from a research agent.

    Research agents should use the structured Fact model for queryable claims
    such as year_built, renovation_year, bond_issue, architect, and
    facility_condition. Summaries remain supplemental and should not replace
    evidence-backed facts when a structured value is possible.
    """

    school_id: int
    agent_name: str
    status: ResearchStatus
    confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    summary: str | None = None
    evidence: tuple[Evidence, ...] = field(default_factory=tuple)
    facts: tuple[Fact, ...] = field(default_factory=tuple)
    job_id: int | None = None
    id: int | None = None
    error_message: str | None = None
