from datetime import UTC, datetime

from fastapi import HTTPException, status

from profile_summary.data_provider import ProfileDataProvider
from profile_summary.form_prompts import (
    build_custom_form_prompt,
    build_fixed_form_prompt,
)
from profile_summary.groq_client import call_groq
from profile_summary.llm_json import parse_summary_object
from profile_summary.schemas import SingleFormSummaryResponse


async def generate_single_form_summary(
    form_id: str,
    provider: ProfileDataProvider,
) -> SingleFormSummaryResponse:
    form = await provider.get_form_by_id(form_id)
    if form is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Form '{form_id}' was not found",
        )

    prompt_builder = (
        build_fixed_form_prompt if form["is_fixed"] else build_custom_form_prompt
    )
    system_prompt, user_prompt = prompt_builder(form)
    narrative = await call_groq(system_prompt, user_prompt)

    return SingleFormSummaryResponse(
        form_id=form_id,
        is_fixed=form["is_fixed"],
        generated_at=datetime.now(UTC),
        summary_text=parse_summary_object(narrative),
    )
