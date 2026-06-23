import json
import re
from typing import Any

MARKDOWN_HEADER = re.compile(
    r"^\s{0,3}#{1,6}\s+\*{0,2}(.+?)\*{0,2}\s*:?\s*$",
    re.MULTILINE,
)


def parse_summary_object(response_text: str) -> dict[str, str]:
    """Parse JSON output, tolerating code fences and legacy markdown."""

    cleaned = response_text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, count=1)
        cleaned = re.sub(r"\s*```$", "", cleaned, count=1)

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end > start:
        try:
            parsed: Any = json.loads(cleaned[start:end + 1])
            if isinstance(parsed, dict):
                return {
                    str(key): _stringify(value)
                    for key, value in parsed.items()
                    if value not in (None, "", [], {})
                }
        except json.JSONDecodeError:
            pass

    matches = list(MARKDOWN_HEADER.finditer(cleaned))
    return {
        match.group(1).strip().strip("*").rstrip(":").strip(): _stringify(
            cleaned[
                match.end():
                matches[index + 1].start() if index + 1 < len(matches) else None
            ].strip()
        )
        for index, match in enumerate(matches)
    }


def _stringify(value: Any) -> str:
    if isinstance(value, str):
        return " ".join(value.split())
    if isinstance(value, list):
        return " ".join(str(item).strip() for item in value if str(item).strip())
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)
    return str(value)
