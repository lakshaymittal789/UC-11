import json
from typing import Any

SectionsData = dict[str, dict[str, Any]]


def _serialize_user_prompt(profile_label: str, sections_data: SectionsData) -> str:
    serialized_data = json.dumps(sections_data, indent=2, default=str)
    return f"Here is the {profile_label} profile data:\n{serialized_data}"


def _system_prompt(profile_label: str, ordered_sections: str) -> str:
    return (
        f"You are generating a concise AI profile summary for a home care "
        f"{profile_label}, for agency staff use. Write one short narrative paragraph "
        f"per section provided below, in this exact order if present: "
        f"{ordered_sections}. Only write a section if its data is present in the "
        "input; do not invent or mention missing sections. Ground every sentence "
        "strictly in the provided data and do not fabricate names, dates, or numbers. "
        "Return ONLY one valid JSON object. Each key must be the exact display section "
        "name and each value must be a 2-4 sentence plain-text paragraph. Do not use "
        "markdown, bullets, or newline-delimited sections."
    )


def build_client_prompt(sections_data: SectionsData) -> tuple[str, str]:
    sections = (
        "Profile, Health Updates, Schedule, Care Plan, Medications, Goals, "
        "Authorizations, Invoices, Forms Summary & Audit, "
        "Documents & File Repository"
    )
    return _system_prompt("client", sections), _serialize_user_prompt(
        "client", sections_data
    )


def build_caregiver_prompt(sections_data: SectionsData) -> tuple[str, str]:
    sections = (
        "Profile, Schedule & Visit Activity, Client Ratings & Reviews, Compliance, "
        "Skills & Restrictions, Compatibility, Forms Summary & Audit, "
        "Documents & File Repository"
    )
    system_prompt = (
        _system_prompt("caregiver", sections)
        + " In the Profile value, if weekly_hours_requested and last_week_hours are "
        "both present, explicitly state the utilization rate as a percentage."
    )
    return system_prompt, _serialize_user_prompt("caregiver", sections_data)


def build_facility_prompt(sections_data: SectionsData) -> tuple[str, str]:
    sections = (
        "Profile, Updates, Schedule, Authorizations, Invoices, "
        "Forms Summary & Audit, Documents & File Repository"
    )
    return _system_prompt("facility", sections), _serialize_user_prompt(
        "facility", sections_data
    )
