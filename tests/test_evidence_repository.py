"""Evidence repository tests."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from districtintel.database import initialize_database
from districtintel.models import Evidence, Source, SourceType
from districtintel.repositories import EvidenceRepository


def test_evidence_repository_get_or_create_source_by_url(tmp_path: Path) -> None:
    """Sources with the same URL are reused instead of duplicated."""

    database_path = tmp_path / "districtintel.sqlite3"
    initialize_database(database_path)

    with sqlite3.connect(database_path) as connection:
        repository = EvidenceRepository(connection)
        source = Source(
            title="County Auditor",
            url="https://example.test/auditor",
            source_type=SourceType.COUNTY_AUDITOR,
        )

        created = repository.get_or_create_source_by_url(source)
        reused = repository.get_or_create_source_by_url(
            Source(
                title="Updated title should not duplicate",
                url="https://example.test/auditor",
                source_type=SourceType.OTHER,
            )
        )

    assert created.id == reused.id
    assert reused.title == "County Auditor"
    assert reused.source_type is SourceType.COUNTY_AUDITOR


def test_evidence_repository_creates_and_lists_evidence(tmp_path: Path) -> None:
    """Evidence can be persisted and retrieved by source and research job."""

    database_path = tmp_path / "districtintel.sqlite3"
    initialize_database(database_path)

    with sqlite3.connect(database_path) as connection:
        school_id = _seed_school(connection)
        job_id = connection.execute(
            """
            INSERT INTO research_jobs (school_id, agent_name, status)
            VALUES (?, ?, ?)
            """,
            (school_id, "test-agent", "pending"),
        ).lastrowid
        repository = EvidenceRepository(connection)
        source = repository.create_source(
            Source(
                title="Board Minutes",
                url="https://example.test/minutes",
                source_type=SourceType.BOARD_MINUTES,
            )
        )
        created = repository.create_evidence(
            Evidence(
                source=source,
                excerpt="The board discussed a 1998 renovation.",
                notes="Meeting packet excerpt",
            ),
            research_job_id=job_id,
        )

        by_source = repository.list_by_source(source.id)
        by_job = repository.list_by_research_job(job_id)

    assert created.id is not None
    assert [evidence.id for evidence in by_source] == [created.id]
    assert [evidence.id for evidence in by_job] == [created.id]
    assert by_source[0].source.source_type is SourceType.BOARD_MINUTES


def _seed_school(connection: sqlite3.Connection) -> int:
    district_id = connection.execute(
        "INSERT INTO districts (name) VALUES (?)",
        ("Example District",),
    ).lastrowid
    return connection.execute(
        "INSERT INTO schools (district_id, name) VALUES (?, ?)",
        (district_id, "Example School"),
    ).lastrowid
