"""SQLite schema management for DistrictIntel."""

from __future__ import annotations

import sqlite3

SCHEMA_STATEMENTS = (
    """
    CREATE TABLE IF NOT EXISTS districts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        county TEXT,
        state TEXT NOT NULL DEFAULT 'OH',
        external_id TEXT UNIQUE,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS schools (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        district_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        external_id TEXT UNIQUE,
        address TEXT,
        city TEXT,
        state TEXT NOT NULL DEFAULT 'OH',
        zip_code TEXT,
        low_grade TEXT,
        high_grade TEXT,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (district_id) REFERENCES districts(id) ON DELETE CASCADE,
        UNIQUE (district_id, name)
    );
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_schools_district_id
    ON schools (district_id);
    """,
)


def apply_schema(connection: sqlite3.Connection) -> None:
    """Apply the foundational DistrictIntel SQLite schema."""

    for statement in SCHEMA_STATEMENTS:
        connection.execute(statement)
