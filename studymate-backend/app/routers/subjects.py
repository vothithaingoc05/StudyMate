from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.subject import Subject
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.subject_schema import (
    SubjectCreate,
    SubjectResponse,
    SubjectUpdate,
)


router = APIRouter(
    prefix="/api/subjects",
    tags=["Subjects"],
)


def clean_optional_text(value: str | None) -> str | None:
    if value is None:
        return None

    cleaned_value = value.strip()
    return cleaned_value if cleaned_value else None


def subject_to_response(subject: Subject) -> SubjectResponse:
    return SubjectResponse(
        id=subject.id,
        user_id=subject.user_id,
        name=subject.name,
        code=subject.code,
        semester=subject.semester,
        academic_year=subject.academic_year,
        description=subject.description,
        color=subject.color or "#B9824C",
        has_documents=False,
        created_at=subject.created_at,
        updated_at=subject.updated_at,
    )


def check_duplicate_subject(
    db: Session,
    user_id: int,
    name: str,
    semester: str | None,
    academic_year: str | None,
    ignored_subject_id: int | None = None,
) -> None:
    statement = select(Subject).where(
        Subject.user_id == user_id,
        func.lower(Subject.name) == name.lower(),
        Subject.semester == semester,
        Subject.academic_year == academic_year,
    )

    if ignored_subject_id is not None:
        statement = statement.where(Subject.id != ignored_subject_id)

    duplicated_subject = db.scalar(statement)

    if duplicated_subject:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Môn học này đã tồn tại trong cùng học kỳ và năm học.",
        )


@router.get("", response_model=list[SubjectResponse])
def get_subjects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    subjects = db.scalars(
        select(Subject)
        .where(Subject.user_id == current_user.id)
        .order_by(Subject.created_at.desc())
    ).all()

    return [subject_to_response(subject) for subject in subjects]


@router.post(
    "",
    response_model=SubjectResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_subject(
    data: SubjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    name = data.name.strip()
    semester = clean_optional_text(data.semester)
    academic_year = clean_optional_text(data.academic_year)

    check_duplicate_subject(
        db=db,
        user_id=current_user.id,
        name=name,
        semester=semester,
        academic_year=academic_year,
    )

    subject = Subject(
        user_id=current_user.id,
        name=name,
        code=clean_optional_text(data.code),
        semester=semester,
        academic_year=academic_year,
        description=clean_optional_text(data.description),
        color=data.color or "#B9824C",
    )

    db.add(subject)
    db.commit()
    db.refresh(subject)

    return subject_to_response(subject)


@router.put("/{subject_id}", response_model=SubjectResponse)
def update_subject(
    subject_id: int,
    data: SubjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    subject = db.scalar(
        select(Subject).where(
            Subject.id == subject_id,
            Subject.user_id == current_user.id,
        )
    )

    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy môn học.",
        )

    name = data.name.strip()
    semester = clean_optional_text(data.semester)
    academic_year = clean_optional_text(data.academic_year)

    check_duplicate_subject(
        db=db,
        user_id=current_user.id,
        name=name,
        semester=semester,
        academic_year=academic_year,
        ignored_subject_id=subject.id,
    )

    subject.name = name
    subject.code = clean_optional_text(data.code)
    subject.semester = semester
    subject.academic_year = academic_year
    subject.description = clean_optional_text(data.description)
    subject.color = data.color or "#B9824C"

    db.commit()
    db.refresh(subject)

    return subject_to_response(subject)


@router.delete("/{subject_id}")
def delete_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    subject = db.scalar(
        select(Subject).where(
            Subject.id == subject_id,
            Subject.user_id == current_user.id,
        )
    )

    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy môn học.",
        )

    db.delete(subject)
    db.commit()

    return {
        "message": "Xóa môn học thành công.",
    }