from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    Integer,
    BigInteger,
    ForeignKey,
    Text,
    Enum,
    DateTime,
    func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin
from .enums import TaskStatusEnum, LevelEnum, AccessRoleEnum
from .support import Reminder, ActivityLog, RecurrenceRule
from .tag import TaskTags


class Task(TimestampMixin, Base):
    __tablename__ = "tasks"
    __table_args__ = (
        CheckConstraint("done_at IS NULL OR done_at >= created_at",
                        name="chk_done_after_created"),
        CheckConstraint("cancelled_at IS NULL OR cancelled_at >= created_at",
                        name="chk_cancelled_after_created"),
    )

    task_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    creator_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.telegram_id"), nullable=False
    )
    message_id: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[LevelEnum] = mapped_column(
        Enum(LevelEnum), nullable=False, default=LevelEnum.MEDIUM
    )
    urgency: Mapped[LevelEnum] = mapped_column(
        Enum(LevelEnum), nullable=False, default=LevelEnum.MEDIUM
    )
    status: Mapped[TaskStatusEnum] = mapped_column(
        Enum(TaskStatusEnum), nullable=False, default=TaskStatusEnum.NEW
    )
    is_shared: Mapped[bool] = mapped_column(default=False, nullable=False)
    owner_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.telegram_id"), nullable=False
    )
    parent_task_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("tasks.task_id", ondelete="CASCADE"),
    )
    deadline: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )
    done_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    cancelled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    postponed_count: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    is_recurring: Mapped[bool] = mapped_column(
        default=False, nullable=False
    )
    recurrence_rule_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("recurrence_rules.rule_id", ondelete="SET NULL")
    )
    duration: Mapped[int] = mapped_column(BigInteger, nullable=True)
    remind: Mapped[bool] = mapped_column(default=False, nullable=False)

    parent: Mapped["Task"] = relationship(
        "Task",
        remote_side=[task_id],
        back_populates="children",
        uselist=False
    )
    children: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="parent",
        cascade="all, delete-orphan"
    )
    user_lists: Mapped[list["UserTaskList"]] = relationship(
        "UserTaskList", back_populates="task", passive_deletes=True
    )
    reminders: Mapped[list["Reminder"]] = relationship(
        "Reminder", back_populates="task", passive_deletes=True
    )
    task_access: Mapped[list["TaskAccess"]] = relationship(
        "TaskAccess", back_populates="task", passive_deletes=True
    )
    activity_logs: Mapped[list["ActivityLog"]] = relationship(
        "ActivityLog", back_populates="task", passive_deletes=True
    )
    recurrence_rules: Mapped[list["RecurrenceRule"]] = relationship(
        "RecurrenceRule", back_populates="tasks", passive_deletes=True
    )
    tags: Mapped[list["TaskTags"]] = relationship(
        "TaskTags", back_populates="task", passive_deletes=True
    )

    def __repr__(self) -> str:
        return (f"<Task id={self.task_id} shared={self.is_shared} "
                f"status={self.status.value} text={self.text[:20]!r}>")


class UserTaskList(TimestampMixin, Base):
    __tablename__ = "user_task_lists"

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.telegram_id", ondelete="CASCADE"),
        primary_key=True,
    )
    list_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("lists.list_id", ondelete="CASCADE"),
        primary_key=True,
    )
    task_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tasks.task_id", ondelete="CASCADE"),
        primary_key=True,
    )
    is_owner: Mapped[bool] = mapped_column(default=True, nullable=False)

    user = relationship(
        "User", back_populates="task_lists",
    )
    tasklist = relationship(
        "TaskList", back_populates="user_tasks",
    )
    task = relationship(
        "Task", back_populates="user_lists",
    )


class TaskAccess(TimestampMixin, Base):
    __tablename__ = "task_access"

    task_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tasks.task_id", ondelete="CASCADE"),
        primary_key=True,
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.telegram_id", ondelete="CASCADE"),
        primary_key=True,
    )
    role: Mapped[AccessRoleEnum] = mapped_column(
        Enum(AccessRoleEnum),
        default=AccessRoleEnum.OWNER,
        nullable=False,
    )
    granted_by: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.telegram_id", ondelete="SET NULL", ),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    user = relationship("User", back_populates="task_access")
    task = relationship("Task", back_populates="task_access")
