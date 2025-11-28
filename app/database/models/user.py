from datetime import datetime, timedelta

from sqlalchemy import (
    BigInteger, String, Enum, SmallInteger, DateTime, Interval, func,
    and_
)
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .achievement import UserAchievement
from .base import Base, make_timestamp_mixin
from .enums import AccessRoleEnum, GenderEnum
from .tag import Tag, UserTag
from .task import Task, TaskAccess
from .task_list import TaskList, ListAccess
from .tracking import Reminder, ActivityLog


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
    is_bot_stopped: Mapped[bool] = mapped_column(
        default=False, nullable=False
    )
    stopped_count: Mapped[int | None] = mapped_column(
        SmallInteger, default=0, nullable=False
    )

    reminders: Mapped[list["Reminder"]] = relationship(
        "Reminder", back_populates="user", passive_deletes=True,
    )
    list_accesses: Mapped[list["ListAccess"]] = relationship(
        "ListAccess",
        back_populates="user",
        foreign_keys="ListAccess.user_id",
        passive_deletes=True,
    )
    granted_list_accesses: Mapped[list["ListAccess"]] = relationship(
        "ListAccess",
        back_populates="granted_by_user",
        foreign_keys="ListAccess.granted_by",
        passive_deletes=True,
    )
    task_accesses: Mapped[list["TaskAccess"]] = relationship(
        "TaskAccess",
        back_populates="user",
        foreign_keys="TaskAccess.user_id",
        passive_deletes=True,
    )
    granted_task_accesses: Mapped[list["TaskAccess"]] = relationship(
        "TaskAccess",
        back_populates="granted_by_user",
        foreign_keys="TaskAccess.granted_by",
        passive_deletes=True,
    )
    owner_list_accesses: Mapped[list[ListAccess]] = relationship(
        "ListAccess",
        primaryjoin=and_(
            ListAccess.user_id == telegram_id,
            ListAccess.role == AccessRoleEnum.OWNER
        ),
        viewonly=True,
    )
    editor_list_accesses: Mapped[list[ListAccess]] = relationship(
        "ListAccess",
        primaryjoin=and_(
            ListAccess.user_id == telegram_id,
            ListAccess.role == AccessRoleEnum.EDITOR
        ),
        viewonly=True,
    )
    viewer_list_accesses: Mapped[list[ListAccess]] = relationship(
        "ListAccess",
        primaryjoin=and_(
            ListAccess.user_id == telegram_id,
            ListAccess.role == AccessRoleEnum.VIEWER
        ),
        viewonly=True,
    )
    owner_task_accesses: Mapped[list[TaskAccess]] = relationship(
        "TaskAccess",
        primaryjoin=and_(
            TaskAccess.user_id == telegram_id,
            TaskAccess.role == AccessRoleEnum.OWNER
        ),
        viewonly=True,
    )
    editor_task_accesses: Mapped[list[TaskAccess]] = relationship(
        "TaskAccess",
        primaryjoin=and_(
            TaskAccess.user_id == telegram_id,
            TaskAccess.role == AccessRoleEnum.EDITOR
        ),
        viewonly=True,
    )
    viewer_task_accesses: Mapped[list[TaskAccess]] = relationship(
        "TaskAccess",
        primaryjoin=and_(
            TaskAccess.user_id == telegram_id,
            TaskAccess.role == AccessRoleEnum.VIEWER
        ),
        viewonly=True,
    )
    activity_logs: Mapped[list["ActivityLog"]] = relationship(
        "ActivityLog",
        back_populates="user",
        passive_deletes=True,
    )
    tag_links: Mapped[list["UserTag"]] = relationship(
        "UserTag",
        back_populates="user",
        passive_deletes=True,
    )
    created_tags: Mapped[list["Tag"]] = relationship(
        "Tag",
        back_populates="created_by_user",
        passive_deletes=True,
    )
    achievements: Mapped[list["UserAchievement"]] = relationship(
        "UserAchievement", back_populates="user", passive_deletes=True,
    )

    lists: Mapped[list["TaskList"]] = association_proxy(
        "list_accesses", "task_list",
        creator=lambda task_list: TaskAccess(  # type: ignore
            task_list=task_list, role=AccessRoleEnum.OWNER
        )
    )
    editor_lists: Mapped[list["TaskList"]] = association_proxy(
        "list_accesses", "task_list",
        creator=lambda task_list: TaskAccess(  # type: ignore
            task_list=task_list, role=AccessRoleEnum.EDITOR
        )
    )
    viewer_lists: Mapped[list["TaskList"]] = association_proxy(
        "list_accesses", "task_list",
        creator=lambda task_list: TaskAccess(  # type: ignore
            task_list=task_list, role=AccessRoleEnum.VIEWER
        )
    )
    tasks: Mapped[list["Task"]] = association_proxy(
        "task_accesses", "task",
        creator=lambda task: TaskAccess(task=task,  # type: ignore
                                        role=AccessRoleEnum.OWNER)
    )
    editor_tasks: Mapped[list["Task"]] = association_proxy(
        "task_accesses", "task",
        creator=lambda task: TaskAccess(task=task,  # type: ignore
                                        role=AccessRoleEnum.EDITOR)
    )
    viewer_tasks: Mapped[list["Task"]] = association_proxy(
        "task_accesses", "task",
        creator=lambda task: TaskAccess(task=task,  # type: ignore
                                        role=AccessRoleEnum.VIEWER)
    )

    def __repr__(self) -> str:
        return f"<User id={self.telegram_id}, username={self.username!r}>"
