from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db

from app.models.study_plan import StudyPlan, StudyPlanStatus
from app.models.subject import Subject
from app.models.task import Task
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.study_plan_schema import (
    StudyPlanCreate,
    StudyPlanResponse,
    StudyPlanStatusUpdate,
    StudyPlanUpdate,
)


router = APIRouter(
    prefix="/api/study-plans",
    tags=["Study Plans"],
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
    task_id: int | None,
    user_id: int,
) -> Task | None:
    if task_id is None:
        return None

    result = db.execute(
        select(Task)
        .join(Subject, Task.subject_id == Subject.id)
        .where(
            Task.id == task_id,
            Subject.user_id == user_id,
        )
    ).scalar_one_or_none()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy bài tập liên quan.",
        )

    return result


def get_study_plan_for_current_user(
    db: Session,
    plan_id: int,
    user_id: int,

) -> tuple[StudyPlan, Subject, Task | None]:
    result = db.execute(
        select(StudyPlan, Subject, Task)
        .join(Subject, StudyPlan.subject_id == Subject.id)
        .outerjoin(Task, StudyPlan.task_id == Task.id)
        .where(
            StudyPlan.id == plan_id,
            Subject.user_id == user_id,
        )

    ).first()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy kế hoạch học.",
        )

    plan, subject, task = result
    return plan, subject, task


def plan_to_response(
    plan: StudyPlan,
    subject: Subject,
    task: Task | None = None,
) -> StudyPlanResponse:
    return StudyPlanResponse(
        id=plan.id,
        subject_id=plan.subject_id,
        subject_name=subject.name,
        task_id=plan.task_id,
        task_title=task.title if task else None,
        title=plan.title,
        content=plan.content,
        study_date=plan.study_date,
        start_time=plan.start_time,
        duration_minutes=plan.duration_minutes,
        status=plan.status,
        completed_at=plan.completed_at,
        created_at=plan.created_at,
        updated_at=plan.updated_at,
    )


@router.get("", response_model=list[StudyPlanResponse])
def get_study_plans(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    rows = db.execute(
        select(StudyPlan, Subject, Task)
        .join(Subject, StudyPlan.subject_id == Subject.id)
        .outerjoin(Task, StudyPlan.task_id == Task.id)
        .where(Subject.user_id == current_user.id)
        .order_by(StudyPlan.study_date.asc(), StudyPlan.start_time.asc())
    ).all()


    return [
        plan_to_response(plan, subject, task)
        for plan, subject, task in rows
    ]



@router.post(
    "",
    response_model=StudyPlanResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_study_plan(
    data: StudyPlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    subject = get_subject_for_current_user(
        db=db,
        subject_id=data.subject_id,
        user_id=current_user.id,
    )


    task = get_task_for_current_user(
        db=db,
        task_id=data.task_id,
        user_id=current_user.id,
    )

    if task and task.subject_id != subject.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bài tập không thuộc môn học đã chọn.",
        )

    completed_at = (
        datetime.now()
        if data.status == StudyPlanStatus.DA_HOAN_THANH
        else None
    )


    plan = StudyPlan(
        subject_id=subject.id,
        task_id=task.id if task else None,
        title=data.title.strip(),
        content=clean_optional_text(data.content),
        study_date=data.study_date,
        start_time=data.start_time,
        duration_minutes=data.duration_minutes,
        status=data.status,
        completed_at=completed_at,
    )

    db.add(plan)
    db.commit()
    db.refresh(plan)

    return plan_to_response(plan, subject, task)


@router.put("/{plan_id}", response_model=StudyPlanResponse)
def update_study_plan(
    plan_id: int,
    data: StudyPlanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    plan, _old_subject, _old_task = get_study_plan_for_current_user(
        db=db,
        plan_id=plan_id,
        user_id=current_user.id,
    )


    subject = get_subject_for_current_user(
        db=db,
        subject_id=data.subject_id,
        user_id=current_user.id,
    )


    task = get_task_for_current_user(
        db=db,
        task_id=data.task_id,
        user_id=current_user.id,
    )

    if task and task.subject_id != subject.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bài tập không thuộc môn học đã chọn.",
        )

    old_status = plan.status

    plan.subject_id = subject.id
    plan.task_id = task.id if task else None
    plan.title = data.title.strip()
    plan.content = clean_optional_text(data.content)
    plan.study_date = data.study_date
    plan.start_time = data.start_time
    plan.duration_minutes = data.duration_minutes
    plan.status = data.status

    if data.status == StudyPlanStatus.DA_HOAN_THANH and old_status != StudyPlanStatus.DA_HOAN_THANH:
        plan.completed_at = datetime.now()
    elif data.status != StudyPlanStatus.DA_HOAN_THANH:
        plan.completed_at = None

    db.commit()
    db.refresh(plan)

    return plan_to_response(plan, subject, task)


@router.patch("/{plan_id}/status", response_model=StudyPlanResponse)
def update_study_plan_status(
    plan_id: int,
    data: StudyPlanStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    plan, subject, task = get_study_plan_for_current_user(
        db=db,
        plan_id=plan_id,
        user_id=current_user.id,
    )

    old_status = plan.status
    plan.status = data.status

    if data.status == StudyPlanStatus.DA_HOAN_THANH and old_status != StudyPlanStatus.DA_HOAN_THANH:
        plan.completed_at = datetime.now()
    elif data.status != StudyPlanStatus.DA_HOAN_THANH:
        plan.completed_at = None

    db.commit()
    db.refresh(plan)
    return plan_to_response(plan, subject, task)


@router.delete("/{plan_id}")
def delete_study_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    plan, _subject, _task = get_study_plan_for_current_user(
        db=db,
        plan_id=plan_id,
        user_id=current_user.id,
    )


    db.delete(plan)
    db.commit()

    return {
        "message": "Xóa kế hoạch học thành công.",
    }

