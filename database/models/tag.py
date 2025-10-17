from sqlalchemy import UniqueConstraint, Integer, String, ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, make_timestamp_mixin


class Tag(Base, make_timestamp_mixin()):
    __tablename__ = "tags"
    __table_args__ = (
        UniqueConstraint(
            "tag_name", "creator_id", name="uq_tag_name_creator"
        ),
    )

    tag_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tag_name: Mapped[str] = mapped_column(String(64), nullable=False)
    parent_tag_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("tags.tag_id", ondelete="CASCADE"),
        nullable=True,
    )
    creator_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("users.telegram_id", ondelete="SET NULL"),
        nullable=True,
    )

    parent: Mapped["Tag"] = relationship(
        "Tag",
        remote_side=[tag_id],
        back_populates="children",
        uselist=False,
    )
    children: Mapped[list["Tag"]] = relationship(
        "Tag",
        back_populates="parent",
        cascade="all, delete-orphan",
    )
    users: Mapped[list["UserTag"]] = relationship("UserTag", back_populates="tag")
    tasks: Mapped[list["TaskTag"]] = relationship("TaskTag", back_populates="tag")


class UserTag(Base, make_timestamp_mixin(include_updated=False)):
    __tablename__ = "user_tags"

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.telegram_id", ondelete="CASCADE"),
        primary_key=True,
    )
    tag_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tags.tag_id", ondelete="CASCADE"),
        primary_key=True,
    )

    user = relationship("User", back_populates="tags")
    tag = relationship("Tag", back_populates="users")


class TaskTag(Base, make_timestamp_mixin(include_updated=False)):
    __tablename__ = "task_tags"

    task_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tasks.task_id", ondelete="CASCADE"),
        primary_key=True,
    )
    tag_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tags.tag_id", ondelete="CASCADE"),
        primary_key=True,
    )

    task = relationship("Task", back_populates="tags")
    tag = relationship("Tag", back_populates="tasks")
