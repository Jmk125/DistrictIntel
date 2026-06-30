"""CSV import pipeline for Ohio schools."""

from __future__ import annotations

import csv
import logging
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar

from districtintel.models import District, School
from districtintel.repositories import DistrictRepository, SchoolRepository

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class ImportErrorDetail:
    """Validation error for one CSV row."""

    row_number: int
    message: str


@dataclass(slots=True)
class ImportSummary:
    """Summary of a school CSV import run."""

    rows_read: int = 0
    districts_created: int = 0
    schools_created: int = 0
    duplicate_schools: int = 0
    invalid_rows: int = 0
    errors: list[ImportErrorDetail] = field(default_factory=list)

    @property
    def success_count(self) -> int:
        """Return rows that were either created or identified as duplicates."""

        return self.schools_created + self.duplicate_schools


class SchoolCsvImporter:
    """Import districts and schools from a CSV file."""

    FIELD_ALIASES: ClassVar[dict[str, tuple[str, ...]]] = {
        "district_name": ("district_name", "district", "district name", "lea name"),
        "school_name": ("school_name", "school", "school name", "building name"),
        "district_external_id": ("district_id", "district irn", "lea irn"),
        "school_external_id": ("school_id", "school irn", "building irn", "irn"),
        "county": ("county", "county name"),
        "address": ("address", "street address", "mailing address"),
        "city": ("city", "mailing city"),
        "state": ("state", "mailing state"),
        "zip_code": ("zip", "zip_code", "zipcode", "postal code"),
        "low_grade": ("low_grade", "lowest grade", "grade low"),
        "high_grade": ("high_grade", "highest grade", "grade high"),
    }

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._districts = DistrictRepository(connection)
        self._schools = SchoolRepository(connection)
        self._connection = connection

    def import_file(self, csv_path: Path) -> ImportSummary:
        """Import a CSV file and return a useful summary."""

        summary = ImportSummary()
        with csv_path.open(newline="", encoding="utf-8-sig") as csv_file:
            reader = csv.DictReader(csv_file)
            if reader.fieldnames is None:
                summary.errors.append(
                    ImportErrorDetail(row_number=0, message="CSV has no header row.")
                )
                summary.invalid_rows += 1
                return summary

            header_map = self._build_header_map(reader.fieldnames)
            missing_fields = self._missing_required_fields(header_map)
            if missing_fields:
                summary.errors.append(
                    ImportErrorDetail(
                        row_number=0,
                        message=f"CSV is missing required fields: {', '.join(missing_fields)}.",
                    )
                )
                summary.invalid_rows += 1
                return summary

            for row_number, row in enumerate(reader, start=2):
                summary.rows_read += 1
                self._import_row(
                    row=row,
                    row_number=row_number,
                    header_map=header_map,
                    summary=summary,
                )

        self._connection.commit()
        LOGGER.info(
            "School import complete: rows=%s districts_created=%s schools_created=%s "
            "duplicates=%s invalid=%s",
            summary.rows_read,
            summary.districts_created,
            summary.schools_created,
            summary.duplicate_schools,
            summary.invalid_rows,
        )
        return summary

    def _import_row(
        self,
        row: dict[str, str],
        row_number: int,
        header_map: dict[str, str],
        summary: ImportSummary,
    ) -> None:
        values = {field: self._clean(row.get(column)) for field, column in header_map.items()}
        district_name = values.get("district_name")
        school_name = values.get("school_name")

        if not district_name or not school_name:
            summary.invalid_rows += 1
            summary.errors.append(
                ImportErrorDetail(
                    row_number=row_number,
                    message="District name and school name are required.",
                )
            )
            return

        district, district_created = self._districts.get_or_create(
            District(
                name=district_name,
                county=values.get("county"),
                state=values.get("state") or "OH",
                external_id=values.get("district_external_id"),
            )
        )
        if district_created:
            summary.districts_created += 1

        if district.id is None:
            raise ValueError("District repository returned a district without an id.")

        school = School(
            district_id=district.id,
            name=school_name,
            external_id=values.get("school_external_id"),
            address=values.get("address"),
            city=values.get("city"),
            state=values.get("state") or "OH",
            zip_code=values.get("zip_code"),
            low_grade=values.get("low_grade"),
            high_grade=values.get("high_grade"),
        )
        if self._schools.exists(school):
            summary.duplicate_schools += 1
            return

        self._schools.create(school)
        summary.schools_created += 1

    @classmethod
    def _build_header_map(cls, fieldnames: list[str]) -> dict[str, str]:
        normalized_headers = {cls._normalize_header(header): header for header in fieldnames}
        header_map: dict[str, str] = {}
        for canonical_field, aliases in cls.FIELD_ALIASES.items():
            for alias in aliases:
                if alias in normalized_headers:
                    header_map[canonical_field] = normalized_headers[alias]
                    break
        return header_map

    @staticmethod
    def _missing_required_fields(header_map: dict[str, str]) -> list[str]:
        return [field for field in ("district_name", "school_name") if field not in header_map]

    @staticmethod
    def _normalize_header(header: str) -> str:
        return " ".join(header.strip().lower().replace("_", " ").split())

    @staticmethod
    def _clean(value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = " ".join(value.strip().split())
        return cleaned or None


def import_schools_from_csv(csv_path: Path, connection: sqlite3.Connection) -> ImportSummary:
    """Import schools from a CSV file using the application importer."""

    return SchoolCsvImporter(connection).import_file(csv_path)
