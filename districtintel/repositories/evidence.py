"""Evidence and source repository."""

from __future__ import annotations

import sqlite3
from datetime import datetime

from districtintel.models import Evidence, Source, SourceType


class EvidenceRepository:
    """Persist and retrieve sources and evidence."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def create_source(self, source: Source) -> Source:
        """Create a source row."""

        cursor = self._connection.execute(
            """
            INSERT INTO sources (title, url, source_type, published_at, accessed_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                source.title,
                source.url,
                source.source_type.value,
                _datetime_to_text(source.published_at),
                _datetime_to_text(source.accessed_at),
            ),
        )
        return Source(
            id=cursor.lastrowid,
            title=source.title,
            url=source.url,
            source_type=source.source_type,
            published_at=source.published_at,
            accessed_at=source.accessed_at,
        )

    def get_source_by_url(self, url: str) -> Source | None:
        """Return a source by URL if it exists."""

        row = self._connection.execute(
            """
            SELECT id, title, url, source_type, published_at, accessed_at
            FROM sources
            WHERE url = ?
            """,
            (url,),
        ).fetchone()
        if row is None:
            return None
        return _source_from_row(row)

    def get_or_create_source_by_url(self, source: Source) -> Source:
        """Return an existing URL-matched source or create it."""

        if source.url is None:
            return self.create_source(source)

        existing = self.get_source_by_url(source.url)
        if existing is not None:
            return existing
        return self.create_source(source)

    def create_evidence(
        self,
        evidence: Evidence,
        *,
        research_job_id: int | None = None,
    ) -> Evidence:
        """Create an evidence row for a persisted source."""

        if evidence.source.id is None:
            raise ValueError("Evidence source must have an id before persistence.")

        cursor = self._connection.execute(
            """
            INSERT INTO evidence (research_job_id, source_id, excerpt, notes)
            VALUES (?, ?, ?, ?)
            """,
            (research_job_id, evidence.source.id, evidence.excerpt, evidence.notes),
        )
        return Evidence(
            id=cursor.lastrowid,
            source=evidence.source,
            excerpt=evidence.excerpt,
            notes=evidence.notes,
        )

    def list_by_source(self, source_id: int) -> list[Evidence]:
        """Return evidence rows for a source."""

        rows = self._connection.execute(
            """
            SELECT
                evidence.id,
                evidence.excerpt,
                evidence.notes,
                sources.id,
                sources.title,
                sources.url,
                sources.source_type,
                sources.published_at,
                sources.accessed_at
            FROM evidence
            JOIN sources ON sources.id = evidence.source_id
            WHERE evidence.source_id = ?
            ORDER BY evidence.id
            """,
            (source_id,),
        ).fetchall()
        return [_evidence_from_row(row) for row in rows]

    def list_by_research_job(self, research_job_id: int) -> list[Evidence]:
        """Return evidence rows associated with a research job."""

        rows = self._connection.execute(
            """
            SELECT
                evidence.id,
                evidence.excerpt,
                evidence.notes,
                sources.id,
                sources.title,
                sources.url,
                sources.source_type,
                sources.published_at,
                sources.accessed_at
            FROM evidence
            JOIN sources ON sources.id = evidence.source_id
            WHERE evidence.research_job_id = ?
            ORDER BY evidence.id
            """,
            (research_job_id,),
        ).fetchall()
        return [_evidence_from_row(row) for row in rows]


def _source_from_row(row: sqlite3.Row | tuple[object, ...]) -> Source:
    source_id, title, url, source_type, published_at, accessed_at = row
    return Source(
        id=int(source_id),
        title=str(title),
        url=str(url) if url is not None else None,
        source_type=_source_type_from_text(source_type),
        published_at=_datetime_from_text(published_at),
        accessed_at=_datetime_from_text(accessed_at),
    )


def _evidence_from_row(row: sqlite3.Row | tuple[object, ...]) -> Evidence:
    (
        evidence_id,
        excerpt,
        notes,
        source_id,
        title,
        url,
        source_type,
        published_at,
        accessed_at,
    ) = row
    return Evidence(
        id=int(evidence_id),
        source=Source(
            id=int(source_id),
            title=str(title),
            url=str(url) if url is not None else None,
            source_type=_source_type_from_text(source_type),
            published_at=_datetime_from_text(published_at),
            accessed_at=_datetime_from_text(accessed_at),
        ),
        excerpt=str(excerpt),
        notes=str(notes) if notes is not None else None,
    )


def _source_type_from_text(value: object) -> SourceType:
    if value is None:
        return SourceType.OTHER
    try:
        return SourceType(str(value))
    except ValueError:
        return SourceType.OTHER


def _datetime_to_text(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.isoformat()


def _datetime_from_text(value: object) -> datetime | None:
    if value is None:
        return None
    return datetime.fromisoformat(str(value))
