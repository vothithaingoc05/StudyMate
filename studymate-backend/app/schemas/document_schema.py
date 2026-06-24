from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DocumentCreate(BaseModel):
    subject_id: int
    title: str = Field(min_length=1, max_length=255)
    source_type: str = Field(default="TEXT", max_length=50)
    file_name: str | None = Field(default=None, max_length=255)
    file_path: str | None = Field(default=None, max_length=500)
    source_url: str | None = Field(default=None, max_length=500)
    content: str = Field(min_length=1)
    summary: str | None = None
    keywords: str | None = None
    relevance_score: float | None = None


class DocumentUpdate(BaseModel):
    subject_id: int
    title: str = Field(min_length=1, max_length=255)
    source_type: str = Field(default="TEXT", max_length=50)
    file_name: str | None = Field(default=None, max_length=255)
    file_path: str | None = Field(default=None, max_length=500)
    source_url: str | None = Field(default=None, max_length=500)
    content: str = Field(min_length=1)
    summary: str | None = None
    keywords: str | None = None
    relevance_score: float | None = None


class DocumentResponse(BaseModel):
    id: int
    subject_id: int
    subject_name: str
    title: str
    source_type: str
    file_name: str | None = None
    file_path: str | None = None
    source_url: str | None = None
    content: str
    summary: str | None = None
    keywords: str | None = None
    relevance_score: float | None = None
    processing_status: str
    chunks: list[str]
    word_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)