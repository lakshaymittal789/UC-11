OFFICE_NOTES_PERMISSION = "view_office_notes"


def user_can_view_office_notes(user_permissions: list[str]) -> bool:
    return OFFICE_NOTES_PERMISSION in user_permissions


def get_notes_user_permissions() -> list[str]:
    """Temporary dependency stub; replace with permissions from real RBAC."""

    return [OFFICE_NOTES_PERMISSION]
