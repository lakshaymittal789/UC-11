import asyncio
import json

import pytest
from fastapi.testclient import TestClient

from main import app
from profile_summary.combined_form_service import (
    generate_combined_form_summary,
)
from profile_summary.dummy_provider import DummyDataProvider
from profile_summary.form_prompts import (
    build_combined_form_prompt,
    build_custom_form_prompt,
    build_fixed_form_prompt,
)
from profile_summary.forms_dummy_data import FORMS
from profile_summary.schemas import (
    CombinedFormSummaryRequest,
    FormOwnerType,
)


def test_form_seed_covers_all_owner_types_and_trend_paths() -> None:
    assert len(FORMS) >= 8
    assert {form["owner_type"] for form in FORMS} == {
        owner_type.value for owner_type in FormOwnerType
    }

    client_care_assessments = [
        form
        for form in FORMS
        if form["owner_id"] == "client-101"
        and form["form_category"] == "Care Assessment"
        and form["status"] == "completed"
    ]
    client_medication_reviews = [
        form
        for form in FORMS
        if form["owner_id"] == "client-101"
        and form["form_category"] == "Medication Review"
        and form["status"] == "completed"
    ]

    assert len(client_care_assessments) >= 2
    assert len(client_medication_reviews) == 1


def test_dummy_provider_fetches_owner_forms_and_form_by_id() -> None:
    provider = DummyDataProvider()

    forms = asyncio.run(
        provider.get_forms(FormOwnerType.CLIENT, "client-101")
    )
    form = asyncio.run(provider.get_form_by_id("form-client-001"))

    assert isinstance(forms, list)
    assert len(forms) == 4
    assert form is not None
    assert form["form_name"] == "Initial Care Assessment"


def test_form_prompt_builders_serialize_data() -> None:
    form = FORMS[0]
    audit = {"total_forms": 2}
    grouped = {"Care Assessment": [form]}

    combined_system, combined_user = build_combined_form_prompt(audit, grouped)
    fixed_system, fixed_user = build_fixed_form_prompt(form)
    custom_system, custom_user = build_custom_form_prompt(FORMS[2])

    assert "Executive Synthesis" in combined_system
    assert "valid JSON object" in combined_system
    assert '"Care Assessment"' in combined_user
    assert "Care Needs Summary" in fixed_system
    assert json.dumps(form["responses_json"], indent=2) == fixed_user
    assert "Additional Notes" in custom_system
    assert '"Are medications taken as scheduled?"' in custom_user


def test_combined_form_service_parses_groups(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_call_groq(system_prompt: str, user_prompt: str) -> str:
        assert "AI Comparison & Trend" in system_prompt
        assert '"in_progress_forms": 1' in user_prompt
        return json.dumps(
            {
                "Executive Synthesis": (
                    "The record contains completed assessments and one open form."
                ),
                "Care Assessment": (
                    "Mobility endurance improved and fall risk decreased over time."
                ),
                "Medication Review": (
                    "The client reports taking medications as scheduled."
                ),
            }
        )

    monkeypatch.setattr(
        "profile_summary.combined_form_service.call_groq",
        fake_call_groq,
    )
    request = CombinedFormSummaryRequest(
        owner_type=FormOwnerType.CLIENT,
        owner_id="client-101",
        requesting_user_id="user-1",
    )

    response = asyncio.run(
        generate_combined_form_summary(request, DummyDataProvider())
    )

    assert response.total_forms == 4
    assert response.completed_forms == 3
    assert response.in_progress_forms == 1
    assert response.date_range_start.isoformat() == "2026-01-15"
    assert response.date_range_end.isoformat() == "2026-05-22"
    assert response.executive_synthesis.startswith("The record")
    assert [
        (group.form_category, group.submission_count, group.is_trend)
        for group in response.group_summaries
    ] == [
        ("Care Assessment", 2, True),
        ("Medication Review", 1, False),
    ]


def test_combined_form_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_call_groq(system_prompt: str, user_prompt: str) -> str:
        return json.dumps(
            {
                "Executive Synthesis": "Applicant record reviewed.",
                "Application": "Application details are complete.",
            }
        )

    monkeypatch.setattr(
        "profile_summary.combined_form_service.call_groq",
        fake_call_groq,
    )

    response = TestClient(app).post(
        "/summaries/forms/chart",
        json={
            "owner_type": "applicant",
            "owner_id": "applicant-301",
            "requesting_user_id": "user-1",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total_forms"] == 2
    assert body["completed_forms"] == 1
    assert body["in_progress_forms"] == 1
    assert body["group_summaries"][0]["form_category"] == "Application"


@pytest.mark.parametrize(
    ("form_id", "is_fixed", "prompt_marker"),
    [
        ("form-client-001", True, "structured, system-generated"),
        ("form-client-003", False, "dynamic, agency-created"),
    ],
)
def test_single_form_endpoint_selects_prompt(
    form_id: str,
    is_fixed: bool,
    prompt_marker: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_call_groq(system_prompt: str, user_prompt: str) -> str:
        assert prompt_marker in system_prompt
        assert user_prompt.startswith("{")
        return '{"Overview": "Summary generated from form data."}'

    monkeypatch.setattr(
        "profile_summary.single_form_service.call_groq",
        fake_call_groq,
    )

    response = TestClient(app).post(
        f"/summaries/forms/{form_id}",
        json={"requesting_user_id": "user-1"},
    )

    assert response.status_code == 200
    assert response.json()["is_fixed"] is is_fixed
    assert response.json()["summary_text"] == {
        "Overview": "Summary generated from form data."
    }


def test_single_form_endpoint_returns_404() -> None:
    response = TestClient(app).post(
        "/summaries/forms/missing-form",
        json={"requesting_user_id": "user-1"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Form 'missing-form' was not found"
