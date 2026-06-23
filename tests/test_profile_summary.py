import asyncio

import pytest
from fastapi.testclient import TestClient

from main import app
from profile_summary.config import PROFILE_SECTIONS
from profile_summary.data_provider import ProfileDataProvider, SectionPayload
from profile_summary.dummy_provider import DummyDataProvider
from profile_summary.resolver import resolve_sections
from profile_summary.schemas import ProfileSummaryRequest, ProfileType
from profile_summary.summary_service import (
    generate_profile_summary,
    generate_simple_profile_summary,
)


@pytest.mark.parametrize("profile_type", list(ProfileType))
def test_endpoint_generates_all_profile_types(
    profile_type: ProfileType, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def fake_generate_narrative(
        requested_profile_type: ProfileType,
        sections_data: dict[str, dict],
    ) -> dict[str, str]:
        del requested_profile_type
        return {
            section.replace("_", " ").title(): "Generated summary."
            for section in sections_data
        }

    monkeypatch.setattr(
        "profile_summary.summary_service.generate_narrative",
        fake_generate_narrative,
    )
    response = TestClient(app).post(
        "/summaries/profile",
        json={
            "profile_type": profile_type.value,
            "profile_id": f"{profile_type.value}-101",
            "requesting_user_id": "user-1",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["profile_type"] == profile_type.value
    assert body["profile_id"] == f"{profile_type.value}-101"
    assert body["sources"] == PROFILE_SECTIONS[profile_type]
    assert isinstance(body["summary_text"], dict)
    assert len(body["summary_text"]) == len(PROFILE_SECTIONS[profile_type])


def test_resolver_preserves_configured_order() -> None:
    result = resolve_sections(
        ProfileType.CLIENT,
        ["documents", "profile", "goals", "unknown"],
    )

    assert result == ["profile", "goals", "documents"]


@pytest.mark.parametrize("profile_type", list(ProfileType))
def test_simple_endpoint_returns_sources_without_groq(
    profile_type: ProfileType, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def fail_if_called(*args, **kwargs) -> str:
        raise AssertionError("The simple endpoint must not call Groq")

    monkeypatch.setattr(
        "profile_summary.summary_service.generate_narrative",
        fail_if_called,
    )

    response = TestClient(app).post(
        "/summaries/profile/simple",
        json={
            "profile_type": profile_type.value,
            "profile_id": f"{profile_type.value}-101",
            "requesting_user_id": "user-1",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["sources"] == PROFILE_SECTIONS[profile_type]
    assert list(body["summary_text"]) == [
        section.replace("_", " ").title()
        for section in PROFILE_SECTIONS[profile_type]
    ]


@pytest.mark.parametrize("profile_type", list(ProfileType))
def test_data_endpoint_returns_raw_section_payloads(
    profile_type: ProfileType, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def fail_if_called(*args, **kwargs) -> str:
        raise AssertionError("The data endpoint must not call Groq")

    monkeypatch.setattr(
        "profile_summary.summary_service.generate_narrative",
        fail_if_called,
    )

    response = TestClient(app).post(
        "/summaries/profile/data",
        json={
            "profile_type": profile_type.value,
            "profile_id": f"{profile_type.value}-101",
            "requesting_user_id": "user-1",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["profile_id"] == f"{profile_type.value}-101"
    assert body["profile_type"] == profile_type.value
    assert [section["section_name"] for section in body["sections"]] == (
        PROFILE_SECTIONS[profile_type]
    )
    assert all(section["data"] for section in body["sections"])
    assert all(section["is_empty"] is False for section in body["sections"])


class SparseProvider(DummyDataProvider):
    async def get_documents(
        self, profile_type: ProfileType, profile_id: str
    ) -> SectionPayload:
        return {}


def test_service_drops_empty_sections(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_generate_narrative(
        profile_type: ProfileType,
        sections_data: dict[str, dict],
    ) -> dict[str, str]:
        del profile_type
        return {section: "Generated summary." for section in sections_data}

    monkeypatch.setattr(
        "profile_summary.summary_service.generate_narrative",
        fake_generate_narrative,
    )
    request = ProfileSummaryRequest(
        profile_type=ProfileType.FACILITY,
        profile_id="facility-1",
        requesting_user_id="user-1",
    )

    response = asyncio.run(generate_profile_summary(request, SparseProvider()))

    assert "documents" not in response.sources
    assert response.sources == PROFILE_SECTIONS[ProfileType.FACILITY][:-1]
    assert isinstance(SparseProvider(), ProfileDataProvider)


def test_simple_service_drops_empty_sections() -> None:
    request = ProfileSummaryRequest(
        profile_type=ProfileType.FACILITY,
        profile_id="facility-1",
        requesting_user_id="user-1",
    )

    response = asyncio.run(
        generate_simple_profile_summary(request, SparseProvider())
    )

    assert response.sources == PROFILE_SECTIONS[ProfileType.FACILITY][:-1]
    assert "Documents" not in response.summary_text
