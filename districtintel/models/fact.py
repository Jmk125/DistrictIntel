"""Structured fact domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from districtintel.models.research import ConfidenceLevel, Evidence

FactValue = str | int | float | bool


class FactType(StrEnum):
    """Queryable intelligence fact categories."""

    YEAR_BUILT = "year_built"
    RENOVATION_YEAR = "renovation_year"
    BOND_ISSUE = "bond_issue"
    ARCHITECT = "architect"
    FACILITY_CONDITION = "facility_condition"
    AVERAGE_BUILDING_AGE = "average_building_age"


class FactValueType(StrEnum):
    """Storage type for a structured fact value."""

    TEXT = "text"
    INTEGER = "integer"
    NUMBER = "number"
    BOOLEAN = "boolean"
    DATE = "date"


class FactStatus(StrEnum):
    """Validation lifecycle for a fact."""

    PROPOSED = "proposed"
    VALIDATED = "validated"
    CONFLICTING = "conflicting"
    REJECTED = "rejected"


@dataclass(frozen=True, slots=True)
class Fact:
    """A structured, evidence-backed claim about a school."""

    school_id: int
    fact_type: FactType
    value: FactValue
    value_type: FactValueType
    confidence: ConfidenceLevel
    evidence: tuple[Evidence, ...] = field(default_factory=tuple)
    status: FactStatus = FactStatus.PROPOSED
    id: int | None = None


def serialize_fact_value(value: FactValue, value_type: FactValueType) -> str:
    """Serialize a structured fact value for SQLite storage."""

    if value_type is FactValueType.BOOLEAN:
        return "true" if bool(value) else "false"
    return str(value)


def coerce_fact_value(value: str, value_type: FactValueType) -> FactValue:
    """Coerce a stored SQLite value back to its declared structured type."""

    if value_type is FactValueType.INTEGER:
        return int(value)
    if value_type is FactValueType.NUMBER:
        return float(value)
    if value_type is FactValueType.BOOLEAN:
        return value.lower() == "true"
    return value
