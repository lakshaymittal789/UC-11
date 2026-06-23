import asyncio
import json

import pytest

from profile_summary.groq_client import SummarizerError
from profile_summary.prompts import (
    build_caregiver_prompt,
    build_client_prompt,
    build_facility_prompt,
)
from profile_summary.schemas import ProfileType
from profile_summary.summarizer import EMPTY_SUMMARY, generate_narrative


@pytest.mark.parametrize(
    ("builder", "profile_label", "expected_section"),
    [
        (build_client_prompt, "client", "Health Updates"),
        (build_caregiver_prompt, "caregiver", "Client Ratings & Reviews"),
        (build_facility_prompt, "facility", "Updates"),
    ],
)
def test_prompt_builders_serialize_section_data(
    builder, profile_label: str, expected_section: str
) -> None:
    sections = {"profile": {"name": "Test Profile"}}

    system_prompt, user_prompt = builder(sections)

    assert expected_section in system_prompt
    assert f"Here is the {profile_label} profile data:" in user_prompt
    assert json.dumps(sections, indent=2) in user_prompt


def test_caregiver_prompt_requires_utilization_rate() -> None:
    system_prompt, _ = build_caregiver_prompt({})

    assert "utilization rate as a percentage" in system_prompt


def test_empty_sections_skip_groq(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fail_if_called(system_prompt: str, user_prompt: str) -> str:
        raise AssertionError("Groq should not be called")

    monkeypatch.setattr("profile_summary.summarizer.call_groq", fail_if_called)

    result = asyncio.run(generate_narrative(ProfileType.CLIENT, {}))

    assert result == EMPTY_SUMMARY


def test_narrative_dispatches_to_groq(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, str] = {}

    async def fake_call_groq(system_prompt: str, user_prompt: str) -> str:
        captured["system_prompt"] = system_prompt
        captured["user_prompt"] = user_prompt
        return '{"Profile": "Test narrative."}'

    monkeypatch.setattr("profile_summary.summarizer.call_groq", fake_call_groq)

    result = asyncio.run(
        generate_narrative(
            ProfileType.CLIENT,
            {"profile": {"name": "Client 101"}},
        )
    )

    assert result == {"Profile": "Test narrative."}
    assert "home care client" in captured["system_prompt"]
    assert '"Client 101"' in captured["user_prompt"]


def test_missing_api_key_is_wrapped(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.chdir("tests")

    from profile_summary.groq_client import call_groq

    with pytest.raises(SummarizerError):
        asyncio.run(call_groq("system", "user"))
