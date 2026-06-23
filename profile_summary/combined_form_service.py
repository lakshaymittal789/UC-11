from collections import defaultdict
from datetime import UTC, date, datetime
from typing import Any

from profile_summary.data_provider import FormRecord, ProfileDataProvider
from profile_summary.form_prompts import build_combined_form_prompt
from profile_summary.groq_client import call_groq
from profile_summary.llm_json import parse_summary_object
from profile_summary.schemas import (
    CombinedFormSummaryRequest,
    CombinedFormSummaryResponse,
    FormGroupSummary,
)

def _completed_date(form: FormRecord) -> date:
    value = form["completed_date"]
    return value if isinstance(value, date) else date.fromisoformat(value)


async def generate_combined_form_summary(
    request: CombinedFormSummaryRequest,
    provider: ProfileDataProvider,
) -> CombinedFormSummaryResponse:
    provider_result = await provider.get_forms(request.owner_type, request.owner_id)
    if not isinstance(provider_result, list):
        raise TypeError("Form provider returned an invalid forms collection")

    all_forms = provider_result
    completed = [form for form in all_forms if form["status"] == "completed"]
    in_progress = [form for form in all_forms if form["status"] == "in_progress"]

    grouped_forms: dict[str, list[FormRecord]] = defaultdict(list)
    for form in completed:
        grouped_forms[form["form_category"]].append(form)

    ordered_groups = {
        category: sorted(forms, key=_completed_date)
        for category, forms in grouped_forms.items()
    }
    completed_dates = [_completed_date(form) for form in completed]
    audit_metadata: dict[str, Any] = {
        "owner_type": request.owner_type.value,
        "owner_id": request.owner_id,
        "total_forms": len(all_forms),
        "completed_forms": len(completed),
        "in_progress_forms": len(in_progress),
        "date_range_start": min(completed_dates) if completed_dates else None,
        "date_range_end": max(completed_dates) if completed_dates else None,
    }

    system_prompt, user_prompt = build_combined_form_prompt(
        audit_metadata, ordered_groups
    )
    narrative = await call_groq(system_prompt, user_prompt)
    parsed_sections = parse_summary_object(narrative)

    return CombinedFormSummaryResponse(
        owner_id=request.owner_id,
        owner_type=request.owner_type,
        generated_at=datetime.now(UTC),
        total_forms=len(all_forms),
        completed_forms=len(completed),
        in_progress_forms=len(in_progress),
        date_range_start=audit_metadata["date_range_start"],
        date_range_end=audit_metadata["date_range_end"],
        executive_synthesis=parsed_sections.get("Executive Synthesis", ""),
        group_summaries=[
            FormGroupSummary(
                form_category=category,
                submission_count=len(forms),
                is_trend=len(forms) > 1,
                summary_text=parsed_sections.get(category, ""),
            )
            for category, forms in ordered_groups.items()
        ],
    )
