from datetime import datetime
from typing import Optional

from sqlalchemy import (
    CheckConstraint,
    Integer,
    BigInteger,
    ForeignKey,
    Text,
    Enum,
    DateTime,
    String,
)
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, make_timestamp_mixin
from .enums import TaskStatusEnum, LevelEnum, AccessRoleEnum
from .tag import TaskTag
from .tracking import Reminder, ActivityLog, RecurrenceRule


class Task(Base, make_timestamp_mixin()):
    __tablename__ = "tasks"
    __table_args__ = (
        CheckConstraint("completed_at IS NULL OR completed_at >= created_at",
                        name="chk_complete_after_created"),
        CheckConstraint("canceled_at IS NULL OR canceled_at >= created_at",
                        name="chk_canceled_after_created"),
    )

    task_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    message_id: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(
        String(64), default="Моя задача", nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
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
    parent_task_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("tasks.task_id", ondelete="CASCADE"),
        nullable=True,
    )
    deadline: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    canceled_at: Mapped[datetime] = mapped_column(
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
    duration: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
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
    list_links: Mapped[list["TaskInList"]] = relationship(
        "TaskInList",
        back_populates="task",
        passive_deletes=True,
    )
    reminders: Mapped[list["Reminder"]] = relationship(
        "Reminder", back_populates="task", passive_deletes=True
    )
    task_accesses: Mapped[list["TaskAccess"]] = relationship(
        "TaskAccess",
        back_populates="task",
        passive_deletes=True,
    )
    activity_logs: Mapped[list["ActivityLog"]] = relationship(
        "ActivityLog",
        back_populates="task",
        passive_deletes=True,
    )
    recurrence_rules: Mapped[list["RecurrenceRule"]] = relationship(
        "RecurrenceRule", back_populates="tasks", passive_deletes=True
    )
    tag_links: Mapped[list["TaskTag"]] = relationship(
        "TaskTag",
        back_populates="task",
        passive_deletes=True,
    )

    users = association_proxy("task_accesses", "user")
    lists = association_proxy("tasks_in_lists", "task_list")

    def __repr__(self) -> str:
        return (f"<Task id={self.task_id}, shared={self.is_shared}, "
                f"status={self.status.value}, title={self.title[:20]!r}>")


class TaskInList(Base, make_timestamp_mixin(include_updated=False)):
    __tablename__ = "tasks_in_lists"

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

    task_list = relationship(
        "TaskList", back_populates="task_links",
    )
    task = relationship(
        "Task", back_populates="list_links",
    )


class TaskAccess(Base, make_timestamp_mixin()):
    __tablename__ = "task_accesses"

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
    granted_by: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("users.telegram_id", ondelete="SET NULL"),
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="task_accesses",
        foreign_keys=[user_id],
    )
    task = relationship(
        "Task",
        back_populates="task_accesses",
        foreign_keys=[task_id],
    )
    granted_by_user = relationship(
        "User",
        back_populates="granted_task_accesses",
        foreign_keys=[granted_by],
    )

    def __repr__(self):
        return (f"<TaskAccess user_id={self.user_id}, task_id={self.list_id}, "
                f"role={self.role.value}>")
