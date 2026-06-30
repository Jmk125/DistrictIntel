"""Provider registration helpers."""

from __future__ import annotations

from dataclasses import dataclass

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

        ordered = sorted(self._providers, key=lambda registered: registered.order)
        return tuple(registered.provider for registered in ordered)


def register_provider(
    registry: ProviderRegistry,
    provider: SourceProvider,
    *,
    order: int = 100,
) -> SourceProvider:
    """Register a provider and return it for decorator-style composition."""

    registry.register(provider, order=order)
    return provider
