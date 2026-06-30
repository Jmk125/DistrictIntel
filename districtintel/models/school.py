"""School domain model."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class School:
    """A school belonging to a district."""

    district_id: int
    name: str
    external_id: str | None = None
    address: str | None = None
    city: str | None = None
    state: str = "OH"
    zip_code: str | None = None
    low_grade: str | None = None
    high_grade: str | None = None
    id: int | None = None
