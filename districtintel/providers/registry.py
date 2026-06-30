"""Provider registration helpers."""

from __future__ import annotations

from dataclasses import dataclass

from districtintel.providers.capabilities import ProviderCapability
from districtintel.providers.interfaces import SourceProvider


@dataclass(frozen=True, slots=True)
class RegisteredProvider:
    """A source provider plus its execution order."""

    provider: SourceProvider
    order: int


class ProviderRegistry:
    """Ordered registry of source providers."""

    def __init__(self) -> None:
        self._providers: list[RegisteredProvider] = []

    def register(self, provider: SourceProvider, *, order: int = 100) -> None:
        """Register a source provider for future execution."""

        if any(registered.provider.name == provider.name for registered in self._providers):
            raise ValueError(f"Provider already registered: {provider.name}")
        self._providers.append(RegisteredProvider(provider=provider, order=order))

    def providers(self) -> tuple[SourceProvider, ...]:
        """Return providers in execution order."""

        return tuple(registered.provider for registered in self._ordered_providers())

    def providers_for(
        self,
        capability: ProviderCapability,
    ) -> tuple[SourceProvider, ...]:
        """Return ordered providers that advertise a capability."""

        return tuple(
            registered.provider
            for registered in self._ordered_providers()
            if capability in registered.provider.capabilities
        )

    def _ordered_providers(self) -> tuple[RegisteredProvider, ...]:
        return tuple(sorted(self._providers, key=lambda registered: registered.order))


def register_provider(
    registry: ProviderRegistry,
    provider: SourceProvider,
    *,
    order: int = 100,
) -> SourceProvider:
    """Register a provider and return it for decorator-style composition."""

    registry.register(provider, order=order)
    return provider
