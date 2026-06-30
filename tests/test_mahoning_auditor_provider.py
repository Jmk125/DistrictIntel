"""Mahoning County Auditor provider tests."""

from __future__ import annotations

from districtintel.models import Evidence, ProviderContext, School, SourceType
from districtintel.providers import MahoningCountyAuditorProvider, ProviderCapability
from districtintel.web import FetchResult


class FakeWebClient:
    """Fake WebClient returning a configured FetchResult."""

    def __init__(self, result: FetchResult) -> None:
        self._result = result
        self.urls: list[str] = []

    def fetch(self, url: str) -> FetchResult:
        self.urls.append(url)
        return self._result


def test_mahoning_auditor_provider_returns_evidence_for_successful_page() -> None:
    """A useful mocked auditor page is converted into evidence."""

    page = """
    <html><body>
      <h1>Property Details</h1>
      <dl>
        <dt>Parcel</dt><dd>53-001-0-000.00-0</dd>
        <dt>Year Built</dt><dd>1965</dd>
        <dt>Living Area</dt><dd>42,000</dd>
      </dl>
    </body></html>
    """
    web_client = FakeWebClient(
        FetchResult(
            url="https://auditor.mahoningcountyoh.gov/search?q=Example",
            final_url="https://auditor.mahoningcountyoh.gov/property/53-001",
            status_code=200,
            content_type="text/html; charset=utf-8",
            text=page,
        )
    )
    provider = MahoningCountyAuditorProvider(web_client=web_client)
    school = School(
        id=1,
        district_id=1,
        name="Example Elementary",
        address="123 Main St",
        city="Youngstown",
    )

    evidence = provider.collect_evidence(school, ProviderContext())

    assert provider.capabilities == (
        ProviderCapability.YEAR_BUILT,
        ProviderCapability.SQUARE_FOOTAGE,
    )
    assert len(evidence) == 1
    assert isinstance(evidence[0], Evidence)
    assert evidence[0].source.title == "Mahoning County Auditor Property Search"
    assert evidence[0].source.source_type is SourceType.COUNTY_AUDITOR
    assert evidence[0].source.url == "https://auditor.mahoningcountyoh.gov/property/53-001"
    assert "Year Built" in evidence[0].excerpt
    assert "Living Area" in evidence[0].excerpt
    assert web_client.urls == [
        "https://auditor.mahoningcountyoh.gov/search?q=123+Main+St+Youngstown"
    ]


def test_mahoning_auditor_provider_handles_failed_fetch_cleanly() -> None:
    """Failed pages return no evidence and raise no provider exception."""

    web_client = FakeWebClient(
        FetchResult(
            url="https://auditor.mahoningcountyoh.gov/search?q=missing",
            error_message="Request timed out: timed out",
        )
    )
    provider = MahoningCountyAuditorProvider(web_client=web_client)
    school = School(id=1, district_id=1, name="Example", address="123 Main St")

    evidence = provider.collect_evidence(school, ProviderContext())

    assert evidence == ()


def test_mahoning_auditor_provider_handles_page_without_property_details() -> None:
    """Pages without useful property details return no evidence."""

    web_client = FakeWebClient(
        FetchResult(
            url="https://auditor.mahoningcountyoh.gov/search?q=empty",
            status_code=200,
            text="<html><body>No matching records found.</body></html>",
        )
    )
    provider = MahoningCountyAuditorProvider(web_client=web_client)
    school = School(id=1, district_id=1, name="Example", address="123 Main St")

    evidence = provider.collect_evidence(school, ProviderContext())

    assert evidence == ()


def test_mahoning_auditor_provider_does_not_create_facts() -> None:
    """The provider returns Evidence objects only, never Facts."""

    web_client = FakeWebClient(
        FetchResult(
            url="https://auditor.mahoningcountyoh.gov/search?q=Example",
            status_code=200,
            text="<html><body>Property Details Year Built 1965 Living Area 42,000</body></html>",
        )
    )
    provider = MahoningCountyAuditorProvider(web_client=web_client)
    school = School(id=1, district_id=1, name="Example", address="123 Main St")

    results = provider.collect_evidence(school, ProviderContext())

    assert all(isinstance(result, Evidence) for result in results)
