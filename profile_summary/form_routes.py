from typing import Annotated

from fastapi import APIRouter, Depends

from profile_summary.data_provider import ProfileDataProvider
from profile_summary.dummy_provider import DummyDataProvider
from profile_summary.schemas import (
    CombinedFormSummaryRequest,
    CombinedFormSummaryResponse,
    SingleFormSummaryRequest,
    SingleFormSummaryResponse,
)
from profile_summary.combined_form_service import generate_combined_form_summary
from profile_summary.single_form_service import generate_single_form_summary

router = APIRouter(prefix="/summaries/forms", tags=["form summaries"])


def get_form_data_provider() -> ProfileDataProvider:
    return DummyDataProvider()


@router.post("/chart", response_model=CombinedFormSummaryResponse)
async def create_combined_form_summary(
    request: CombinedFormSummaryRequest,
    provider: Annotated[ProfileDataProvider, Depends(get_form_data_provider)],
) -> CombinedFormSummaryResponse:
    return await generate_combined_form_summary(request, provider)


@router.post("/list")
async def list_forms_for_owner(
    request: CombinedFormSummaryRequest,
    provider: Annotated[ProfileDataProvider, Depends(get_form_data_provider)],
) -> dict[str, object]:
    forms = await provider.get_forms(request.owner_type, request.owner_id)
    if not isinstance(forms, list):
        forms = []
    return {
        "owner_type": request.owner_type,
        "owner_id": request.owner_id,
        "forms": forms,
    }


@router.post("/{form_id}", response_model=SingleFormSummaryResponse)
async def create_single_form_summary(
    form_id: str,
    request: SingleFormSummaryRequest,
    provider: Annotated[ProfileDataProvider, Depends(get_form_data_provider)],
) -> SingleFormSummaryResponse:
    del request
    return await generate_single_form_summary(form_id, provider)
