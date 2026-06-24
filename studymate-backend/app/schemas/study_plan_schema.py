from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, Field

from app.models.study_plan import StudyPlanStatus


class StudyPlanCreate(BaseModel):
    subject_id: int
    task_id: int | None = None
    title: str = Field(min_length=1, max_length=255)
    content: str | None = None
    study_date: date
    start_time: time | None = None
    duration_minutes: int = Field(default=60, gt=0)
    status: StudyPlanStatus = StudyPlanStatus.CHUA_THUC_HIEN


class StudyPlanUpdate(BaseModel):
    subject_id: int
    task_id: int | None = None
    title: str = Field(min_length=1, max_length=255)
    content: str | None = None
    study_date: date
    start_time: time | None = None
    duration_minutes: int = Field(default=60, gt=0)
    status: StudyPlanStatus = StudyPlanStatus.CHUA_THUC_HIEN


class StudyPlanStatusUpdate(BaseModel):
    status: StudyPlanStatus


class StudyPlanResponse(BaseModel):
    id: int
    subject_id: int
    subject_name: str
    task_id: int | None = None
    task_title: str | None = None
    title: str
    content: str | None = None
    study_date: date
    start_time: time | None = None
    duration_minutes: int
    status: StudyPlanStatus
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
