import enum
from datetime import datetime

from sqlalchemy import (
    DateTime, func, Integer, ForeignKey, BigInteger, Enum, String, Text
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, relationship
)

from database.models import User, TaskList, Task


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class GenderEnum(enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class LevelEnum(enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskStatusEnum(enum.Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"


class ReminderStatusEnum(enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    CANCELLED = "cancelled"


class AccessRoleEnum(enum.Enum):
    OWNER = "owner"
    EDITOR = "editor"
    VIEWER = "viewer"


class Reminder(TimestampMixin, Base):
    __tablename__ = "reminders"

    reminder_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.task_id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.telegram_id", ondelete="CASCADE"),
        nullable=False,
    )
    remind_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    recurrence_rule_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("recurrence_rules.rule_id", ondelete="SET NULL")
    )
    status: Mapped[ReminderStatusEnum] = mapped_column(
        Enum(ReminderStatusEnum),
        default=ReminderStatusEnum.PENDING,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    user: Mapped["User"] = relationship("User", back_populates="reminders")
    task: Mapped["Task"] = relationship("Task", back_populates="reminders")
    recurrence_rules: Mapped["RecurrenceRule"] = relationship(
        "RecurrenceRule", back_populates="reminders"
    )


class ActivityLog(TimestampMixin, Base):
    __tablename__ = "activity_logs"

    log_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.telegram_id"), nullable=True,
    )
    task_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("tasks.task_id"), nullable=True,
    )
    list_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("lists.list_id"), nullable=True,
    )
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    old_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    extra: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    user: Mapped["User"] = relationship(
        "User", back_populates="activity_logs"
    )
    tasklist: Mapped["TaskList"] = relationship(
        "TaskList", back_populates="activity_logs"
    )
    task: Mapped["Task"] = relationship(
        "Task", back_populates="activity_logs"
    )


class RecurrenceRule(TimestampMixin, Base):
    __tablename__ = "recurrence_rules"

    rule_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    frequency: Mapped[str | None] = mapped_column(String(20), nullable=True)
    interval: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pattern: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    tasks: Mapped[list["Task"]] = relationship(
        "Task", back_populates="recurrence_rules"
    )
    reminders: Mapped[list["Reminder"]] = relationship(
        "Reminder", back_populates="recurrence_rules"
    )
