"""Command-line interface for DistrictIntel."""

from __future__ import annotations

import argparse
import logging
from collections.abc import Sequence
from pathlib import Path

from districtintel.config import load_config
from districtintel.database import initialize_database
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
    subparsers.add_parser("init-db", help="Create an empty SQLite database file.")
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

    parser.error(f"Unknown command: {args.command}")
    return 2
