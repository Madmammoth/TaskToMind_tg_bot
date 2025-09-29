import enum
from datetime import datetime

from sqlalchemy import (
    BigInteger, String, Integer, ForeignKey, Text, SmallInteger,
    CheckConstraint, DateTime, Enum, func, UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, relationship
)


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class GenderEnum(enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class LevelEnum(enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskStatusEnum(enum.Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"


class ReminderStatusEnum(enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    CANCELLED = "cancelled"


class AccessRoleEnum(enum.Enum):
    OWNER = "owner"
    EDITOR = "editor"
    VIEWER = "viewer"


class User(TimestampMixin, Base):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None] = mapped_column(String(32), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    gender: Mapped[GenderEnum] = mapped_column(
        Enum(GenderEnum), default=GenderEnum.OTHER, nullable=False,
    )
    timezone: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
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


class TaskList(TimestampMixin, Base):
    __tablename__ = "lists"

    list_id: Mapped[int] = mapped_column(Integer, primary_key=True)
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


class Task(TimestampMixin, Base):
    __tablename__ = "tasks"
    __table_args__ = (
        CheckConstraint("done_at IS NULL OR done_at >= created_at",
                        name="chk_done_after_created"),
        CheckConstraint("cancelled_at IS NULL OR cancelled_at >= created_at",
                        name="chk_cancelled_after_created"),
    )

    task_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    creator_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.telegram_id"), nullable=False
    )
    message_id: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[LevelEnum] = mapped_column(
        Enum(LevelEnum), nullable=False, default=LevelEnum.MEDIUM
    )
    urgency: Mapped[LevelEnum] = mapped_column(
        Enum(LevelEnum), nullable=False, default=LevelEnum.MEDIUM
    )
    status: Mapped[TaskStatusEnum] = mapped_column(
        Enum(TaskStatusEnum), nullable=False, default=TaskStatusEnum.NEW
    )
    is_shared: Mapped[bool] = mapped_column(default=False, nullable=False)
    owner_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.telegram_id"), nullable=False
    )
    parent_task_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("tasks.task_id", ondelete="CASCADE"),
    )
    deadline: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )
    done_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    cancelled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    postponed_count: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    is_recurring: Mapped[bool] = mapped_column(
        default=False, nullable=False
    )
    recurrence_rule_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("recurrence_rules.rule_id", ondelete="SET NULL")
    )
    duration: Mapped[int] = mapped_column(BigInteger, nullable=True)
    remind: Mapped[bool] = mapped_column(default=False, nullable=False)

    parent: Mapped["Task"] = relationship(
        "Task",
        remote_side=[task_id],
        back_populates="children",
        uselist=False
    )
    children: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="parent",
        cascade="all, delete-orphan"
    )
    user_lists: Mapped[list["UserTaskList"]] = relationship(
        "UserTaskList", back_populates="task", passive_deletes=True
    )
    reminders: Mapped[list["Reminder"]] = relationship(
        "Reminder", back_populates="task", passive_deletes=True
    )
    task_access: Mapped[list["TaskAccess"]] = relationship(
        "TaskAccess", back_populates="task", passive_deletes=True
    )
    activity_logs: Mapped[list["ActivityLog"]] = relationship(
        "ActivityLog", back_populates="task", passive_deletes=True
    )
    recurrence_rules: Mapped[list["RecurrenceRule"]] = relationship(
        "RecurrenceRule", back_populates="tasks", passive_deletes=True
    )
    tags: Mapped[list["TaskTags"]] = relationship(
        "TaskTags", back_populates="task", passive_deletes=True
    )

    def __repr__(self) -> str:
        return (f"<Task id={self.task_id} shared={self.is_shared} "
                f"status={self.status.value} text={self.text[:20]!r}>")


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

    user: Mapped["User"] = relationship(
        "User", back_populates="tasklist",
    )
    tasklist: Mapped["TaskList"] = relationship(
        "TaskList", back_populates="user",
    )


class UserTaskList(TimestampMixin, Base):
    __tablename__ = "user_task_lists"

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
    task_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tasks.task_id", ondelete="CASCADE"),
        primary_key=True,
    )
    is_owner: Mapped[bool] = mapped_column(default=True, nullable=False)

    user: Mapped["User"] = relationship(
        "User", back_populates="task_lists",
    )
    tasklist: Mapped["TaskList"] = relationship(
        "TaskList", back_populates="user_tasks",
    )
    task: Mapped["Task"] = relationship(
        "Task", back_populates="user_lists",
    )


class Reminder(TimestampMixin, Base):
    __tablename__ = "reminders"

    reminder_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.task_id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.telegram_id", ondelete="CASCADE"),
        nullable=False,
    )
    remind_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    recurrence_rule_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("recurrence_rules.rule_id", ondelete="SET NULL")
    )
    status: Mapped[ReminderStatusEnum] = mapped_column(
        Enum(ReminderStatusEnum),
        default=ReminderStatusEnum.PENDING,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    user: Mapped["User"] = relationship("User", back_populates="reminders")
    task: Mapped["Task"] = relationship("Task", back_populates="reminders")
    recurrence_rules: Mapped["RecurrenceRule"] = relationship(
        "RecurrenceRule", back_populates="reminders"
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
        ForeignKey("users.telegram_id", ondelete="SET NULL",),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    user: Mapped["User"] = relationship(
        "User", back_populates="list_access"
    )
    tasklist: Mapped["TaskList"] = relationship(
        "TaskList", back_populates="list_access"
    )


class TaskAccess(TimestampMixin, Base):
    __tablename__ = "task_access"

    task_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tasks.task_id", ondelete="CASCADE"),
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
        ForeignKey("users.telegram_id", ondelete="SET NULL",),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    user: Mapped["User"] = relationship("User", back_populates="task_access")
    task: Mapped["Task"] = relationship("Task", back_populates="task_access")


class ActivityLog(TimestampMixin, Base):
    __tablename__ = "activity_logs"

    log_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.telegram_id"), nullable=True,
    )
    task_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("tasks.task_id"), nullable=True,
    )
    list_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("lists.list_id"), nullable=True,
    )
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    old_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    extra: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    user: Mapped["User"] = relationship(
        "User", back_populates="activity_logs"
    )
    tasklist: Mapped["TaskList"] = relationship(
        "TaskList", back_populates="activity_logs"
    )
    task: Mapped["Task"] = relationship(
        "Task", back_populates="activity_logs"
    )


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

    user: Mapped["User"] = relationship(
        "User", back_populates="achievements"
    )
    achievement: Mapped["Achievement"] = relationship(
        "Achievement", back_populates="users"
    )


class RecurrenceRule(TimestampMixin, Base):
    __tablename__ = "recurrence_rules"

    rule_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    frequency: Mapped[str | None] = mapped_column(String(20), nullable=True)
    interval: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pattern: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    tasks: Mapped[list["Task"]] = relationship(
        "Task", back_populates="recurrence_rules"
    )
    reminders: Mapped[list["Reminder"]] = relationship(
        "Reminder", back_populates="recurrence_rules"
    )
