from datetime import datetime, date
from enum import Enum

from app.database.models.enums import db_enums

_ENUM_MAP: dict[str, type[Enum]] = {cls.__name__: cls for cls in db_enums}


def to_dialog_safe(value):
    if isinstance(value, Enum):
        return {"__enum__": f"{value.__class__.__name__}.{value.name}"}

    if isinstance(value, (datetime, date)):
        return {"__datetime__": value.isoformat()}

    if isinstance(value, dict):
        safe_dict = {}
        for k, v in value.items():
            safe_key = f"__int__{k}" if isinstance(k, int) else k
            safe_dict[safe_key] = to_dialog_safe(v)
        return safe_dict

    if isinstance(value, tuple):
        return {"__tuple__": [to_dialog_safe(v) for v in value]}

    if isinstance(value, list):
        return [to_dialog_safe(v) for v in value]

    return value


def from_dialog_safe(value):
    if isinstance(value, dict):
        if "__enum__" in value:
            name, member = value["__enum__"].split(".")
            return _ENUM_MAP[name][member]

        if "__datetime__" in value:
            return datetime.fromisoformat(value["__datetime__"])

        if "__tuple__" in value:
            return tuple(from_dialog_safe(v) for v in value["__tuple__"])

        safe_dict = {}
        for k, v in value.items():
            if k.startswith("__int__"):
                key = int(k[len("__int__"):])
            else:
                key = k
            safe_dict[key] = from_dialog_safe(v)
        return safe_dict

    if isinstance(value, list):
        return [from_dialog_safe(v) for v in value]

    return value
