"""Command-line interface for DistrictIntel."""

from __future__ import annotations

import argparse
import logging
from collections.abc import Sequence
from pathlib import Path

from districtintel.config import load_config
from districtintel.database import connect, initialize_database
from districtintel.services import ImportSummary, import_schools_from_csv
from districtintel.utils.logging import configure_logging

LOGGER = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Build the DistrictIntel command parser."""

    parser = argparse.ArgumentParser(
        prog="districtintel",
        description="DistrictIntel facility intelligence research platform.",
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=None,
        help="Path to the SQLite database file. Overrides DISTRICTINTEL_DB_PATH.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("init-db", help="Create or update the SQLite database schema.")

    import_parser = subparsers.add_parser(
        "import-schools",
        help="Import districts and schools from an Ohio school CSV file.",
    )
    import_parser.add_argument("csv_file", type=Path, help="Path to the Ohio school CSV file.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the DistrictIntel CLI."""

    parser = build_parser()
    args = parser.parse_args(argv)

    config = load_config()
    configure_logging(config.log_level)

    database_path = args.db_path or config.database_path

    if args.command == "init-db":
        initialized_path = initialize_database(database_path)
        LOGGER.info("Database ready: %s", initialized_path)
        return 0

    if args.command == "import-schools":
        initialized_path = initialize_database(database_path)
        with connect(initialized_path) as connection:
            summary = import_schools_from_csv(args.csv_file, connection)
        _print_import_summary(summary)
        return 1 if summary.invalid_rows else 0

    parser.error(f"Unknown command: {args.command}")
    return 2


def _print_import_summary(summary: ImportSummary) -> None:
    """Print a human-readable import summary."""

    print("School import summary")
    print(f"Rows read: {summary.rows_read}")
    print(f"Districts created: {summary.districts_created}")
    print(f"Schools created: {summary.schools_created}")
    print(f"Duplicate schools skipped: {summary.duplicate_schools}")
    print(f"Invalid rows: {summary.invalid_rows}")

    if summary.errors:
        print("Errors:")
        for error in summary.errors[:10]:
            print(f"  Row {error.row_number}: {error.message}")
        if len(summary.errors) > 10:
            print(f"  ... {len(summary.errors) - 10} additional errors")
