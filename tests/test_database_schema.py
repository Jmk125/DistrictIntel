"""Database schema tests."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from districtintel.database import initialize_database


def test_research_schema_tables_are_created(tmp_path: Path) -> None:
    """Database initialization creates research framework tables."""

    database_path = tmp_path / "districtintel.sqlite3"
    initialize_database(database_path)

    with sqlite3.connect(database_path) as connection:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%';"
            )
        }

    assert {
        "research_jobs",
        "sources",
        "evidence",
        "research_results",
        "facts",
        "fact_evidence",
    }.issubset(tables)
