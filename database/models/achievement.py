from sqlalchemy import Integer, String, ForeignKey, Text, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class Achievement(Base):
    __tablename__ = "achievements"

    achievement_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    achievement_name: Mapped[str] = mapped_column(String(100), nullable=False)
    parent_achievement_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("achievements.achievement_id", ondelete="CASCADE"),
        nullable=True,
    )
    achievement_description: Mapped[str] = mapped_column(
        Text, nullable=False
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
        cascade="all, delete-orphan",
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

    user = relationship(
        "User", back_populates="achievements"
    )
    achievement = relationship(
        "Achievement", back_populates="users"
    )
