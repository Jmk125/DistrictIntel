"""SQLite initialization layer."""

from __future__ import annotations

import logging
from pathlib import Path

from districtintel.database.connection import connect
from districtintel.database.schema import apply_schema

LOGGER = logging.getLogger(__name__)


def initialize_database(database_path: Path) -> Path:
    """Create or update the SQLite database with the foundational schema."""

    resolved_path = database_path.expanduser()
    resolved_path.parent.mkdir(parents=True, exist_ok=True)

    LOGGER.info("Initializing SQLite database at %s", resolved_path)
    with connect(resolved_path) as connection:
        connection.execute("PRAGMA journal_mode = WAL;")
        apply_schema(connection)
        connection.commit()

    LOGGER.info("SQLite database initialized at %s", resolved_path)
    return resolved_path
