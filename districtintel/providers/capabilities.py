"""Provider capability vocabulary."""

from __future__ import annotations

from enum import StrEnum


class ProviderCapability(StrEnum):
    """Types of information a source provider can collect."""

    YEAR_BUILT = "year_built"
    RENOVATION_HISTORY = "renovation_history"
    ADDITIONS = "additions"
    DEMOLITIONS = "demolitions"
    SQUARE_FOOTAGE = "square_footage"
    ARCHITECT = "architect"
    ENROLLMENT = "enrollment"
    BOND_HISTORY = "bond_history"
    LEVY_HISTORY = "levy_history"
    OFCC_INFORMATION = "ofcc_information"
    FACILITY_CONDITION = "facility_condition"
    BOARD_DISCUSSIONS = "board_discussions"
    NEWS = "news"
    CONTACT_INFORMATION = "contact_information"
