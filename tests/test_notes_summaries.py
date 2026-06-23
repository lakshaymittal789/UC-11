import asyncio
import json

import pytest
from fastapi.testclient import TestClient

from main import app
from profile_summary.dummy_provider import DummyDataProvider
from profile_summary.notes_dummy_data import NOTES
from profile_summary.notes_prompts import build_notes_prompt
from profile_summary.notes_publish_service import publish_note
from profile_summary.notes_rbac import (
    OFFICE_NOTES_PERMISSION,
    get_notes_user_permissions,
    user_can_view_office_notes,
)
from profile_summary.notes_save_service import save_notes_summary
from profile_summary.notes_summary_service import generate_notes_summary
from profile_summary.schemas import (
    NotesSaveRequest,
    NotesSummaryRequest,
    PublishRequest,
    TimeFilter,
)


@pytest.fixture
def restore_notes():
    original_length = len(NOTES)
    yield
    del NOTES[original_length:]


def _summary_request(**overrides) -> NotesSummaryRequest:
    values = {
        "client_id": "client-101",
        "requesting_user_id": "user-1",
        "time_filter": TimeFilter.CUSTOM,
        "custom_start": "2026-05-01",
        "custom_end": "2026-06-22",
        "include_care_notes": True,
        "include_care_published": True,
        "include_care_unpublished": True,
        "include_family_notes": True,
        "include_family_published": True,
        "include_family_unpublished": True,
        "include_office_notes": True,
    }
    values.update(overrides)
    return NotesSummaryRequest(**values)


def test_notes_prompt_serializes_data() -> None:
    notes = {"care": [{"content": "Mobility improved."}]}

    system_prompt, user_prompt = build_notes_prompt(notes)

    assert "Clinical & Care Observations" in system_prompt
    assert "plain-text paragraph of 2-4 sentences" in system_prompt
    assert json.dumps(notes, indent=2) == user_prompt


def test_office_permission_stub() -> None:
    assert user_can_view_office_notes([OFFICE_NOTES_PERMISSION])
    assert not user_can_view_office_notes([])


