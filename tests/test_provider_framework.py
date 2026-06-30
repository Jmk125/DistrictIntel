"""Source provider framework tests."""

from __future__ import annotations

from districtintel.models import Evidence, ProviderContext, School, Source
from districtintel.providers import ProviderCoordinator, ProviderRegistry, register_provider


class NamedProvider:
    """Test provider that returns one evidence item."""

    def __init__(self, name: str, excerpt: str) -> None:
        self.name = name
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
