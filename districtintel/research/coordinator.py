"""Research job coordination."""

from __future__ import annotations

import logging

from districtintel.models import ConfidenceLevel, Evidence, ResearchResult, ResearchStatus, School
from districtintel.research.interfaces import ResearchAgent, SourceProvider

LOGGER = logging.getLogger(__name__)


class ResearchCoordinator:
    """Coordinates source providers and one research agent for a school."""

    def __init__(self, source_providers: tuple[SourceProvider, ...] = ()) -> None:
        self._source_providers = source_providers

    def run(self, school: School, agent: ResearchAgent) -> ResearchResult:
        """Run a research agent for one school and return its result.

        The coordinator does not perform real research itself. It only gathers
        evidence from injected providers and delegates interpretation to the
        injected agent.
        """

        LOGGER.info("Starting research agent=%s school_id=%s", agent.name, school.id)
        try:
            evidence = self._collect_evidence(school)
            result = agent.research(school=school, evidence=evidence)
        except Exception as exc:
            LOGGER.exception("Research failed agent=%s school_id=%s", agent.name, school.id)
            return ResearchResult(
                school_id=school.id or 0,
                agent_name=agent.name,
                status=ResearchStatus.FAILED,
                confidence=ConfidenceLevel.UNKNOWN,
                error_message=str(exc),
            )

        LOGGER.info(
            "Research completed agent=%s school_id=%s status=%s",
            agent.name,
            school.id,
            result.status,
        )
        return result

    def _collect_evidence(self, school: School) -> tuple[Evidence, ...]:
        collected: list[Evidence] = []
        for provider in self._source_providers:
            LOGGER.info("Collecting evidence provider=%s school_id=%s", provider.name, school.id)
            collected.extend(provider.collect_evidence(school))
        return tuple(collected)
