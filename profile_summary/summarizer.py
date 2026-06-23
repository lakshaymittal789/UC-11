from collections.abc import Callable

from profile_summary.groq_client import call_groq
from profile_summary.llm_json import parse_summary_object
from profile_summary.prompts import (
    SectionsData,
    build_caregiver_prompt,
    build_client_prompt,
    build_facility_prompt,
)
from profile_summary.schemas import ProfileType

PromptBuilder = Callable[[SectionsData], tuple[str, str]]

PROMPT_BUILDERS: dict[ProfileType, PromptBuilder] = {
    ProfileType.CLIENT: build_client_prompt,
    ProfileType.CAREGIVER: build_caregiver_prompt,
    ProfileType.FACILITY: build_facility_prompt,
}

EMPTY_SUMMARY = {"Summary": "No data available to summarize for this profile."}


async def generate_narrative(
    profile_type: ProfileType, sections_data: SectionsData
) -> dict[str, str]:
    if not sections_data:
        return EMPTY_SUMMARY

    system_prompt, user_prompt = PROMPT_BUILDERS[profile_type](sections_data)
    response_text = await call_groq(system_prompt, user_prompt)
    return parse_summary_object(response_text)
