from sqlalchemy import UniqueConstraint, Integer, String, ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models import TimestampMixin, Base, User, Task


class Tag(TimestampMixin, Base):
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
    users: Mapped[list["UserTags"]] = relationship("UserTags", back_populates="tag")
    tasks: Mapped[list["TaskTags"]] = relationship("TaskTags", back_populates="tag")


class UserTags(TimestampMixin, Base):
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

    user: Mapped["User"] = relationship("User", back_populates="tags")
    tag: Mapped["Tag"] = relationship("Tag", back_populates="users")


class TaskTags(TimestampMixin, Base):
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

    task: Mapped["Task"] = relationship("Task", back_populates="tags")
    tag: Mapped["Tag"] = relationship("Tag", back_populates="tasks")
