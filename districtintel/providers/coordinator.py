"""Provider execution coordination."""

from __future__ import annotations

import logging

from districtintel.models import Evidence, ProviderContext, ProviderResult, School
from districtintel.providers.capabilities import ProviderCapability
from districtintel.providers.interfaces import SourceProvider
from districtintel.providers.registry import ProviderRegistry

LOGGER = logging.getLogger(__name__)


class ProviderCoordinator:
    """Run source providers and aggregate their evidence."""

    def __init__(self, providers: tuple[SourceProvider, ...] = ()) -> None:
        self._providers = providers

    @classmethod
    def from_registry(cls, registry: ProviderRegistry) -> ProviderCoordinator:
        """Create a coordinator using providers from a registry."""

        return cls(providers=registry.providers())

    def run(
        self,
        school: School,
        context: ProviderContext | None = None,
    ) -> tuple[ProviderResult, ...]:
        """Run every provider, isolating provider failures."""

        provider_context = context or ProviderContext()
        results: list[ProviderResult] = []
        for provider in self._providers:
            LOGGER.info("Running source provider=%s school_id=%s", provider.name, school.id)
            try:
                evidence = provider.collect_evidence(school, provider_context)
            except Exception as exc:
                LOGGER.exception(
                    "Source provider failed provider=%s school_id=%s",
                    provider.name,
                    school.id,
                )
                results.append(
                    ProviderResult(provider_name=provider.name, error_message=str(exc))
                )
                continue
            results.append(
                ProviderResult(provider_name=provider.name, evidence=tuple(evidence))
            )
        return tuple(results)

    def collect_evidence(
        self,
        school: School,
        context: ProviderContext | None = None,
    ) -> tuple[Evidence, ...]:
        """Run providers and return the aggregate successful evidence."""

        return self._collect_successful_evidence(self.run(school=school, context=context))

    def collect_evidence_for(
        self,
        school: School,
        capability: ProviderCapability,
        context: ProviderContext | None = None,
    ) -> tuple[Evidence, ...]:
        """Run providers advertising a capability and aggregate evidence."""

        matching_providers = tuple(
            provider for provider in self._providers if capability in provider.capabilities
        )
        results = ProviderCoordinator(providers=matching_providers).run(
            school=school,
            context=context,
        )
        return self._collect_successful_evidence(results)

    def _collect_successful_evidence(
        self,
        results: tuple[ProviderResult, ...],
    ) -> tuple[Evidence, ...]:
        evidence: list[Evidence] = []
        for result in results:
            evidence.extend(result.evidence)
        return tuple(evidence)
