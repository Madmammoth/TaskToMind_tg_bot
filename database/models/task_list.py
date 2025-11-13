from typing import Optional

from sqlalchemy import (
    Integer,
    ForeignKey,
    BigInteger,
    Enum, String,
    CheckConstraint,
    UniqueConstraint,
)
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, make_timestamp_mixin
from .enums import AccessRoleEnum, SystemListTypeEnum
from .tracking import ActivityLog
from .task import TaskInList


class TaskList(Base, make_timestamp_mixin()):
    __tablename__ = "lists"

    list_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(
        String(64), default="Мой список", nullable=False
    )
    parent_list_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("lists.list_id", ondelete="CASCADE"),
        nullable=True,
    )
    system_type: Mapped[SystemListTypeEnum] = mapped_column(
        Enum(SystemListTypeEnum),
        nullable=False,
        default=SystemListTypeEnum.NONE,
    )

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
    task_links: Mapped[list["TaskInList"]] = relationship(
        "TaskInList",
        back_populates="task_list",
        passive_deletes=True,
    )
    list_accesses: Mapped[list["ListAccess"]] = relationship(
        "ListAccess",
        back_populates="task_list",
        passive_deletes=True,
    )
    activity_logs: Mapped[list["ActivityLog"]] = relationship(
        "ActivityLog",
        back_populates="tasklist",
        passive_deletes=True,
    )

    users = association_proxy("list_accesses", "user")
    tasks = association_proxy("task_links", "task")

    def __repr__(self) -> str:
        return (f"<TaskList id={self.list_id}, shared={self.is_shared}, "
                f"title={self.title[:20]!r}>")


class ListAccess(Base, make_timestamp_mixin()):
    __tablename__ = "list_accesses"
    __table_args__ = (
        CheckConstraint("position >= 1", name="check_list_position_min"),
        UniqueConstraint("user_id", "list_id"),
        UniqueConstraint("user_id", "parent_list_id", "position",
                         name="uq_user_parent_position"),
    )

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
    granted_by: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("users.telegram_id", ondelete="SET NULL"),
        nullable=True,
    )
    parent_list_id: Mapped[int] = mapped_column(Integer, nullable=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    user = relationship(
        "User",
        back_populates="list_accesses",
        foreign_keys=[user_id],
    )
    task_list = relationship(
        "TaskList",
        back_populates="list_accesses",
        foreign_keys=[list_id],
    )
    granted_by_user = relationship(
        "User",
        back_populates="granted_list_accesses",
        foreign_keys=[granted_by],
    )

    def __repr__(self):
        return (f"<ListAccess user_id={self.user_id}, list_id={self.list_id}, "
                f"role={self.role.value}>")
