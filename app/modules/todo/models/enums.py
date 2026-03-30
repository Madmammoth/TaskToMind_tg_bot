import inspect
import sys
from enum import Enum


class GenderEnum(Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class SystemListTypeEnum(Enum):
    INBOX = "inbox"
    ARCHIVE = "archive"
    TRASH = "trash"
    NONE = "none"


class LevelEnum(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskStatusEnum(Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELED = "canceled"


class ReminderStatusEnum(Enum):
    PENDING = "pending"
    SENT = "sent"
    CANCELED = "canceled"


class AccessRoleEnum(Enum):
    OWNER = "owner"
    EDITOR = "editor"
    VIEWER = "viewer"


_current_module = sys.modules[__name__]
db_enums = [
    obj for name, obj in inspect.getmembers(_current_module)
    if inspect.isclass(obj) and issubclass(obj, Enum) and obj.__module__ == __name__
]
