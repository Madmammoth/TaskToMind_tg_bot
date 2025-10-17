from datetime import datetime, timedelta
from typing import Annotated

from sqlalchemy import (
    BigInteger, String, Enum, SmallInteger, DateTime, Interval, func,
    ForeignKey, Integer
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, make_timestamp_mixin
from .enums import GenderEnum
from .tasklist import UserList, ListAccess
from .task import UserTaskList, TaskAccess
from .support import Reminder, ActivityLog
from .tag import UserTags
from .achievement import UserAchievements

stats_counter = Annotated[
    int, mapped_column(Integer, default=0, nullable=False)
]


class User(Base, make_timestamp_mixin()):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None] = mapped_column(String(32), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    gender: Mapped[GenderEnum] = mapped_column(
        Enum(GenderEnum), default=GenderEnum.OTHER, nullable=False,
    )
    timezone_name: Mapped[str] = mapped_column(
        String(50), nullable=False, default="Europe/Moscow"
    )
    timezone_offset: Mapped[timedelta] = mapped_column(
        Interval, nullable=False, default=timedelta(hours=3)
    )
    last_active: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )
    is_stopped_bot: Mapped[bool] = mapped_column(
        default=False, nullable=False
    )
    stopped_count: Mapped[int | None] = mapped_column(
        SmallInteger, default=0, nullable=False
    )

    tasklist: Mapped[list["UserList"]] = relationship(
        "UserList", back_populates="user", passive_deletes=True
    )
    task_lists: Mapped[list["UserTaskList"]] = relationship(
        "UserTaskList", back_populates="user", passive_deletes=True
    )
    reminders: Mapped[list["Reminder"]] = relationship(
        "Reminder", back_populates="user", passive_deletes=True,
    )
    list_access: Mapped[list["ListAccess"]] = relationship(
        "ListAccess",
        back_populates="user",
        passive_deletes=True,
        foreign_keys="ListAccess.user_id",
    )
    task_access: Mapped[list["TaskAccess"]] = relationship(
        "TaskAccess",
        back_populates="user",
        passive_deletes=True,
        foreign_keys="TaskAccess.user_id",
    )
    activity_logs: Mapped[list["ActivityLog"]] = relationship(
        "ActivityLog", back_populates="user", passive_deletes=True,
    )
    tags: Mapped[list["UserTags"]] = relationship(
        "UserTags", back_populates="user"
    )
    achievements: Mapped[list["UserAchievements"]] = relationship(
        "UserAchievements", back_populates="user", passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<User id={self.telegram_id} username={self.username!r}>"


class UserStats(Base, make_timestamp_mixin()):
    __tablename__ = "user_stats"

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.telegram_id", ondelete="CASCADE"),
        primary_key=True,
    )
    tasks_created: Mapped[stats_counter]
    tasks_completed: Mapped[stats_counter]
    tasks_postponed: Mapped[stats_counter]
    tasks_canceled: Mapped[stats_counter]
    tasks_shared: Mapped[stats_counter]
    shared_tasks_completed: Mapped[stats_counter]
    shared_tasks_postponed: Mapped[stats_counter]
    shared_tasks_canceled: Mapped[stats_counter]
    recurring_tasks_created: Mapped[stats_counter]
    recurring_tasks_deleted: Mapped[stats_counter]
    low_priority_tasks_created: Mapped[stats_counter]
    medium_priority_tasks_created: Mapped[stats_counter]
    high_priority_tasks_created: Mapped[stats_counter]
    low_urgency_tasks_created: Mapped[stats_counter]
    medium_urgency_tasks_created: Mapped[stats_counter]
    high_urgency_tasks_created: Mapped[stats_counter]
    low_priority_tasks_completed: Mapped[stats_counter]
    medium_priority_tasks_completed: Mapped[stats_counter]
    high_priority_tasks_completed: Mapped[stats_counter]
    low_urgency_tasks_completed: Mapped[stats_counter]
    medium_urgency_tasks_completed: Mapped[stats_counter]
    high_urgency_tasks_completed: Mapped[stats_counter]
    postpones_per_task: Mapped[stats_counter]
    tasks_completed_before_deadline: Mapped[stats_counter]
    tasks_completed_after_deadline: Mapped[stats_counter]
    checked_tasks_created: Mapped[stats_counter]
    checked_tasks_completed: Mapped[stats_counter]
    checked_tasks_canceled: Mapped[stats_counter]
    lists_created: Mapped[stats_counter]
    lists_deleted: Mapped[stats_counter]
    lists_shared: Mapped[stats_counter]
    tags_created: Mapped[stats_counter]
    tags_deleted: Mapped[stats_counter]
    tasks_tagged: Mapped[stats_counter]
    tags_assigned: Mapped[stats_counter]
    tags_per_task: Mapped[stats_counter]
    reminders_created: Mapped[stats_counter]
    reminders_deleted: Mapped[stats_counter]
    recurring_reminders_created: Mapped[stats_counter]
    recurring_reminders_deleted: Mapped[stats_counter]
    recurrence_rules_created: Mapped[stats_counter]
