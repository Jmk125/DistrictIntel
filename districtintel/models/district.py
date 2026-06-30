"""District domain model."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class District:
    """A K-12 school district."""

    name: str
    county: str | None = None
    state: str = "OH"
    external_id: str | None = None
    id: int | None = None
