"""Research coordinator behavior tests."""

from __future__ import annotations

from districtintel.models import (
    ConfidenceLevel,
    Evidence,
    ResearchResult,
    ResearchStatus,
    School,
    Source,
)
from districtintel.research import ResearchCoordinator


class FakeProvider:
    """Fake source provider for coordinator tests."""

    name = "fake-provider"

    def collect_evidence(self, school: School) -> tuple[Evidence, ...]:
        return (
            Evidence(
                source=Source(title=f"{school.name} source"),
                excerpt="Evidence excerpt.",
            ),
        )


class FakeAgent:
    """Fake research agent for coordinator tests."""

    name = "fake-agent"

    def research(self, school: School, evidence: tuple[Evidence, ...]) -> ResearchResult:
        return ResearchResult(
            school_id=school.id or 0,
            agent_name=self.name,
            status=ResearchStatus.COMPLETED,
            confidence=ConfidenceLevel.MEDIUM,
            summary=f"Reviewed {len(evidence)} evidence item(s).",
            evidence=evidence,
        )


class FailingAgent:
    """Fake research agent that fails deterministically."""

    name = "failing-agent"

    def research(self, school: School, evidence: tuple[Evidence, ...]) -> ResearchResult:
        raise RuntimeError("planned failure")


def test_coordinator_delegates_evidence_to_agent() -> None:
    """The coordinator gathers evidence and passes it to the research agent."""

    school = School(id=10, district_id=1, name="Example Elementary")
    coordinator = ResearchCoordinator(source_providers=(FakeProvider(),))

    result = coordinator.run(school=school, agent=FakeAgent())

    assert result.status == ResearchStatus.COMPLETED
    assert result.school_id == 10
    assert result.summary == "Reviewed 1 evidence item(s)."
    assert len(result.evidence) == 1


def test_coordinator_returns_failed_result_when_agent_raises() -> None:
    """Agent exceptions are represented as failed research results."""

    school = School(id=10, district_id=1, name="Example Elementary")
    coordinator = ResearchCoordinator()

    result = coordinator.run(school=school, agent=FailingAgent())

    assert result.status == ResearchStatus.FAILED
    assert result.confidence == ConfidenceLevel.UNKNOWN
    assert result.error_message == "planned failure"
