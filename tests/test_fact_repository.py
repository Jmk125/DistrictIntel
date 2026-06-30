"""Fact repository tests."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from districtintel.database import initialize_database
from districtintel.models import ConfidenceLevel, Evidence, Fact, FactType, FactValueType, Source
from districtintel.repositories import FactRepository


def test_fact_repository_creates_links_and_lists_facts(tmp_path: Path) -> None:
    """Facts can be created, linked to evidence, and retrieved by school."""

    database_path = tmp_path / "districtintel.sqlite3"
    initialize_database(database_path)

    with sqlite3.connect(database_path) as connection:
        school_id = _seed_school(connection)
        source_id = connection.execute(
            "INSERT INTO sources (title, url) VALUES (?, ?)",
            ("Auditor", "https://example.test/auditor"),
        ).lastrowid
        evidence_id = connection.execute(
            "INSERT INTO evidence (source_id, excerpt) VALUES (?, ?)",
            (source_id, "Built in 1965."),
        ).lastrowid

        repository = FactRepository(connection)
        evidence = Evidence(
            id=evidence_id,
            source=Source(id=source_id, title="Auditor"),
            excerpt="Built in 1965.",
        )
        created = repository.create(
            Fact(
                school_id=school_id,
                fact_type=FactType.YEAR_BUILT,
                value=1965,
                value_type=FactValueType.INTEGER,
                confidence=ConfidenceLevel.HIGH,
                evidence=(evidence,),
            )
        )

        facts = repository.list_for_school(school_id)
        links = connection.execute(
            "SELECT fact_id, evidence_id FROM fact_evidence"
        ).fetchall()

    assert len(facts) == 1
    assert facts[0].id == created.id
    assert facts[0].value == 1965
    assert links == [(created.id, evidence_id)]


def _seed_school(connection: sqlite3.Connection) -> int:
    district_id = connection.execute(
        "INSERT INTO districts (name) VALUES (?)",
        ("Example District",),
    ).lastrowid
    return connection.execute(
        "INSERT INTO schools (district_id, name) VALUES (?, ?)",
        (district_id, "Example School"),
    ).lastrowid
