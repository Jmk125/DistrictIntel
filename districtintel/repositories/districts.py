"""District repository."""

from __future__ import annotations

import sqlite3

from districtintel.models import District


class DistrictRepository:
    """Persist and retrieve districts."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def get_by_name(self, name: str) -> District | None:
        """Return a district by its normalized unique name."""

        row = self._connection.execute(
            """
            SELECT id, name, county, state, external_id
            FROM districts
            WHERE name = ?
            """,
            (name,),
        ).fetchone()
        return self._to_model(row) if row else None

    def get_or_create(self, district: District) -> tuple[District, bool]:
        """Get an existing district by name or create it.

        Returns the district and a boolean indicating whether it was created.
        """

        existing = self.get_by_name(district.name)
        if existing is not None:
            return existing, False

        cursor = self._connection.execute(
            """
            INSERT INTO districts (name, county, state, external_id)
            VALUES (?, ?, ?, ?)
            """,
            (district.name, district.county, district.state, district.external_id),
        )
        created = District(
            id=cursor.lastrowid,
            name=district.name,
            county=district.county,
            state=district.state,
            external_id=district.external_id,
        )
        return created, True

    @staticmethod
    def _to_model(row: sqlite3.Row) -> District:
        return District(
            id=row["id"],
            name=row["name"],
            county=row["county"],
            state=row["state"],
            external_id=row["external_id"],
        )
