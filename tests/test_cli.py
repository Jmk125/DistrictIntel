"""CLI behavior tests."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from districtintel.cli import main
from pytest import CaptureFixture


def test_init_db_creates_foundational_schema(tmp_path: Path) -> None:
    """The init-db command creates a valid SQLite database with core tables."""

    database_path = tmp_path / "districtintel.sqlite3"

    exit_code = main(["--db-path", str(database_path), "init-db"])

    assert exit_code == 0
    assert database_path.exists()
    with sqlite3.connect(database_path) as connection:
        integrity = connection.execute("PRAGMA integrity_check;").fetchone()
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%';"
            )
        }

    assert integrity == ("ok",)
    assert {"districts", "schools"}.issubset(tables)


def test_import_schools_creates_districts_and_skips_duplicates(
    tmp_path: Path,
    capsys: CaptureFixture[str],
) -> None:
    """The import-schools command imports valid rows and skips duplicate schools."""

    database_path = tmp_path / "districtintel.sqlite3"
    csv_path = tmp_path / "schools.csv"
    csv_path.write_text(
        "District Name,School Name,County,School IRN,City\n"
        "Example Local,Example Elementary,Franklin,000001,Columbus\n"
        "Example Local,Example Elementary,Franklin,000001,Columbus\n"
        "Example Local,Example Middle,Franklin,000002,Columbus\n",
        encoding="utf-8",
    )

    exit_code = main(["--db-path", str(database_path), "import-schools", str(csv_path)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Schools created: 2" in captured.out
    assert "Duplicate schools skipped: 1" in captured.out

    with sqlite3.connect(database_path) as connection:
        district_count = connection.execute("SELECT COUNT(*) FROM districts;").fetchone()[0]
        school_count = connection.execute("SELECT COUNT(*) FROM schools;").fetchone()[0]

    assert district_count == 1
    assert school_count == 2
