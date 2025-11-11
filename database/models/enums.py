import json
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
    CANCELLED = "cancelled"


class ReminderStatusEnum(Enum):
    PENDING = "pending"
    SENT = "sent"
    CANCELLED = "cancelled"


class AccessRoleEnum(Enum):
    OWNER = "owner"
    EDITOR = "editor"
    VIEWER = "viewer"


ENUM_MAP = {
    "GenderEnum": GenderEnum,
    "SystemListTypeEnum": SystemListTypeEnum,
    "LevelEnum": LevelEnum,
    "TaskStatusEnum": TaskStatusEnum,
    "ReminderStatusEnum": ReminderStatusEnum,
    "AccessRoleEnum": AccessRoleEnum,
}


class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return {"__enum__": f"{obj.__class__.__name__}.{obj.name}"}
        return super().default(obj)


def enum_decoder(data):
    if "__enum__" in data:
        name, member = data["__enum__"].split(".")
        enum_cls = ENUM_MAP.get(name)
        if enum_cls:
            return enum_cls[member]
    return data
