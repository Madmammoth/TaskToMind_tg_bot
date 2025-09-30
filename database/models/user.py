from datetime import datetime, timedelta

from sqlalchemy import BigInteger, String, Enum, SmallInteger, DateTime, Interval
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin
from .enums import GenderEnum
from .tasklist import UserList, ListAccess
from .task import UserTaskList, TaskAccess
from .support import Reminder, ActivityLog
from .tag import UserTags
from .achievement import UserAchievements


class User(TimestampMixin, Base):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None] = mapped_column(String(32), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    gender: Mapped[GenderEnum] = mapped_column(
        Enum(GenderEnum), default=GenderEnum.OTHER, nullable=False,
    )
    timezone_name: Mapped[str] = mapped_column(
        String(50), nullable=False, default="UTC"
    )
    timezone_offset: Mapped[timedelta] = mapped_column(
        Interval, nullable=False, default=timedelta(0)
    )
    last_active: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    is_stopped_bot: Mapped[bool] = mapped_column(
        default=False, nullable=False
    )
    stopped_count: Mapped[int | None] = mapped_column(
        SmallInteger, nullable=True
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
        "ListAccess", back_populates="user", passive_deletes=True,
    )
    task_access: Mapped[list["TaskAccess"]] = relationship(
        "TaskAccess", back_populates="user", passive_deletes=True,
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
