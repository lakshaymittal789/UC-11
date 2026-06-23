import json
from typing import Any


def build_notes_prompt(
    filtered_notes_by_type: dict[str, list[dict[str, Any]]],
) -> tuple[str, str]:
    system_prompt = (
        "You are summarizing case notes for a home care client. Return ONLY one "
        "valid JSON object with keys in this order when their note type is present: "
        "`Clinical & Care Observations` for care notes, `Family Communications` for "
        "family notes, and `Administrative Updates` for office notes. Never include "
        "a key with no supporting notes. Each value must be one concise plain-text "
        "paragraph of 2-4 sentences, grounded strictly in the provided note content. "
        "Never fabricate dates, names, or details. Do not use markdown, bullets, or "
        "newline-delimited sections."
    )
    user_prompt = json.dumps(filtered_notes_by_type, indent=2, default=str)
    return system_prompt, user_prompt
