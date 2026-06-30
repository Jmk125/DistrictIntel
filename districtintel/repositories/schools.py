"""School repository."""

from __future__ import annotations

import sqlite3

from districtintel.models import School


class SchoolRepository:
    """Persist and retrieve schools."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def exists(self, school: School) -> bool:
        """Return whether a school already exists."""

        if school.external_id:
            row = self._connection.execute(
                "SELECT 1 FROM schools WHERE external_id = ?",
                (school.external_id,),
            ).fetchone()
            if row is not None:
                return True

        row = self._connection.execute(
            """
            SELECT 1
            FROM schools
            WHERE district_id = ? AND name = ?
            """,
            (school.district_id, school.name),
        ).fetchone()
        return row is not None

    def create(self, school: School) -> School:
        """Create a school record."""

        cursor = self._connection.execute(
            """
            INSERT INTO schools (
                district_id, name, external_id, address, city, state,
                zip_code, low_grade, high_grade
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                school.district_id,
                school.name,
                school.external_id,
                school.address,
                school.city,
                school.state,
                school.zip_code,
                school.low_grade,
                school.high_grade,
            ),
        )
        return School(
            id=cursor.lastrowid,
            district_id=school.district_id,
            name=school.name,
            external_id=school.external_id,
            address=school.address,
            city=school.city,
            state=school.state,
            zip_code=school.zip_code,
            low_grade=school.low_grade,
            high_grade=school.high_grade,
        )
