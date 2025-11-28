from datetime import datetime, date

import pytest

from app.database.models import GenderEnum, LevelEnum, SystemListTypeEnum
from app.utils.serialization import to_dialog_safe, from_dialog_safe, \
    generate_enum_map


def test_to_dialog_safe_enum_positive():
    assert to_dialog_safe(GenderEnum.MALE) == {
        "__enum__": "GenderEnum.MALE"
    }


def test_to_dialog_safe_datetime():
    dt = datetime(2024, 1, 2, 3, 4, 5)
    assert to_dialog_safe(dt) == {
        "__datetime__": "2024-01-02T03:04:05"
    }


def test_to_dialog_safe_date():
    d = date(2024, 2, 3)
    assert to_dialog_safe(d) == {
        "__datetime__": "2024-02-03"
    }


def test_to_dialog_safe_dict_simple():
    data = {"a": 10, "b": "text"}
    assert to_dialog_safe(data) == {"a": 10, "b": "text"}


def test_to_dialog_safe_dict_with_int_keys():
    data = {1: "one", 2: LevelEnum.MEDIUM}
    result = to_dialog_safe(data)

    assert result == {
        "__int__1": "one",
        "__int__2": {"__enum__": "LevelEnum.MEDIUM"}
    }


def test_to_dialog_safe_list_mixed():
    data = [1, "text", GenderEnum.FEMALE]
    assert to_dialog_safe(data) == [
        1,
        "text",
        {"__enum__": "GenderEnum.FEMALE"}
    ]


def test_to_dialog_safe_tuple():
    data = (1, GenderEnum.MALE)
    assert to_dialog_safe(data) == {
        "__tuple__": [1, {"__enum__": "GenderEnum.MALE"}]
    }


def test_to_dialog_safe_nested_structures():
    data = {
        "a": [
            {"x": (GenderEnum.MALE, 10)}
        ]
    }

    assert to_dialog_safe(data) == {
        "a": [
            {
                "x": {
                    "__tuple__": [
                        {"__enum__": "GenderEnum.MALE"},
                        10
                    ]
                }
            }
        ]
    }


def test_from_dialog_safe_enum():
    assert from_dialog_safe(
        {"__enum__": "SystemListTypeEnum.ARCHIVE"}
    ) == SystemListTypeEnum.ARCHIVE


def test_from_dialog_safe_datetime():
    obj = {"__datetime__": "2024-01-01T10:20:30"}
    assert from_dialog_safe(obj) == datetime(2024, 1, 1, 10, 20, 30)


def test_from_dialog_safe_date():
    obj = {"__datetime__": "2024-02-03"}
    assert from_dialog_safe(obj) == datetime(2024, 2, 3)


def test_from_dialog_safe_tuple():
    obj = {"__tuple__": [1, {"__enum__": "GenderEnum.MALE"}]}
    assert from_dialog_safe(obj) == (1, GenderEnum.MALE)


def test_from_dialog_safe_dict_int_keys():
    obj = {
        "__int__1": 100,
        "__int__2": {"__enum__": "LevelEnum.HIGH"},
    }

    result = from_dialog_safe(obj)
    assert result == {
        1: 100,
        2: LevelEnum.HIGH,
    }


def test_from_dialog_safe_list():
    obj = [1, {"__enum__": "SystemListTypeEnum.NONE"}]
    assert from_dialog_safe(obj) == [1, SystemListTypeEnum.NONE]


def test_from_dialog_safe_nested():
    obj = {
        "a": [
            {
                "x": {
                    "__tuple__": [
                        {"__enum__": "GenderEnum.OTHER"},
                        42
                    ]
                }
            }
        ]
    }

    result = from_dialog_safe(obj)
    assert result == {
        "a": [
            {
                "x": (GenderEnum.OTHER, 42)
            }
        ]
    }


def test_from_dialog_safe_invalid_enum():
    with pytest.raises(KeyError):
        from_dialog_safe({"__enum__": "UnknownEnum.VALUE"})


def test_from_dialog_safe_invalid_enum_member():
    with pytest.raises(KeyError):
        from_dialog_safe({"__enum__": "GenderEnum.MEMBER"})


def test_from_dialog_safe_invalid_datetime_format():
    with pytest.raises(ValueError):
        from_dialog_safe({"__datetime__": "not-a-date"})


def test_to_dialog_safe_unsupported_type():
    class CustomObj:
        pass

    obj = CustomObj()
    assert to_dialog_safe(obj) is obj


def test_from_dialog_safe_non_dict_non_list_non_basic():
    assert from_dialog_safe(123) == 123
    assert from_dialog_safe("text") == "text"
    assert from_dialog_safe(None) is None


def test_generate_enum_map(tmp_path):
    """Dynamically create a module, import it and scan enums."""

    module_file = tmp_path / "enums_test_module.py"
    module_file.write_text("""
from enum import Enum

class A(Enum):
    X = 1
    Y = 2

class B(Enum):
    Z = 3

value = 10
""")

    import sys
    sys.path.insert(0, str(tmp_path))

    enum_map = generate_enum_map("enums_test_module")
    assert enum_map == {
        "A": enum_map["A"],
        "B": enum_map["B"]
    }

    sys.path.pop(0)