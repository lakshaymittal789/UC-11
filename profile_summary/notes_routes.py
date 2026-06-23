from typing import Annotated

from fastapi import APIRouter, Depends

from profile_summary.data_provider import ProfileDataProvider
from profile_summary.dummy_provider import DummyDataProvider
from profile_summary.notes_publish_service import publish_note
from profile_summary.notes_rbac import get_notes_user_permissions
from profile_summary.notes_save_service import save_notes_summary
from profile_summary.notes_summary_service import generate_notes_summary
from profile_summary.schemas import (
    NotesSaveRequest,
    NotesSaveResponse,
    NotesSummaryRequest,
    NotesSummaryResponse,
    PublishRequest,
    PublishResponse,
)

router = APIRouter(tags=["notes summaries"])


def get_notes_data_provider() -> ProfileDataProvider:
    return DummyDataProvider()


@router.post("/summaries/notes", response_model=NotesSummaryResponse)
async def create_notes_summary(
    request: NotesSummaryRequest,
    provider: Annotated[ProfileDataProvider, Depends(get_notes_data_provider)],
    user_permissions: Annotated[
        list[str], Depends(get_notes_user_permissions)
    ],
) -> NotesSummaryResponse:
    return await generate_notes_summary(request, provider, user_permissions)


@router.post("/summaries/notes/list")
async def list_client_notes(
    request: NotesSummaryRequest,
    provider: Annotated[ProfileDataProvider, Depends(get_notes_data_provider)],
) -> dict[str, object]:
    notes = await provider.get_notes("client", request.client_id)
    if not isinstance(notes, list):
        notes = []
    return {
        "client_id": request.client_id,
        "notes": notes,
    }


@router.post("/summaries/notes/save", response_model=NotesSaveResponse)
async def create_saved_notes_summary(
    request: NotesSaveRequest,
    provider: Annotated[ProfileDataProvider, Depends(get_notes_data_provider)],
) -> NotesSaveResponse:
    return await save_notes_summary(request, provider)


@router.post("/notes/{note_id}/publish", response_model=PublishResponse)
async def publish_saved_note(
    note_id: str,
    request: PublishRequest,
    provider: Annotated[ProfileDataProvider, Depends(get_notes_data_provider)],
) -> PublishResponse:
    return await publish_note(note_id, request, provider)
