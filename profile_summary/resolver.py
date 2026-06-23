from collections.abc import Iterable

from profile_summary.config import PROFILE_SECTIONS
from profile_summary.schemas import ProfileType


def resolve_sections(
    profile_type: ProfileType, user_permissions: Iterable[str]
) -> list[str]:
    """Keep configured section order while applying the permission allow-list."""

    allowed = set(user_permissions)
    return [
        section
        for section in PROFILE_SECTIONS[profile_type]
        if section in allowed
    ]
