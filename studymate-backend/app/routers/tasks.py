from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.subject import Subject
from app.models.task import Task, TaskStatus
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.task_schema import (
    TaskCreate,
    TaskResponse,
    TaskStatusUpdate,
    TaskUpdate,
)


router = APIRouter(
    prefix="/api/tasks",
    tags=["Tasks"],
)


def clean_optional_text(value: str | None) -> str | None:
    if value is None:
        return None

    cleaned_value = value.strip()
    return cleaned_value if cleaned_value else None


def get_subject_for_current_user(
    db: Session,
    subject_id: int,
    user_id: int,
) -> Subject:
    subject = db.scalar(
        select(Subject).where(
            Subject.id == subject_id,
            Subject.user_id == user_id,
        )
    )

    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy môn học của bạn.",
        )

    return subject


def get_task_for_current_user(
    db: Session,
    task_id: int,
    user_id: int,
) -> tuple[Task, Subject]:
    result = db.execute(
        select(Task, Subject)
        .join(Subject, Task.subject_id == Subject.id)
        .where(
            Task.id == task_id,
            Subject.user_id == user_id,
        )
    ).first()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy bài tập.",
        )

    task, subject = result
    return task, subject


def get_days_remaining(deadline: datetime) -> int:
    seconds = (deadline - datetime.now()).total_seconds()
    days = seconds / 86400

    if days > 0:
        return max(1, int(days) + (1 if days % 1 > 0 else 0))

    return int(days)


def calculate_priority(
    deadline: datetime,
    difficulty: int,
    importance: int,
    task_status: TaskStatus,
) -> tuple[float, str, str]:
    if task_status == TaskStatus.HOAN_THANH:
        return 0.0, "Đã hoàn thành", "completed"

    days = get_days_remaining(deadline)

    if days < 0:
        score = (importance * 2 + difficulty) * 10
        return round(score, 2), "Quá hạn", "overdue"

    score = (importance * 2 + difficulty) / max(days, 1)

    if days <= 1:
        label = "Rất cao"
        class_name = "very-high"
    elif days <= 3:
        label = "Cao"
        class_name = "high"
    elif score >= 2:
        label = "Trung bình"
        class_name = "medium"
    else:
        label = "Thấp"
        class_name = "low"

    return round(score, 2), label, class_name


def task_to_response(task: Task, subject: Subject) -> TaskResponse:
    score, label, class_name = calculate_priority(
        deadline=task.deadline,
        difficulty=task.difficulty,
        importance=task.importance,
        task_status=task.status,
    )

    return TaskResponse(
        id=task.id,
        subject_id=task.subject_id,
        subject_name=subject.name,
        title=task.title,
        description=task.description,
        deadline=task.deadline,
        difficulty=task.difficulty,
        importance=task.importance,
        status=task.status,
        completed_at=task.completed_at,
        priority_score=score,
        priority_label=label,
        priority_class=class_name,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


@router.get("", response_model=list[TaskResponse])
def get_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = db.execute(
        select(Task, Subject)
        .join(Subject, Task.subject_id == Subject.id)
        .where(Subject.user_id == current_user.id)
        .order_by(Task.deadline.asc())
    ).all()

    results = [
        task_to_response(task, subject)
        for task, subject in rows
    ]

    return sorted(
        results,
        key=lambda task: task.priority_score,
        reverse=True,
    )


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    subject = get_subject_for_current_user(
        db=db,
        subject_id=data.subject_id,
        user_id=current_user.id,
    )

    completed_at = datetime.now() if data.status == TaskStatus.HOAN_THANH else None

    task = Task(
        subject_id=subject.id,
        title=data.title.strip(),
        description=clean_optional_text(data.description),
        deadline=data.deadline,
        difficulty=data.difficulty,
        importance=data.importance,
        status=data.status,
        completed_at=completed_at,
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task_to_response(task, subject)


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task, _old_subject = get_task_for_current_user(
        db=db,
        task_id=task_id,
        user_id=current_user.id,
    )

    new_subject = get_subject_for_current_user(
        db=db,
        subject_id=data.subject_id,
        user_id=current_user.id,
    )

    old_status = task.status

    task.subject_id = new_subject.id
    task.title = data.title.strip()
    task.description = clean_optional_text(data.description)
    task.deadline = data.deadline
    task.difficulty = data.difficulty
    task.importance = data.importance
    task.status = data.status

    if data.status == TaskStatus.HOAN_THANH and old_status != TaskStatus.HOAN_THANH:
        task.completed_at = datetime.now()
    elif data.status != TaskStatus.HOAN_THANH:
        task.completed_at = None

    db.commit()
    db.refresh(task)

    return task_to_response(task, new_subject)


@router.patch("/{task_id}/status", response_model=TaskResponse)
def update_task_status(
    task_id: int,
    data: TaskStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task, subject = get_task_for_current_user(
        db=db,
        task_id=task_id,
        user_id=current_user.id,
    )

    old_status = task.status
    task.status = data.status

    if data.status == TaskStatus.HOAN_THANH and old_status != TaskStatus.HOAN_THANH:
        task.completed_at = datetime.now()
    elif data.status != TaskStatus.HOAN_THANH:
        task.completed_at = None

    db.commit()
    db.refresh(task)

    return task_to_response(task, subject)


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task, _subject = get_task_for_current_user(
        db=db,
        task_id=task_id,
        user_id=current_user.id,
    )

    db.delete(task)
    db.commit()

    return {
        "message": "Xóa bài tập thành công.",
    }