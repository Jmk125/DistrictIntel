"""Fact repository."""

from __future__ import annotations

import sqlite3

from districtintel.models import ConfidenceLevel, Fact, FactStatus, FactType, FactValueType
from districtintel.models.fact import coerce_fact_value, serialize_fact_value


class FactRepository:
    """Persist and retrieve structured facts for schools."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def create(self, fact: Fact) -> Fact:
        """Create a structured fact row.

        At least one persisted Evidence object is required so facts are never
        stored without traceability. Additional evidence can be linked later with
        ``link_evidence``.
        """

        _validate_fact(fact)
        cursor = self._connection.execute(
            """
            INSERT INTO facts (
                school_id, fact_type, value, value_type, confidence_level, status
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                fact.school_id,
                fact.fact_type.value,
                serialize_fact_value(fact.value, fact.value_type),
                fact.value_type.value,
                fact.confidence.value,
                fact.status.value,
            ),
        )
        created = Fact(
            id=cursor.lastrowid,
            school_id=fact.school_id,
            fact_type=fact.fact_type,
            value=fact.value,
            value_type=fact.value_type,
            confidence=fact.confidence,
            status=fact.status,
            evidence=fact.evidence,
        )
        for evidence in fact.evidence:
            if evidence.id is None:
                raise ValueError("Fact evidence must have an id before linking.")
            self.link_evidence(created.id, evidence.id)
        return created

    def link_evidence(self, fact_id: int | None, evidence_id: int) -> None:
        """Link a fact to an evidence row."""

        if fact_id is None:
            raise ValueError("fact_id is required to link evidence.")
        self._connection.execute(
            """
            INSERT OR IGNORE INTO fact_evidence (fact_id, evidence_id)
            VALUES (?, ?)
            """,
            (fact_id, evidence_id),
        )

    def list_for_school(self, school_id: int) -> list[Fact]:
        """Return structured facts for a school.

        This method returns fact records and keeps evidence traceability queryable
        through ``fact_evidence``. Loading full Evidence objects belongs in a future
        evidence repository once evidence persistence grows beyond schema prep.
        """

        rows = self._connection.execute(
            """
            SELECT id, school_id, fact_type, value, value_type, confidence_level, status
            FROM facts
            WHERE school_id = ?
            ORDER BY fact_type, id
            """,
            (school_id,),
        ).fetchall()
        return [_fact_from_row(row) for row in rows]


def _validate_fact(fact: Fact) -> None:
    if fact.school_id <= 0:
        raise ValueError("Fact must be tied to a persisted school.")
    if not fact.evidence:
        raise ValueError("Fact must include at least one evidence relationship.")
    if any(evidence.id is None for evidence in fact.evidence):
        raise ValueError("Fact evidence must have an id before persistence.")


def _fact_from_row(row: sqlite3.Row | tuple[object, ...]) -> Fact:
    fact_id, school_id, fact_type, value, value_type, confidence, status = row
    parsed_value_type = FactValueType(str(value_type))
    return Fact(
        id=int(fact_id),
        school_id=int(school_id),
        fact_type=FactType(str(fact_type)),
        value=coerce_fact_value(str(value), parsed_value_type),
        value_type=parsed_value_type,
        confidence=ConfidenceLevel(str(confidence)),
        status=FactStatus(str(status)),
    )
