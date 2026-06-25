from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SubjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    code: str | None = Field(default=None, max_length=30)
    semester: str | None = Field(default=None, max_length=30)
    academic_year: str | None = Field(default=None, max_length=20)
    description: str | None = None
    color: str | None = Field(default="#B9824C", max_length=20)


class SubjectUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    code: str | None = Field(default=None, max_length=30)
    semester: str | None = Field(default=None, max_length=30)
    academic_year: str | None = Field(default=None, max_length=20)
    description: str | None = None
    color: str | None = Field(default="#B9824C", max_length=20)


class SubjectResponse(BaseModel):
    id: int
    user_id: int
    name: str
    code: str | None = None
    semester: str | None = None
    academic_year: str | None = None
    description: str | None = None
    color: str | None = "#B9824C"
    has_documents: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)