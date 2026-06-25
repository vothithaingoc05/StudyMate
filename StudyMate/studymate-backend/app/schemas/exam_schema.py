from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ExamCreate(BaseModel):
    subject_id: int
    title: str = Field(min_length=1, max_length=255)
    exam_type: str | None = Field(default="Cuối kỳ", max_length=50)
    exam_datetime: datetime
    location: str | None = Field(default=None, max_length=255)
    note: str | None = None


class ExamUpdate(BaseModel):
    subject_id: int
    title: str = Field(min_length=1, max_length=255)
    exam_type: str | None = Field(default="Cuối kỳ", max_length=50)
    exam_datetime: datetime
    location: str | None = Field(default=None, max_length=255)
    note: str | None = None


class ExamResponse(BaseModel):
    id: int
    subject_id: int
    subject_name: str
    title: str
    exam_type: str | None = None
    exam_datetime: datetime
    location: str | None = None
    note: str | None = None
    days_remaining: int
    time_status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)