from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.exam import Exam
from app.models.subject import Subject
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.exam_schema import ExamCreate, ExamResponse, ExamUpdate


router = APIRouter(
    prefix="/api/exams",
    tags=["Exams"],
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


def get_exam_for_current_user(
    db: Session,
    exam_id: int,
    user_id: int,
) -> tuple[Exam, Subject]:
    result = db.execute(
        select(Exam, Subject)
        .join(Subject, Exam.subject_id == Subject.id)
        .where(
            Exam.id == exam_id,
            Subject.user_id == user_id,
        )
    ).first()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy lịch thi.",
        )

    exam, subject = result
    return exam, subject


def get_days_remaining(exam_datetime: datetime) -> int:
    seconds = (exam_datetime - datetime.now()).total_seconds()
    days = seconds / 86400

    if days > 0:
        return max(0, int(days) + (1 if days % 1 > 0 else 0))

    return int(days)


def get_time_status(exam_datetime: datetime) -> str:
    days = get_days_remaining(exam_datetime)

    if exam_datetime < datetime.now():
        return "PAST"

    if days == 0:
        return "TODAY"

    if days <= 7:
        return "SOON"

    return "UPCOMING"


def exam_to_response(exam: Exam, subject: Subject) -> ExamResponse:
    return ExamResponse(
        id=exam.id,
        subject_id=exam.subject_id,
        subject_name=subject.name,
        title=exam.title,
        exam_type=exam.exam_type,
        exam_datetime=exam.exam_datetime,
        location=exam.location,
        note=exam.note,
        days_remaining=get_days_remaining(exam.exam_datetime),
        time_status=get_time_status(exam.exam_datetime),
        created_at=exam.created_at,
        updated_at=exam.updated_at,
    )


@router.get("", response_model=list[ExamResponse])
def get_exams(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = db.execute(
        select(Exam, Subject)
        .join(Subject, Exam.subject_id == Subject.id)
        .where(Subject.user_id == current_user.id)
        .order_by(Exam.exam_datetime.asc())
    ).all()

    return [
        exam_to_response(exam, subject)
        for exam, subject in rows
    ]


@router.post(
    "",
    response_model=ExamResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_exam(
    data: ExamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    subject = get_subject_for_current_user(
        db=db,
        subject_id=data.subject_id,
        user_id=current_user.id,
    )

    exam = Exam(
        subject_id=subject.id,
        title=data.title.strip(),
        exam_type=clean_optional_text(data.exam_type) or "Cuối kỳ",
        exam_datetime=data.exam_datetime,
        location=clean_optional_text(data.location),
        note=clean_optional_text(data.note),
    )

    db.add(exam)
    db.commit()
    db.refresh(exam)

    return exam_to_response(exam, subject)


@router.put("/{exam_id}", response_model=ExamResponse)
def update_exam(
    exam_id: int,
    data: ExamUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    exam, _old_subject = get_exam_for_current_user(
        db=db,
        exam_id=exam_id,
        user_id=current_user.id,
    )

    new_subject = get_subject_for_current_user(
        db=db,
        subject_id=data.subject_id,
        user_id=current_user.id,
    )

    exam.subject_id = new_subject.id
    exam.title = data.title.strip()
    exam.exam_type = clean_optional_text(data.exam_type) or "Cuối kỳ"
    exam.exam_datetime = data.exam_datetime
    exam.location = clean_optional_text(data.location)
    exam.note = clean_optional_text(data.note)

    db.commit()
    db.refresh(exam)

    return exam_to_response(exam, new_subject)


@router.delete("/{exam_id}")
def delete_exam(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    exam, _subject = get_exam_for_current_user(
        db=db,
        exam_id=exam_id,
        user_id=current_user.id,
    )

    db.delete(exam)
    db.commit()

    return {
        "message": "Xóa lịch thi thành công.",
    }