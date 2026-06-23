from datetime import UTC, datetime

from fastapi import HTTPException, status

from profile_summary.data_provider import ProfileDataProvider
from profile_summary.schemas import PublishRequest, PublishResponse


# The frontend hides Publish for locked notes, but UI state is not a security
# boundary. This endpoint must re-check the note's current persisted state.
async def publish_note(
    note_id: str,
    request: PublishRequest,
    provider: ProfileDataProvider,
) -> PublishResponse:
    note = await provider.get_note_by_id(note_id)
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note '{note_id}' was not found",
        )
    if note.get("includes_office_notes") is True or note.get("status") == (
        "internal_staff_only"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Notes containing office content cannot be published",
        )

    published_at = datetime.now(UTC)
    updated = await provider.update_note(
        note_id,
        {
            "status": "published",
            "published": True,
            "published_at": published_at.isoformat(),
            "published_by": request.requesting_user_id,
        },
    )
    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note '{note_id}' was not found",
        )
    return PublishResponse(
        note_id=note_id,
        status="published",
        published_at=published_at,
    )
