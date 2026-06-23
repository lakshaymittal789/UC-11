from datetime import date, datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


class ProfileType(StrEnum):
    CLIENT = "client"
    CAREGIVER = "caregiver"
    FACILITY = "facility"


class ProfileSummaryRequest(BaseModel):
    profile_type: ProfileType
    profile_id: str = Field(min_length=1)
    requesting_user_id: str = Field(min_length=1)


class SectionData(BaseModel):
    section_name: str
    data: dict[str, Any]
    is_empty: bool


class ProfileSummaryResponse(BaseModel):
    profile_id: str
    profile_type: ProfileType
    generated_at: datetime
    sources: list[str]
    summary_text: dict[str, str]


class ProfileDataResponse(BaseModel):
    profile_id: str
    profile_type: ProfileType
    sections: list[SectionData]


class FormOwnerType(StrEnum):
    CLIENT = "client"
    PROSPECTIVE_CLIENT = "prospective_client"
    CAREGIVER = "caregiver"
    APPLICANT = "applicant"


class CombinedFormSummaryRequest(BaseModel):
    owner_type: FormOwnerType
    owner_id: str = Field(min_length=1)
    requesting_user_id: str = Field(min_length=1)


class SingleFormSummaryRequest(BaseModel):
    requesting_user_id: str = Field(min_length=1)


class FormGroupSummary(BaseModel):
    form_category: str
    submission_count: int
    is_trend: bool
    summary_text: str


class CombinedFormSummaryResponse(BaseModel):
    owner_id: str
    owner_type: FormOwnerType
    generated_at: datetime
    total_forms: int
    completed_forms: int
    in_progress_forms: int
    date_range_start: date | None
    date_range_end: date | None
    executive_synthesis: str
    group_summaries: list[FormGroupSummary]


class SingleFormSummaryResponse(BaseModel):
    form_id: str
    is_fixed: bool
    generated_at: datetime
    summary_text: dict[str, str]


class NoteType(StrEnum):
    CARE = "care"
    FAMILY = "family"
    OFFICE = "office"


class TimeFilter(StrEnum):
    LAST_30 = "last_30"
    LAST_60 = "last_60"
    LAST_90 = "last_90"
    CUSTOM = "custom"


class NotesSummaryRequest(BaseModel):
    client_id: str = Field(min_length=1)
    requesting_user_id: str = Field(min_length=1)
    time_filter: TimeFilter
    custom_start: date | None = None
    custom_end: date | None = None
    include_care_notes: bool = True
    include_care_published: bool = True
    include_care_unpublished: bool = True
    include_family_notes: bool = True
    include_family_published: bool = True
    include_family_unpublished: bool = True
    include_office_notes: bool = False

    @model_validator(mode="after")
    def validate_custom_range(self) -> "NotesSummaryRequest":
        if self.time_filter is TimeFilter.CUSTOM:
            if self.custom_start is None or self.custom_end is None:
                raise ValueError(
                    "custom_start and custom_end are required for a custom range"
                )
            if self.custom_start > self.custom_end:
                raise ValueError("custom_start cannot be after custom_end")
        return self


class NotesSummarySection(BaseModel):
    header: str
    text: str


class NotesSummaryResponse(BaseModel):
    client_id: str
    context_line: str
    sections: dict[str, str]
    includes_office_notes: bool
    generated_at: datetime


class NotesSaveRequest(BaseModel):
    client_id: str = Field(min_length=1)
    sections: dict[str, str]
    context_line: str
    date_range_start: date
    date_range_end: date
    includes_office_notes: bool
    generated_by: str = Field(min_length=1)


class NotesSaveResponse(BaseModel):
    note_id: str
    status: Literal["unpublished", "internal_staff_only"]
    saved_at: datetime


class PublishRequest(BaseModel):
    requesting_user_id: str = Field(min_length=1)


class PublishResponse(BaseModel):
    note_id: str
    status: Literal["published"]
    published_at: datetime
