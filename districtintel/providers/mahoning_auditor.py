"""Mahoning County Auditor source provider spike."""

from __future__ import annotations

import re
from html import unescape
from urllib.parse import quote_plus

from districtintel.models import Evidence, ProviderContext, School, Source, SourceType
from districtintel.providers.capabilities import ProviderCapability
from districtintel.web import WebClient

MAHONING_AUDITOR_SEARCH_URL = "https://auditor.mahoningcountyoh.gov/search"
_USEFUL_LABELS = (
    "year built",
    "living area",
    "square footage",
    "sq ft",
    "parcel",
    "property details",
    "building card",
)


class MahoningCountyAuditorProvider:
    """Collect evidence from Mahoning County Auditor public property pages.

    This provider is intentionally a spike: it fetches one public county auditor
    page through WebClient and extracts a short text excerpt when the page appears
    to contain property/building details. It does not perform final research,
    create facts, persist data, use AI, or bypass access controls.
    """

    name = "mahoning-county-auditor"
    capabilities = (
        ProviderCapability.YEAR_BUILT,
        ProviderCapability.SQUARE_FOOTAGE,
    )

    def __init__(self, web_client: WebClient | None = None) -> None:
        self._web_client = web_client or WebClient()

    def collect_evidence(
        self,
        school: School,
        context: ProviderContext,
    ) -> tuple[Evidence, ...]:
        """Fetch a Mahoning Auditor page and return evidence snippets if present."""

        url = self._build_search_url(school)
        if url is None:
            return ()

        result = self._web_client.fetch(url)
        if not result.succeeded or not result.text:
            return ()

        excerpt = _extract_property_excerpt(result.text)
        if excerpt is None:
            return ()

        source = Source(
            title="Mahoning County Auditor Property Search",
            url=result.final_url or result.url,
            source_type=SourceType.COUNTY_AUDITOR,
            accessed_at=result.fetched_at,
        )
        return (Evidence(source=source, excerpt=excerpt),)

    def _build_search_url(self, school: School) -> str | None:
        if not school.address:
            return None
        address_parts = [school.address]
        if school.city:
            address_parts.append(school.city)
        query = quote_plus(" ".join(address_parts))
        return f"{MAHONING_AUDITOR_SEARCH_URL}?q={query}"


def _extract_property_excerpt(html: str) -> str | None:
    text = _normalize_text(html)
    lower_text = text.lower()
    matching_positions = [lower_text.find(label) for label in _USEFUL_LABELS]
    matching_positions = [position for position in matching_positions if position >= 0]
    if not matching_positions:
        return None

    start = max(min(matching_positions) - 120, 0)
    end = min(start + 700, len(text))
    return text[start:end].strip()


def _normalize_text(html: str) -> str:
    without_scripts = re.sub(
        r"<script\b[^>]*>.*?</script>",
        " ",
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    without_styles = re.sub(
        r"<style\b[^>]*>.*?</style>",
        " ",
        without_scripts,
        flags=re.IGNORECASE | re.DOTALL,
    )
    without_tags = re.sub(r"<[^>]+>", " ", without_styles)
    return re.sub(r"\s+", " ", unescape(without_tags)).strip()