def test_generation_filters_and_parses_sections(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_call_groq(system_prompt: str, user_prompt: str) -> str:
        assert "Administrative Updates" in system_prompt
        assert '"office"' in user_prompt
        return json.dumps(
            {
                "Clinical & Care Observations": (
                    "Mobility and medication adherence were documented."
                ),
                "Family Communications": (
                    "Family discussed scheduling and care-plan review."
                ),
                "Administrative Updates": (
                    "Remaining authorization hours were recorded."
                ),
            }
        )

    monkeypatch.setattr(
        "profile_summary.notes_summary_service.call_groq",
        fake_call_groq,
    )

    response = asyncio.run(
        generate_notes_summary(
            _summary_request(),
            DummyDataProvider(),
            [OFFICE_NOTES_PERMISSION],
        )
    )

    assert response.includes_office_notes is True
    assert "2 Care Notes (1 Published, 1 Unpublished)" in response.context_line
    assert "2 Family Notes (1 Published, 1 Unpublished)" in response.context_line
    assert "1 Office Notes" in response.context_line
    assert list(response.sections) == [
        "Clinical & Care Observations",
        "Family Communications",
        "Administrative Updates",
    ]
    assert all(response.sections.values())


def test_parser_accepts_common_markdown_header_variations(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_call_groq(system_prompt: str, user_prompt: str) -> str:
        return (
            "### **Clinical and Care Observations:**\n"
            "- Care observation.\n\n"
            "# Family Communications:\n"
            "- Family communication."
        )

    monkeypatch.setattr(
        "profile_summary.notes_summary_service.call_groq",
        fake_call_groq,
    )

    response = asyncio.run(
        generate_notes_summary(
            _summary_request(include_office_notes=False),
            DummyDataProvider(),
            [],
        )
    )

    assert list(response.sections.values()) == [
        "- Care observation.",
        "- Family communication.",
    ]


def test_office_notes_are_forced_off_without_permission(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_call_groq(system_prompt: str, user_prompt: str) -> str:
        assert '"office"' not in user_prompt
        return json.dumps(
            {
                "Clinical & Care Observations": "Care note summary.",
                "Family Communications": "Family note summary.",
            }
        )

    monkeypatch.setattr(
        "profile_summary.notes_summary_service.call_groq",
        fake_call_groq,
    )

    response = asyncio.run(
        generate_notes_summary(
            _summary_request(),
            DummyDataProvider(),
            [],
        )
    )

    assert response.includes_office_notes is False
    assert "Office Notes" not in response.context_line
    assert "Administrative Updates" not in response.sections


def test_empty_filter_skips_llm(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fail_if_called(system_prompt: str, user_prompt: str) -> str:
        raise AssertionError("Groq must not be called for an empty result")

    monkeypatch.setattr(
        "profile_summary.notes_summary_service.call_groq",
        fail_if_called,
    )

    response = asyncio.run(
        generate_notes_summary(
            _summary_request(
                include_care_notes=False,
                include_family_notes=False,
                include_office_notes=False,
            ),
            DummyDataProvider(),
            [OFFICE_NOTES_PERMISSION],
        )
    )

    assert response.sections == {}
    assert "No notes matched the selected filters." in response.context_line


def test_notes_generation_endpoint_enforces_permission(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_call_groq(system_prompt: str, user_prompt: str) -> str:
        assert '"office"' not in user_prompt
        return "## Clinical & Care Observations\n- Care notes were reviewed."

    monkeypatch.setattr(
        "profile_summary.notes_summary_service.call_groq",
        fake_call_groq,
    )
    app.dependency_overrides[get_notes_user_permissions] = lambda: []
    try:
        response = TestClient(app).post(
            "/summaries/notes",
            json=_summary_request(
                include_family_notes=False
            ).model_dump(mode="json"),
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["includes_office_notes"] is False


def test_save_status_and_publish_gate(restore_notes) -> None:
    provider = DummyDataProvider()
    locked_request = NotesSaveRequest(
        client_id="client-101",
        sections={
            "Administrative Updates": "Internal authorization information."
        },
        context_line="Based on dates: 2026-06-01 – 2026-06-22.",
        date_range_start="2026-06-01",
        date_range_end="2026-06-22",
        includes_office_notes=True,
        generated_by="staff-1",
    )

    saved = asyncio.run(save_notes_summary(locked_request, provider))

    assert saved.status == "internal_staff_only"
    with pytest.raises(Exception) as exc_info:
        asyncio.run(
            publish_note(
                saved.note_id,
                PublishRequest(requesting_user_id="staff-1"),
                provider,
            )
        )
    assert getattr(exc_info.value, "status_code", None) == 403
    stored = asyncio.run(provider.get_note_by_id(saved.note_id))
    assert stored is not None
    assert stored["status"] == "internal_staff_only"
    assert stored["published"] is False


def test_unlocked_saved_summary_can_be_published(restore_notes) -> None:
    provider = DummyDataProvider()
    save_request = NotesSaveRequest(
        client_id="client-101",
        sections={"Clinical & Care Observations": "Mobility improved."},
        context_line="Based on dates: 2026-06-01 – 2026-06-22.",
        date_range_start="2026-06-01",
        date_range_end="2026-06-22",
        includes_office_notes=False,
        generated_by="staff-1",
    )

    saved = asyncio.run(save_notes_summary(save_request, provider))
    published = asyncio.run(
        publish_note(
            saved.note_id,
            PublishRequest(requesting_user_id="staff-1"),
            provider,
        )
    )

    assert saved.status == "unpublished"
    assert published.status == "published"
    stored = asyncio.run(provider.get_note_by_id(saved.note_id))
    assert stored is not None
    assert stored["published"] is True
    assert stored["status"] == "published"


def test_publish_endpoint_returns_404() -> None:
    response = TestClient(app).post(
        "/notes/missing-note/publish",
        json={"requesting_user_id": "staff-1"},
    )

    assert response.status_code == 404
