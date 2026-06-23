import json
from typing import Any

FormRecord = dict[str, Any]


def _json(value: Any) -> str:
    return json.dumps(value, indent=2, default=str)


def build_combined_form_prompt(
    audit_metadata: dict[str, Any],
    grouped_forms: dict[str, list[FormRecord]],
) -> tuple[str, str]:
    system_prompt = (
        "You are auditing a complete set of forms on file for a home care agency "
        "record. First write one Executive Synthesis paragraph of 3-5 sentences "
        "evaluating milestones, consistent trends, or notable past issues. Then "
        "write one paragraph for each form group. For groups with multiple "
        "submissions, write an AI Comparison & Trend analysis comparing changes "
        "over time. For groups with one submission, "
        "write a direct concise summary. Ground every statement strictly in the "
        "provided data. Return ONLY one valid JSON object in this order: first the "
        "key `Executive Synthesis`, then one key matching each exact form_category. "
        "Every value must be a plain-text paragraph. Do not use markdown or newline "
        "section headers."
    )
    user_prompt = (
        "Audit metadata:\n"
        f"{_json(audit_metadata)}\n\n"
        "Grouped completed forms:\n"
        f"{_json(grouped_forms)}"
    )
    return system_prompt, user_prompt


def build_fixed_form_prompt(form: FormRecord) -> tuple[str, str]:
    system_prompt = (
        "This is a structured, system-generated form such as a Care Assessment. "
        "Return ONLY one valid JSON object using these keys in this order when data "
        "supports them: Overview, Care Needs Summary, Risk & Safety Highlights, "
        "Mobility & Functional Status, Medications, Care Plan / Activities, "
        "Important Notes. Skip unsupported keys. Each value must be a concise "
        "plain-text paragraph grounded in the provided field values. Never fabricate "
        "and do not use markdown."
    )
    return system_prompt, _json(form["responses_json"])


def build_custom_form_prompt(form: FormRecord) -> tuple[str, str]:
    system_prompt = (
        "This is a dynamic, agency-created custom form. Return ONLY one valid JSON "
        "object. Always include Overview and Key Findings first. Include only "
        "supported optional keys from: Care Needs, Risks / Concerns, Medications, "
        "Activities / Plan. Always end with Additional Notes. Each value must be a "
        "concise plain-text paragraph grounded strictly in the provided answers. "
        "Never fabricate and do not use markdown."
    )
    return system_prompt, _json(form["responses_json"])
