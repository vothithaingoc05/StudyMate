from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class TaskStatus(str, Enum):
    CHUA_LAM = "CHUA_LAM"
    DANG_LAM = "DANG_LAM"
    HOAN_THANH = "HOAN_THANH"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    subject_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("subjects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    deadline: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        index=True,
    )

    difficulty: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    importance: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    status: Mapped[TaskStatus] = mapped_column(
        SQLEnum(
            TaskStatus,
            values_callable=lambda enum_class: [item.value for item in enum_class],
        ),
        nullable=False,
        default=TaskStatus.CHUA_LAM,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )