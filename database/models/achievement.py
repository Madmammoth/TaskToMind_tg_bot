from datetime import datetime

from sqlalchemy import (
    Integer, String, ForeignKey, Text, BigInteger, DateTime
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class Achievement(TimestampMixin, Base):
    __tablename__ = "achievements"

    achievement_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    achievement_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(
        Text, nullable=False
    )
    emoji: Mapped[str] = mapped_column(String(10), nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=True)
    is_secret: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_progression: Mapped[bool] = mapped_column(default=False,
                                                 nullable=False)
    required_count: Mapped[int] = mapped_column(Integer, nullable=True)
    previous_achievement_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("achievements.achievement_id", ondelete="SET NULL"),
        nullable=True,
        default=None,
    )

    parent: Mapped["Achievement"] = relationship(
        "Achievement",
        remote_side=[achievement_id],
        back_populates="children",
        uselist=False,
    )
    children: Mapped[list["Achievement"]] = relationship(
        "Achievement",
        back_populates="parent",
        cascade="all, delete-orphan"
    )
    users: Mapped[list["UserAchievements"]] = relationship(
        "UserAchievements", back_populates="achievement"
    )


class UserAchievements(TimestampMixin, Base):
    __tablename__ = "user_achievements"

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.telegram_id", ondelete="CASCADE"),
        primary_key=True,
    )
    achievement_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("achievements.achievement_id", ondelete="CASCADE"),
        primary_key=True,
    )
    unlocked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    progress: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_completed: Mapped[bool] = mapped_column(default=False,
                                               nullable=False)

    user = relationship(
        "User", back_populates="achievements"
    )
    achievement = relationship(
        "Achievement", back_populates="users"
    )
