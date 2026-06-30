"""Research domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum


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


@dataclass(frozen=True, slots=True)
class Source:
    """A source that may support research evidence."""

    title: str
    url: str | None = None
    source_type: str | None = None
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
    """Structured output from a research agent."""

    school_id: int
    agent_name: str
    status: ResearchStatus
    confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    summary: str | None = None
    evidence: tuple[Evidence, ...] = field(default_factory=tuple)
    job_id: int | None = None
    id: int | None = None
    error_message: str | None = None
