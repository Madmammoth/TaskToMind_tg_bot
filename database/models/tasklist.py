from datetime import datetime

from sqlalchemy import (
    Integer, ForeignKey, BigInteger, Enum, DateTime, func, String
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin
from .enums import AccessRoleEnum
from .task import UserTaskList
from .support import ActivityLog


class TaskList(TimestampMixin, Base):
    __tablename__ = "lists"

    list_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    list_name: Mapped[str] = mapped_column(
        String(64), default="Мой список", nullable=False
    )
    parent_list_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("lists.list_id", ondelete="CASCADE")
    )
    is_shared: Mapped[bool] = mapped_column(default=False, nullable=False)

    parent: Mapped["TaskList"] = relationship(
        "TaskList",
        remote_side=[list_id],
        back_populates="children",
        uselist=False,
    )
    children: Mapped[list["TaskList"]] = relationship(
        "TaskList",
        back_populates="parent",
        cascade="all, delete-orphan",
    )
    user: Mapped[list["UserList"]] = relationship(
        "UserList", back_populates="tasklist", passive_deletes=True
    )
    user_tasks: Mapped[list["UserTaskList"]] = relationship(
        "UserTaskList", back_populates="tasklist", passive_deletes=True,
    )
    list_access: Mapped[list["ListAccess"]] = relationship(
        "ListAccess", back_populates="tasklist", passive_deletes=True,
    )
    activity_logs: Mapped[list["ActivityLog"]] = relationship(
        "ActivityLog", back_populates="tasklist", passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<TaskList id={self.list_id} shared={self.is_shared}>"


class UserList(TimestampMixin, Base):
    __tablename__ = "user_lists"

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
    is_owner: Mapped[bool] = mapped_column(default=True, nullable=False)

    user = relationship(
        "User", back_populates="tasklist",
    )
    tasklist = relationship(
        "TaskList", back_populates="user",
    )


class ListAccess(TimestampMixin, Base):
    __tablename__ = "list_access"

    list_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("lists.list_id", ondelete="CASCADE"),
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

    user = relationship(
        "User", back_populates="list_access"
    )
    tasklist = relationship(
        "TaskList", back_populates="list_access"
    )
