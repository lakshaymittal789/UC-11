from profile_summary.schemas import ProfileType


PROFILE_SECTIONS: dict[ProfileType, list[str]] = {
    ProfileType.CLIENT: [
        "profile",
        "health_updates",
        "schedule",
        "care_plan",
        "medications",
        "goals",
        "authorizations",
        "invoices",
        "forms",
        "documents",
    ],
    ProfileType.CAREGIVER: [
        "profile",
        "schedule_visit_activity",
        "client_ratings",
        "compliance",
        "skills_restrictions",
        "compatibility",
        "forms",
        "documents",
    ],
    ProfileType.FACILITY: [
        "profile",
        "updates",
        "schedule",
        "authorizations",
        "invoices",
        "forms",
        "documents",
    ],
}
