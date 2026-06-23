from typing import Any

from profile_summary.data_provider import (
    FormRecord,
    NoteRecord,
    ProfileDataProvider,
    SectionPayload,
)
from profile_summary.forms_dummy_data import FORMS
from profile_summary.notes_dummy_data import NOTES
from profile_summary.schemas import FormOwnerType, ProfileType


class DummyDataProvider(ProfileDataProvider):
    """Deterministic mock data suitable for local development and tests."""

    @staticmethod
    def _seed(profile_id: str) -> int:
        return sum(ord(character) for character in profile_id)

    @staticmethod
    def _name(profile_type: ProfileType, profile_id: str) -> str:
        labels = {
            ProfileType.CLIENT: "Client",
            ProfileType.CAREGIVER: "Caregiver",
            ProfileType.FACILITY: "Facility",
        }
        return f"{labels[profile_type]} {profile_id.upper()}"

    async def get_profile_info(
        self, profile_type: ProfileType, profile_id: str
    ) -> SectionPayload:
        common: dict[str, Any] = {
            "id": profile_id,
            "name": self._name(profile_type, profile_id),
            "status": "active",
        }
        details = {
            ProfileType.CLIENT: {
                "date_of_birth": "1948-04-12",
                "primary_contact": "Jordan Morgan",
                "preferred_language": "English",
            },
            ProfileType.CAREGIVER: {
                "role": "Home Health Aide",
                "hire_date": "2022-08-15",
                "service_area": "North District",
            },
            ProfileType.FACILITY: {
                "facility_type": "Assisted Living",
                "capacity": 72,
                "primary_contact": "Alex Rivera",
            },
        }
        return common | details[profile_type]

    async def get_notes(
        self, owner_type: ProfileType | str, owner_id: str
    ) -> SectionPayload | list[NoteRecord]:
        if not isinstance(owner_type, ProfileType):
            return [
                dict(note)
                for note in NOTES
                if note["owner_type"] == owner_type
                and note["owner_id"] == owner_id
            ]

        if owner_type is ProfileType.CAREGIVER:
            return {}
        note = (
            "Mobility and appetite are stable; continue monitoring."
            if owner_type is ProfileType.CLIENT
            else "New memory-care wing onboarding is on schedule."
        )
        return {
            "latest_update": note,
            "updated_at": "2026-06-20T09:30:00Z",
            "profile_id": owner_id,
        }

    async def get_note_by_id(self, note_id: str) -> NoteRecord | None:
        return next(
            (dict(note) for note in NOTES if note["id"] == note_id),
            None,
        )

    async def save_note(self, note: NoteRecord) -> NoteRecord:
        stored_note = dict(note)
        NOTES.append(stored_note)
        return dict(stored_note)

    async def update_note(
        self, note_id: str, updates: dict[str, Any]
    ) -> NoteRecord | None:
        for note in NOTES:
            if note["id"] == note_id:
                note.update(updates)
                return dict(note)
        return None

    async def get_schedule(
        self, profile_type: ProfileType, profile_id: str
    ) -> SectionPayload:
        if profile_type is ProfileType.CAREGIVER:
            return {
                "next_visit": "2026-06-23T08:00:00Z",
                "weekly_visits": 5,
                "completed_visits_this_month": 18 + self._seed(profile_id) % 4,
                "late_arrivals_this_month": 0,
            }
        return {
            "next_visit": "2026-06-23T10:00:00Z",
            "assigned_caregiver": f"Caregiver CG-{self._seed(profile_id) % 100:02d}",
            "visits_this_week": 4,
        }

    async def get_care_plan(
        self, profile_type: ProfileType, profile_id: str
    ) -> SectionPayload:
        if profile_type is not ProfileType.CLIENT:
            return {}
        return {
            "plan_id": f"CP-{profile_id}",
            "level_of_care": "Moderate assistance",
            "review_due": "2026-07-15",
            "tasks": ["mobility support", "meal preparation", "vital checks"],
        }

    async def get_authorizations(
        self, profile_type: ProfileType, profile_id: str
    ) -> SectionPayload:
        if profile_type is ProfileType.CAREGIVER:
            return {}
        return {
            "authorization_id": f"AUTH-{profile_id}",
            "status": "approved",
            "approved_hours": 120,
            "remaining_hours": 44,
            "valid_through": "2026-07-31",
        }

    async def get_invoices(
        self, profile_type: ProfileType, profile_id: str
    ) -> SectionPayload:
        if profile_type is ProfileType.CAREGIVER:
            return {}
        return {
            "open_balance": float(75 + self._seed(profile_id) % 200),
            "currency": "USD",
            "oldest_due_date": "2026-06-30",
            "invoice_count": 2,
        }

    async def get_forms(
        self,
        owner_type: ProfileType | FormOwnerType,
        owner_id: str,
    ) -> SectionPayload | list[FormRecord]:
        if isinstance(owner_type, FormOwnerType):
            return [
                dict(form)
                for form in FORMS
                if form["owner_type"] == owner_type.value
                and form["owner_id"] == owner_id
            ]

        return {
            "completed": 8 + self._seed(owner_id) % 5,
            "pending": 1,
            "next_required": "Quarterly review form",
        }

    async def get_form_by_id(self, form_id: str) -> FormRecord | None:
        return next(
            (dict(form) for form in FORMS if form["id"] == form_id),
            None,
        )

    async def get_documents(
        self, profile_type: ProfileType, profile_id: str
    ) -> SectionPayload:
        return {
            "document_count": 10 + self._seed(profile_id) % 9,
            "latest_document": "Profile verification.pdf",
            "latest_uploaded_at": "2026-06-18T14:10:00Z",
        }

    async def get_compliance(
        self, profile_type: ProfileType, profile_id: str
    ) -> SectionPayload:
        if profile_type is not ProfileType.CAREGIVER:
            return {}
        return {
            "profile_id": profile_id,
            "overall_status": "compliant",
            "background_check": "current",
            "cpr_expires": "2027-03-01",
            "training_completion_percent": 96,
        }

    async def get_skills(
        self, profile_type: ProfileType, profile_id: str
    ) -> SectionPayload:
        if profile_type is not ProfileType.CAREGIVER:
            return {}
        return {
            "profile_id": profile_id,
            "skills": ["dementia care", "mobility assistance", "meal preparation"],
            "restrictions": ["no heavy lifting over 40 lb"],
            "certifications": ["CPR", "First Aid"],
        }

    async def get_compatibility(
        self, profile_type: ProfileType, profile_id: str
    ) -> SectionPayload:
        if profile_type is not ProfileType.CAREGIVER:
            return {}
        return {
            "profile_id": profile_id,
            "preferred_shifts": ["morning", "weekday"],
            "languages": ["English", "Spanish"],
            "transportation": True,
            "pet_friendly": True,
        }

    async def get_medications(
        self, profile_type: ProfileType, profile_id: str
    ) -> SectionPayload:
        if profile_type is not ProfileType.CLIENT:
            return {}
        return {
            "profile_id": profile_id,
            "active_count": 3,
            "medications": [
                {"name": "Lisinopril", "schedule": "once daily"},
                {"name": "Metformin", "schedule": "twice daily"},
                {"name": "Vitamin D", "schedule": "once daily"},
            ],
            "medication_review_due": "2026-07-02",
        }

    async def get_goals(
        self, profile_type: ProfileType, profile_id: str
    ) -> SectionPayload:
        if profile_type is not ProfileType.CLIENT:
            return {}
        return {
            "profile_id": profile_id,
            "active_goals": [
                {"goal": "Walk 300 feet with assistance", "progress": "on_track"},
                {"goal": "Prepare one meal weekly", "progress": "improving"},
            ]
        }

    async def get_ratings(
        self, profile_type: ProfileType, profile_id: str
    ) -> SectionPayload:
        if profile_type is not ProfileType.CAREGIVER:
            return {}
        return {
            "profile_id": profile_id,
            "average_rating": round(4.5 + (self._seed(profile_id) % 5) / 10, 1),
            "rating_count": 24,
            "recent_feedback": "Dependable, attentive, and communicates clearly.",
        }
