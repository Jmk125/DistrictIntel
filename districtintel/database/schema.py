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
    """
    CREATE TABLE IF NOT EXISTS research_jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        school_id INTEGER NOT NULL,
        agent_name TEXT NOT NULL,
        status TEXT NOT NULL,
        started_at TEXT,
        completed_at TEXT,
        error_message TEXT,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS sources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        url TEXT,
        source_type TEXT,
        published_at TEXT,
        accessed_at TEXT,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE (url)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS evidence (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        research_job_id INTEGER,
        source_id INTEGER NOT NULL,
        excerpt TEXT NOT NULL,
        notes TEXT,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (research_job_id) REFERENCES research_jobs(id) ON DELETE CASCADE,
        FOREIGN KEY (source_id) REFERENCES sources(id) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS research_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        research_job_id INTEGER NOT NULL UNIQUE,
        school_id INTEGER NOT NULL,
        agent_name TEXT NOT NULL,
        status TEXT NOT NULL,
        confidence_level TEXT NOT NULL,
        summary TEXT,
        error_message TEXT,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (research_job_id) REFERENCES research_jobs(id) ON DELETE CASCADE,
        FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE
    );
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_research_jobs_school_id
    ON research_jobs (school_id);
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_evidence_research_job_id
    ON evidence (research_job_id);
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_evidence_source_id
    ON evidence (source_id);
    """,
    """
    CREATE TABLE IF NOT EXISTS facts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        school_id INTEGER NOT NULL,
        fact_type TEXT NOT NULL,
        value TEXT NOT NULL,
        value_type TEXT NOT NULL,
        confidence_level TEXT NOT NULL,
        status TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS fact_evidence (
        fact_id INTEGER NOT NULL,
        evidence_id INTEGER NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (fact_id, evidence_id),
        FOREIGN KEY (fact_id) REFERENCES facts(id) ON DELETE CASCADE,
        FOREIGN KEY (evidence_id) REFERENCES evidence(id) ON DELETE CASCADE
    );
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_facts_school_id
    ON facts (school_id);
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_fact_evidence_evidence_id
    ON fact_evidence (evidence_id);
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_research_results_school_id
    ON research_results (school_id);
    """,
)


def apply_schema(connection: sqlite3.Connection) -> None:
    """Apply the foundational DistrictIntel SQLite schema."""

    for statement in SCHEMA_STATEMENTS:
        connection.execute(statement)
