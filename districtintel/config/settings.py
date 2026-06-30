"""Application configuration loading.

Configuration intentionally uses the Python standard library for Milestone 1.
Environment variables provide deploy-time overrides without introducing a
settings dependency before the application needs one.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class AppConfig:
    """Runtime settings for DistrictIntel."""

    database_path: Path
    log_level: str = "INFO"


def load_config() -> AppConfig:
    """Load application configuration from environment variables.

    Supported environment variables:
    - ``DISTRICTINTEL_DB_PATH``: path to the SQLite database file.
    - ``DISTRICTINTEL_LOG_LEVEL``: standard logging level name.
    """

    import os

    database_path = Path(os.getenv("DISTRICTINTEL_DB_PATH", "data/districtintel.sqlite3"))
    log_level = os.getenv("DISTRICTINTEL_LOG_LEVEL", "INFO").upper()
    return AppConfig(database_path=database_path, log_level=log_level)
