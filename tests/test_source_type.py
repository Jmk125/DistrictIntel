"""Source type model tests."""

from __future__ import annotations

from districtintel.models import Source, SourceType


def test_source_type_contains_controlled_vocabulary() -> None:
    """SourceType defines source categories expected by future providers."""

    assert SourceType.COUNTY_AUDITOR.value == "county_auditor"
    assert SourceType.OFCC.value == "ofcc"
    assert SourceType.DISTRICT_FACILITY_PLAN.value == "district_facility_plan"
    assert SourceType.DISTRICT_WEBSITE.value == "district_website"
    assert SourceType.BOARD_MINUTES.value == "board_minutes"
    assert SourceType.ARCHITECT_DOCUMENT.value == "architect_document"
    assert SourceType.GOVERNMENT_PUBLICATION.value == "government_publication"
    assert SourceType.LOCAL_NEWS.value == "local_news"
    assert SourceType.OTHER.value == "other"


def test_source_defaults_to_other_source_type() -> None:
    """Unknown or uncategorized sources remain representable as other."""

    source = Source(title="Uncategorized source")

    assert source.source_type is SourceType.OTHER
