from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.task import TaskStatus


class TaskCreate(BaseModel):
    subject_id: int
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    deadline: datetime
    difficulty: int = Field(default=1, ge=1, le=5)
    importance: int = Field(default=1, ge=1, le=5)
    status: TaskStatus = TaskStatus.CHUA_LAM


class TaskUpdate(BaseModel):
    subject_id: int
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    deadline: datetime
    difficulty: int = Field(default=1, ge=1, le=5)
    importance: int = Field(default=1, ge=1, le=5)
    status: TaskStatus = TaskStatus.CHUA_LAM


class TaskStatusUpdate(BaseModel):
    status: TaskStatus


class TaskResponse(BaseModel):
    id: int
    subject_id: int
    subject_name: str
    title: str
    description: str | None = None
    deadline: datetime
    difficulty: int
    importance: int
    status: TaskStatus
    completed_at: datetime | None = None
    priority_score: float
    priority_label: str
    priority_class: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)