import asyncio
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime

from profile_summary.config import PROFILE_SECTIONS
from profile_summary.data_provider import ProfileDataProvider, SectionPayload
from profile_summary.resolver import resolve_sections
from profile_summary.schemas import (
    ProfileDataResponse,
    ProfileSummaryRequest,
    ProfileSummaryResponse,
    ProfileType,
    SectionData,
)
from profile_summary.summarizer import generate_narrative

SectionFetcher = Callable[[ProfileType, str], Awaitable[SectionPayload]]


def _get_user_permissions(
    requesting_user_id: str, profile_type: ProfileType
) -> list[str]:
    """Temporary RBAC stub: every requesting user can access configured sections."""

    del requesting_user_id
    return list(PROFILE_SECTIONS[profile_type])


def _section_fetchers(provider: ProfileDataProvider) -> dict[str, SectionFetcher]:
    return {
        "profile": provider.get_profile_info,
        "health_updates": provider.get_notes,
        "updates": provider.get_notes,
        "schedule": provider.get_schedule,
        "schedule_visit_activity": provider.get_schedule,
        "care_plan": provider.get_care_plan,
        "medications": provider.get_medications,
        "goals": provider.get_goals,
        "authorizations": provider.get_authorizations,
        "invoices": provider.get_invoices,
        "forms": provider.get_forms,
        "documents": provider.get_documents,
        "client_ratings": provider.get_ratings,
        "compliance": provider.get_compliance,
        "skills_restrictions": provider.get_skills,
        "compatibility": provider.get_compatibility,
    }


async def _collect_sections(
    request: ProfileSummaryRequest, provider: ProfileDataProvider
) -> list[SectionData]:
    user_permissions = _get_user_permissions(
        request.requesting_user_id, request.profile_type
    )
    allowed_sections = resolve_sections(request.profile_type, user_permissions)
    fetchers = _section_fetchers(provider)

    payloads = await asyncio.gather(
        *(
            fetchers[section](request.profile_type, request.profile_id)
            for section in allowed_sections
        )
    )

    return [
        SectionData(
            section_name=section_name,
            data=payload,
            is_empty=not bool(payload),
        )
        for section_name, payload in zip(allowed_sections, payloads, strict=True)
        if payload
    ]


async def generate_profile_summary(
    request: ProfileSummaryRequest, provider: ProfileDataProvider
) -> ProfileSummaryResponse:
    sections_data = await _collect_sections(request, provider)
    sources = [section.section_name for section in sections_data]

    return ProfileSummaryResponse(
        profile_id=request.profile_id,
        profile_type=request.profile_type,
        generated_at=datetime.now(UTC),
        sources=sources,
        summary_text=await generate_narrative(
            request.profile_type,
            {section.section_name: section.data for section in sections_data},
        ),
    )


async def generate_simple_profile_summary(
    request: ProfileSummaryRequest, provider: ProfileDataProvider
) -> ProfileSummaryResponse:
    """Generate a deterministic summary without calling the LLM."""

    sections_data = await _collect_sections(request, provider)
    sources = [section.section_name for section in sections_data]
    return ProfileSummaryResponse(
        profile_id=request.profile_id,
        profile_type=request.profile_type,
        generated_at=datetime.now(UTC),
        sources=sources,
        summary_text={
            section.replace("_", " ").title(): "Data is available for this section."
            for section in sources
        },
    )


async def get_profile_section_data(
    request: ProfileSummaryRequest, provider: ProfileDataProvider
) -> ProfileDataResponse:
    """Return resolved raw section data without invoking the summarizer."""

    sections_data = await _collect_sections(request, provider)
    return ProfileDataResponse(
        profile_id=request.profile_id,
        profile_type=request.profile_type,
        sections=sections_data,
    )
