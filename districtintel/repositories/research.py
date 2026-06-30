"""Research repository helpers."""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime

from districtintel.models import ResearchJob, ResearchResult, ResearchStatus


class ResearchJobRepository:
    """Persist research job lifecycle state."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def create(self, school_id: int, agent_name: str) -> ResearchJob:
        """Create a pending research job."""

        cursor = self._connection.execute(
            """
            INSERT INTO research_jobs (school_id, agent_name, status)
            VALUES (?, ?, ?)
            """,
            (school_id, agent_name, ResearchStatus.PENDING.value),
        )
        return ResearchJob(
            id=cursor.lastrowid,
            school_id=school_id,
            agent_name=agent_name,
            status=ResearchStatus.PENDING,
        )

    def mark_running(self, job_id: int) -> None:
        """Mark a research job as running."""

        now = _utc_now_iso()
        self._connection.execute(
            """
            UPDATE research_jobs
            SET status = ?, started_at = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (ResearchStatus.RUNNING.value, now, job_id),
        )

    def mark_completed(self, job_id: int) -> None:
        """Mark a research job as completed."""

        now = _utc_now_iso()
        self._connection.execute(
            """
            UPDATE research_jobs
            SET status = ?, completed_at = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (ResearchStatus.COMPLETED.value, now, job_id),
        )

    def mark_failed(self, job_id: int, error_message: str) -> None:
        """Mark a research job as failed."""

        now = _utc_now_iso()
        self._connection.execute(
            """
            UPDATE research_jobs
            SET status = ?, completed_at = ?, error_message = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (ResearchStatus.FAILED.value, now, error_message, job_id),
        )


class ResearchResultRepository:
    """Persist final research results."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def create(self, result: ResearchResult) -> ResearchResult:
        """Create a research result row."""

        if result.job_id is None:
            raise ValueError("A research result must have a job_id before persistence.")

        cursor = self._connection.execute(
            """
            INSERT INTO research_results (
                research_job_id, school_id, agent_name, status,
                confidence_level, summary, error_message
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                result.job_id,
                result.school_id,
                result.agent_name,
                result.status.value,
                result.confidence.value,
                result.summary,
                result.error_message,
            ),
        )
        return ResearchResult(
            id=cursor.lastrowid,
            job_id=result.job_id,
            school_id=result.school_id,
            agent_name=result.agent_name,
            status=result.status,
            confidence=result.confidence,
            summary=result.summary,
            evidence=result.evidence,
            error_message=result.error_message,
        )


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()
