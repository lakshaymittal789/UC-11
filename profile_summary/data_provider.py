from abc import ABC, abstractmethod
from typing import Any

from profile_summary.schemas import FormOwnerType, ProfileType

SectionPayload = dict[str, Any]
FormRecord = dict[str, Any]
NoteRecord = dict[str, Any]


class ProfileDataProvider(ABC):
    """Interface for profile data sources such as a CRM, database, or mock."""

    @abstractmethod
    async def get_profile_info(
        self, profile_type: ProfileType, profile_id: str
    ) -> SectionPayload:
        pass

    @abstractmethod
    async def get_notes(
        self, owner_type: ProfileType | str, owner_id: str
    ) -> SectionPayload | list[NoteRecord]:
        pass

    @abstractmethod
    async def get_note_by_id(self, note_id: str) -> NoteRecord | None:
        pass

    @abstractmethod
    async def save_note(self, note: NoteRecord) -> NoteRecord:
        pass

    @abstractmethod
    async def update_note(
        self, note_id: str, updates: dict[str, Any]
    ) -> NoteRecord | None:
        pass

    @abstractmethod
    async def get_schedule(
        self, profile_type: ProfileType, profile_id: str
    ) -> SectionPayload:
        pass

    @abstractmethod
    async def get_care_plan(
        self, profile_type: ProfileType, profile_id: str
    ) -> SectionPayload:
        pass

    @abstractmethod
    async def get_authorizations(
        self, profile_type: ProfileType, profile_id: str
    ) -> SectionPayload:
        pass

    @abstractmethod
    async def get_invoices(
        self, profile_type: ProfileType, profile_id: str
    ) -> SectionPayload:
        pass

    @abstractmethod
    async def get_forms(
        self,
        owner_type: ProfileType | FormOwnerType,
        owner_id: str,
    ) -> SectionPayload | list[FormRecord]:
        pass

    @abstractmethod
    async def get_form_by_id(self, form_id: str) -> FormRecord | None:
        pass

    @abstractmethod
    async def get_documents(
        self, profile_type: ProfileType, profile_id: str
    ) -> SectionPayload:
        pass

    @abstractmethod
    async def get_compliance(
        self, profile_type: ProfileType, profile_id: str
    ) -> SectionPayload:
        pass

    @abstractmethod
    async def get_skills(
        self, profile_type: ProfileType, profile_id: str
    ) -> SectionPayload:
        pass

    @abstractmethod
    async def get_compatibility(
        self, profile_type: ProfileType, profile_id: str
    ) -> SectionPayload:
        pass

    @abstractmethod
    async def get_medications(
        self, profile_type: ProfileType, profile_id: str
    ) -> SectionPayload:
        pass

    @abstractmethod
    async def get_goals(
        self, profile_type: ProfileType, profile_id: str
    ) -> SectionPayload:
        pass

    @abstractmethod
    async def get_ratings(
        self, profile_type: ProfileType, profile_id: str
    ) -> SectionPayload:
        pass
