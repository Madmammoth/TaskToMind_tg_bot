import importlib
import inspect
from datetime import datetime, date
from enum import Enum


def generate_enum_map(module_path: str) -> dict:
    module = importlib.import_module(module_path)
    enum_map = {}

    for name, obj in inspect.getmembers(module):
        if (
            inspect.isclass(obj)
            and issubclass(obj, Enum)
            and obj.__module__ == module_path
        ):
            enum_map[name] = obj

    return enum_map


ENUM_MAP = generate_enum_map("app.database.models.enums")


def to_dialog_safe(value):
    if isinstance(value, Enum):
        return {"__enum__": f"{value.__class__.__name__}.{value.name}"}

    if isinstance(value, (datetime, date)):
        return {"__datetime__": value.isoformat()}

    if isinstance(value, dict):
        safe_dict = {}
        for k, v in value.items():
            if isinstance(k, int):
                safe_key = f"__int__{k}"
            else:
                safe_key = k
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
            return ENUM_MAP[name][member]

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
