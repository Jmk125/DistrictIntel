"""SQLite initialization layer."""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path

LOGGER = logging.getLogger(__name__)


def initialize_database(database_path: Path) -> Path:
    """Create an empty SQLite database file if it does not already exist.

    The function deliberately does not create application tables in Milestone 1.
    It only validates that SQLite can open the configured path and applies safe
    connection-level pragmas for future use.
    """

    resolved_path = database_path.expanduser()
    resolved_path.parent.mkdir(parents=True, exist_ok=True)

    LOGGER.info("Initializing SQLite database at %s", resolved_path)
    with sqlite3.connect(resolved_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON;")
        connection.execute("PRAGMA journal_mode = WAL;")
        connection.commit()

    LOGGER.info("SQLite database initialized at %s", resolved_path)
    return resolved_path
