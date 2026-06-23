from datetime import UTC, datetime
from uuid import uuid4

from profile_summary.data_provider import ProfileDataProvider
from profile_summary.schemas import NotesSaveRequest, NotesSaveResponse


async def save_notes_summary(
    request: NotesSaveRequest,
    provider: ProfileDataProvider,
) -> NotesSaveResponse:
    saved_at = datetime.now(UTC)
    status = (
        "internal_staff_only"
        if request.includes_office_notes
        else "unpublished"
    )
    combined_sections = "\n\n".join(
        f"{header}: {text}" for header, text in request.sections.items()
    )
    note_id = f"ai-note-{uuid4().hex[:12]}"
    await provider.save_note(
        {
            "id": note_id,
            "owner_type": "client",
            "owner_id": request.client_id,
            "note_type": "ai_summary",
            "published": False,
            "content": combined_sections,
            "context_line": request.context_line,
            "date_range_start": request.date_range_start.isoformat(),
            "date_range_end": request.date_range_end.isoformat(),
            "created_by": request.generated_by,
            "generated_by": request.generated_by,
            "created_at": saved_at.isoformat(),
            "saved_at": saved_at.isoformat(),
            "status": status,
            "includes_office_notes": request.includes_office_notes,
            "published_at": None,
            "is_ai_summary": True,
        }
    )
    return NotesSaveResponse(
        note_id=note_id,
        status=status,
        saved_at=saved_at,
    )
