"""CLI behavior tests."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from districtintel.cli import main


def test_init_db_creates_sqlite_database(tmp_path: Path) -> None:
    """The init-db command creates a valid SQLite database file."""

    database_path = tmp_path / "districtintel.sqlite3"

    exit_code = main(["--db-path", str(database_path), "init-db"])

    assert exit_code == 0
    assert database_path.exists()
    with sqlite3.connect(database_path) as connection:
        result = connection.execute("PRAGMA integrity_check;").fetchone()

    assert result == ("ok",)
