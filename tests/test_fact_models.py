"""Fact model tests."""

from __future__ import annotations

from districtintel.models import ConfidenceLevel, Fact, FactType, FactValueType
from districtintel.models.fact import coerce_fact_value, serialize_fact_value


def test_fact_supports_structured_integer_values() -> None:
    """Facts store structured values instead of free-text only values."""

    fact = Fact(
        school_id=1,
        fact_type=FactType.YEAR_BUILT,
        value=1965,
        value_type=FactValueType.INTEGER,
        confidence=ConfidenceLevel.HIGH,
    )

    assert fact.value == 1965
    assert fact.value_type is FactValueType.INTEGER
    assert fact.evidence == ()


def test_fact_value_serialization_round_trips_boolean() -> None:
    """Typed fact values can be serialized for SQLite and restored."""

    stored = serialize_fact_value(True, FactValueType.BOOLEAN)

    assert stored == "true"
    assert coerce_fact_value(stored, FactValueType.BOOLEAN) is True
