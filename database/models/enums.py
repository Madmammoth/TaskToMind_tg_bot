import enum


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
