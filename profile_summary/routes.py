from typing import Annotated

from fastapi import APIRouter, Depends

from profile_summary.data_provider import ProfileDataProvider
from profile_summary.dummy_provider import DummyDataProvider
from profile_summary.schemas import (
    ProfileDataResponse,
    ProfileSummaryRequest,
    ProfileSummaryResponse,
)
from profile_summary.summary_service import (
    generate_profile_summary,
    generate_simple_profile_summary,
    get_profile_section_data,
)

router = APIRouter(tags=["profile summaries"])


def get_profile_data_provider() -> ProfileDataProvider:
    """Dependency-injection point to replace when the CRM provider is ready."""

    return DummyDataProvider()


@router.post("/summaries/profile", response_model=ProfileSummaryResponse)
async def create_profile_summary(
    request: ProfileSummaryRequest,
    provider: Annotated[ProfileDataProvider, Depends(get_profile_data_provider)],
) -> ProfileSummaryResponse:
    return await generate_profile_summary(request, provider)


@router.post("/summaries/profile/simple", response_model=ProfileSummaryResponse)
async def create_simple_profile_summary(
    request: ProfileSummaryRequest,
    provider: Annotated[ProfileDataProvider, Depends(get_profile_data_provider)],
) -> ProfileSummaryResponse:
    """Return sources and a deterministic summary without invoking Groq."""

    return await generate_simple_profile_summary(request, provider)


@router.post("/summaries/profile/data", response_model=ProfileDataResponse)
async def get_profile_data(
    request: ProfileSummaryRequest,
    provider: Annotated[ProfileDataProvider, Depends(get_profile_data_provider)],
) -> ProfileDataResponse:
    """Return raw provider data after permission and empty-section filtering."""

    return await get_profile_section_data(request, provider)
