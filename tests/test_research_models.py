"""Research domain model tests."""

from __future__ import annotations

from districtintel.models import ConfidenceLevel, Evidence, ResearchResult, ResearchStatus, Source


def test_research_result_defaults_to_tuple_evidence() -> None:
    """Research results keep evidence immutable by default."""

    result = ResearchResult(
        school_id=1,
        agent_name="fake-agent",
        status=ResearchStatus.COMPLETED,
        confidence=ConfidenceLevel.HIGH,
    )

    assert result.evidence == ()
    assert result.confidence == ConfidenceLevel.HIGH
    assert result.status == ResearchStatus.COMPLETED


def test_evidence_references_source() -> None:
    """Evidence keeps a direct link to its supporting source model."""

    source = Source(title="District facility plan", url="https://example.test/facility-plan")
    evidence = Evidence(source=source, excerpt="The building opened in 1995.")

    assert evidence.source == source
    assert evidence.excerpt == "The building opened in 1995."
