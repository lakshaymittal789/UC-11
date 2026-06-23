from datetime import UTC, date, datetime, timedelta
from typing import Any

from profile_summary.data_provider import NoteRecord, ProfileDataProvider
from profile_summary.groq_client import call_groq
from profile_summary.llm_json import parse_summary_object
from profile_summary.notes_prompts import build_notes_prompt
from profile_summary.notes_rbac import user_can_view_office_notes
from profile_summary.schemas import (
    NotesSummaryRequest,
    NotesSummaryResponse,
    TimeFilter,
)

HEADER_BY_TYPE = {
    "care": "Clinical & Care Observations",
    "family": "Family Communications",
    "office": "Administrative Updates",
}
HEADER_ALIASES = {
    "clinical & care observations": "Clinical & Care Observations",
    "clinical and care observations": "Clinical & Care Observations",
    "family communications": "Family Communications",
    "administrative updates": "Administrative Updates",
}


def _resolve_date_range(request: NotesSummaryRequest) -> tuple[date, date]:
    end = date.today()
    days_by_filter = {
        TimeFilter.LAST_30: 30,
        TimeFilter.LAST_60: 60,
        TimeFilter.LAST_90: 90,
    }
    if request.time_filter is TimeFilter.CUSTOM:
        assert request.custom_start is not None
        assert request.custom_end is not None
        return request.custom_start, request.custom_end
    return end - timedelta(days=days_by_filter[request.time_filter]), end


def _note_date(note: NoteRecord) -> date:
    value = note["created_at"]
    if isinstance(value, datetime):
        return value.date()
    return datetime.fromisoformat(value.replace("Z", "+00:00")).date()


def _parse_sections(
    response_text: str,
    filtered_notes_by_type: dict[str, list[NoteRecord]],
) -> dict[str, str]:
    parsed = parse_summary_object(response_text)
    canonical = {
        HEADER_ALIASES.get(header.casefold(), header): text
        for header, text in parsed.items()
    }
    return {
        HEADER_BY_TYPE[note_type]: canonical.get(HEADER_BY_TYPE[note_type], "")
        for note_type in ("care", "family", "office")
        if filtered_notes_by_type.get(note_type)
    }


def _matches_publication_filter(
    note: NoteRecord, include_published: bool, include_unpublished: bool
) -> bool:
    return (
        bool(note["published"]) and include_published
    ) or (
        not bool(note["published"]) and include_unpublished
    )


def _build_context_line(
    start: date,
    end: date,
    grouped_notes: dict[str, list[NoteRecord]],
) -> str:
    clauses: list[str] = []
    labels = {
        "care": "Care Notes",
        "family": "Family Notes",
    }
    for note_type in ("care", "family"):
        notes = grouped_notes.get(note_type, [])
        if not notes:
            continue
        published = sum(bool(note["published"]) for note in notes)
        unpublished = len(notes) - published
        clauses.append(
            f"{len(notes)} {labels[note_type]} "
            f"({published} Published, {unpublished} Unpublished)"
        )

    office_notes = grouped_notes.get("office", [])
    if office_notes:
        clauses.append(f"{len(office_notes)} Office Notes")

    prefix = f"Based on dates: {start.isoformat()} – {end.isoformat()}."
    if not clauses:
        return f"{prefix} No notes matched the selected filters."
    if len(clauses) == 1:
        joined = clauses[0]
    else:
        joined = f"{', '.join(clauses[:-1])}, and {clauses[-1]}"
    return f"{prefix} Synthesizing {joined}."


async def generate_notes_summary(
    request: NotesSummaryRequest,
    provider: ProfileDataProvider,
    user_permissions: list[str],
) -> NotesSummaryResponse:
    start, end = _resolve_date_range(request)
    includes_office_notes = (
        request.include_office_notes
        and user_can_view_office_notes(user_permissions)
    )
    provider_result = await provider.get_notes("client", request.client_id)
    if not isinstance(provider_result, list):
        raise TypeError("Notes provider returned an invalid notes collection")

    notes_in_range = [
        note for note in provider_result if start <= _note_date(note) <= end
    ]
    grouped: dict[str, list[NoteRecord]] = {}
    if request.include_care_notes:
        grouped["care"] = [
            note
            for note in notes_in_range
            if note["note_type"] == "care"
            and _matches_publication_filter(
                note,
                request.include_care_published,
                request.include_care_unpublished,
            )
        ]
    if request.include_family_notes:
        grouped["family"] = [
            note
            for note in notes_in_range
            if note["note_type"] == "family"
            and _matches_publication_filter(
                note,
                request.include_family_published,
                request.include_family_unpublished,
            )
        ]
    if includes_office_notes:
        grouped["office"] = [
            note for note in notes_in_range if note["note_type"] == "office"
        ]

    grouped = {note_type: notes for note_type, notes in grouped.items() if notes}
    context_line = _build_context_line(start, end, grouped)
    if not grouped:
        return NotesSummaryResponse(
            client_id=request.client_id,
            context_line=context_line,
            sections={},
            includes_office_notes=includes_office_notes,
            generated_at=datetime.now(UTC),
        )

    prompt_data: dict[str, list[dict[str, Any]]] = {
        note_type: [
            {
                "content": note["content"],
                "published": note["published"],
                "created_by": note["created_by"],
                "created_at": note["created_at"],
            }
            for note in notes
        ]
        for note_type, notes in grouped.items()
    }
    system_prompt, user_prompt = build_notes_prompt(prompt_data)
    narrative = await call_groq(system_prompt, user_prompt)

    return NotesSummaryResponse(
        client_id=request.client_id,
        context_line=context_line,
        sections=_parse_sections(narrative, grouped),
        includes_office_notes=includes_office_notes,
        generated_at=datetime.now(UTC),
    )
