from datetime import datetime

from sqlalchemy import (
    Integer, ForeignKey, BigInteger, DateTime, Enum, String, Text
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, make_timestamp_mixin
from .enums import ReminderStatusEnum


class Reminder(Base, make_timestamp_mixin()):
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

    user = relationship("User", back_populates="reminders")
    task = relationship("Task", back_populates="reminders")
    recurrence_rules = relationship(
        "RecurrenceRule", back_populates="reminders"
    )


class ActivityLog(Base, make_timestamp_mixin(include_updated=False)):
    __tablename__ = "activity_logs"

    log_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("users.telegram_id", ondelete="SET NULL"),
        nullable=True,
    )
    task_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("tasks.task_id", ondelete="SET NULL"),
        nullable=True,
    )
    list_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("lists.list_id", ondelete="SET NULL"),
        nullable=True,
    )
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    old_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    extra: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    success: Mapped[bool] = mapped_column(default=False, nullable=False)

    user = relationship(
        "User", back_populates="activity_logs"
    )
    tasklist = relationship(
        "TaskList", back_populates="activity_logs"
    )
    task = relationship(
        "Task", back_populates="activity_logs"
    )


class RecurrenceRule(Base, make_timestamp_mixin()):
    __tablename__ = "recurrence_rules"

    rule_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    frequency: Mapped[str | None] = mapped_column(String(20), nullable=True)
    interval: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pattern: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    tasks = relationship(
        "Task", back_populates="recurrence_rules"
    )
    reminders = relationship(
        "Reminder", back_populates="recurrence_rules"
    )
