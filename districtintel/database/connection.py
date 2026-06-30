"""SQLite connection helpers."""

from __future__ import annotations

import sqlite3
from pathlib import Path


def connect(database_path: Path) -> sqlite3.Connection:
    """Open a SQLite connection with application defaults enabled."""

    connection = sqlite3.connect(database_path.expanduser())
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON;")
    return connection
