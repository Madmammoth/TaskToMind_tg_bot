from typing import Annotated

from sqlalchemy import Integer, BigInteger, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

from app.database.models import Base
from app.database.models.base import make_timestamp_mixin

stats_counter = Annotated[
    int, mapped_column(Integer, default=0, nullable=False)
]


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
