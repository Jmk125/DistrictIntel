"""Source provider framework tests."""

from __future__ import annotations

from districtintel.models import Evidence, ProviderContext, School, Source
from districtintel.providers import (
    ProviderCapability,
    ProviderCoordinator,
    ProviderRegistry,
    register_provider,
)


class NamedProvider:
    """Test provider that returns one evidence item."""

    def __init__(
        self,
        name: str,
        excerpt: str,
        capabilities: tuple[ProviderCapability, ...] = (ProviderCapability.YEAR_BUILT,),
    ) -> None:
        self.name = name
        self.capabilities = capabilities
        self._excerpt = excerpt

    def collect_evidence(
        self,
        school: School,
        context: ProviderContext,
    ) -> tuple[Evidence, ...]:
        return (
            Evidence(
                source=Source(title=f"{self.name} source"),
                excerpt=f"{school.name}: {self._excerpt}",
            ),
        )


class FailingProvider:
    """Test provider that fails deterministically."""

    name = "failing-provider"
    capabilities = (ProviderCapability.YEAR_BUILT,)

    def collect_evidence(
        self,
        school: School,
        context: ProviderContext,
    ) -> tuple[Evidence, ...]:
        raise RuntimeError("provider failure")


def test_provider_registration_and_helper() -> None:
    """Providers can be registered directly or through the helper."""

    registry = ProviderRegistry()
    first = NamedProvider("first", "first evidence")
    second = NamedProvider("second", "second evidence")

    registry.register(second, order=20)
    returned = register_provider(registry, first, order=10)

    assert returned is first
    assert registry.providers() == (first, second)


def test_provider_registration_rejects_duplicate_names() -> None:
    """Duplicate provider names are rejected to keep execution unambiguous."""

    registry = ProviderRegistry()
    registry.register(NamedProvider("duplicate", "one"))

    try:
        registry.register(NamedProvider("duplicate", "two"))
    except ValueError as exc:
        assert str(exc) == "Provider already registered: duplicate"
    else:  # pragma: no cover - defensive assertion path
        raise AssertionError("Expected duplicate provider registration to fail.")


def test_provider_coordinator_executes_and_aggregates_evidence() -> None:
    """The coordinator aggregates evidence from successful providers."""

    school = School(id=1, district_id=1, name="Example School")
    coordinator = ProviderCoordinator(
        providers=(
            NamedProvider("first", "first evidence"),
            NamedProvider("second", "second evidence"),
        )
    )

    results = coordinator.run(school, ProviderContext())
    evidence = coordinator.collect_evidence(school, ProviderContext())

    assert [result.provider_name for result in results] == ["first", "second"]
    assert [item.excerpt for item in evidence] == [
        "Example School: first evidence",
        "Example School: second evidence",
    ]


def test_provider_coordinator_uses_registry_ordering() -> None:
    """Providers execute in registry order."""

    registry = ProviderRegistry()
    third = NamedProvider("third", "third evidence")
    first = NamedProvider("first", "first evidence")
    second = NamedProvider("second", "second evidence")
    registry.register(third, order=30)
    registry.register(first, order=10)
    registry.register(second, order=20)

    coordinator = ProviderCoordinator.from_registry(registry)
    results = coordinator.run(School(id=1, district_id=1, name="Example"))

    assert [result.provider_name for result in results] == ["first", "second", "third"]


def test_provider_failure_is_isolated() -> None:
    """A failing provider does not prevent later providers from running."""

    school = School(id=1, district_id=1, name="Example School")
    coordinator = ProviderCoordinator(
        providers=(
            NamedProvider("before", "before evidence"),
            FailingProvider(),
            NamedProvider("after", "after evidence"),
        )
    )

    results = coordinator.run(school, ProviderContext())
    evidence = coordinator.collect_evidence(school, ProviderContext())

    assert [result.provider_name for result in results] == [
        "before",
        "failing-provider",
        "after",
    ]
    assert results[1].succeeded is False
    assert results[1].error_message == "provider failure"
    assert [item.excerpt for item in evidence] == [
        "Example School: before evidence",
        "Example School: after evidence",
    ]


def test_registry_filters_providers_by_capability() -> None:
    """Registry lookup returns only providers advertising the requested capability."""

    registry = ProviderRegistry()
    year_built = NamedProvider(
        "year-built",
        "year built evidence",
        capabilities=(ProviderCapability.YEAR_BUILT,),
    )
    news = NamedProvider(
        "news",
        "news evidence",
        capabilities=(ProviderCapability.NEWS,),
    )
    both = NamedProvider(
        "both",
        "combined evidence",
        capabilities=(ProviderCapability.YEAR_BUILT, ProviderCapability.NEWS),
    )
    registry.register(news, order=30)
    registry.register(both, order=20)
    registry.register(year_built, order=10)

    assert registry.providers_for(ProviderCapability.YEAR_BUILT) == (year_built, both)
    assert registry.providers_for(ProviderCapability.NEWS) == (both, news)


def test_coordinator_collects_evidence_for_matching_capability_only() -> None:
    """Capability-scoped collection only executes matching providers."""

    school = School(id=1, district_id=1, name="Example School")
    coordinator = ProviderCoordinator(
        providers=(
            NamedProvider(
                "year-built",
                "year built evidence",
                capabilities=(ProviderCapability.YEAR_BUILT,),
            ),
            NamedProvider(
                "news",
                "news evidence",
                capabilities=(ProviderCapability.NEWS,),
            ),
        )
    )

    evidence = coordinator.collect_evidence_for(
        school,
        ProviderCapability.NEWS,
        ProviderContext(),
    )

    assert [item.excerpt for item in evidence] == ["Example School: news evidence"]


def test_capability_filtered_failure_is_isolated() -> None:
    """A failing matching provider does not block later matching providers."""

    school = School(id=1, district_id=1, name="Example School")
    coordinator = ProviderCoordinator(
        providers=(
            NamedProvider(
                "non-matching",
                "non-matching evidence",
                capabilities=(ProviderCapability.NEWS,),
            ),
            FailingProvider(),
            NamedProvider(
                "matching",
                "matching evidence",
                capabilities=(ProviderCapability.YEAR_BUILT,),
            ),
        )
    )

    evidence = coordinator.collect_evidence_for(
        school,
        ProviderCapability.YEAR_BUILT,
        ProviderContext(),
    )

    assert [item.excerpt for item in evidence] == ["Example School: matching evidence"]


def test_placeholder_providers_advertise_expected_capabilities() -> None:
    """Placeholder providers advertise initial capability mappings only."""

    from districtintel.providers import (  # noqa: PLC0415
        BoardMinutesProvider,
        CountyAuditorProvider,
        DistrictWebsiteProvider,
        LocalNewsProvider,
        OfccProvider,
    )

    assert CountyAuditorProvider.capabilities == (
        ProviderCapability.YEAR_BUILT,
        ProviderCapability.SQUARE_FOOTAGE,
    )
    assert DistrictWebsiteProvider.capabilities == (
        ProviderCapability.CONTACT_INFORMATION,
        ProviderCapability.ARCHITECT,
    )
    assert BoardMinutesProvider.capabilities == (
        ProviderCapability.BOARD_DISCUSSIONS,
        ProviderCapability.BOND_HISTORY,
        ProviderCapability.LEVY_HISTORY,
    )
    assert LocalNewsProvider.capabilities == (ProviderCapability.NEWS,)
    assert OfccProvider.capabilities == (ProviderCapability.OFCC_INFORMATION,)
