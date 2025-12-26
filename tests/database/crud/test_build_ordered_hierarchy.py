from types import SimpleNamespace

from app.database.services.task_list import build_ordered_hierarchy


def fake_list(
        list_id: int,
        title: str,
        parent_list_id: int | None,
        position: int,
):
    return SimpleNamespace(
        list_id=list_id,
        title=title,
        parent_list_id=parent_list_id,
        position=position,
    )


def test_empty_rows():
    buttons, lists = build_ordered_hierarchy([])
    assert buttons == []
    assert lists == {}


def test_simple_tree():
    rows = [
        fake_list(1, "A", None, 1),
        fake_list(2, "B", 1, 1),
    ]

    buttons, lists = build_ordered_hierarchy(rows)  # noqa

    assert buttons == [
        {"list_id": 1, "list_title": "A", "pos": "1."},
        {"list_id": 2, "list_title": "B", "pos": "1.1."},
    ]
    assert lists == {
        1: "A",
        2: "B",
    }


def test_hidden_parent_keeps_position_for_child():
    rows = [
        fake_list(3, "Parent", None, 3),
        fake_list(4, "Child", 3, 1),
    ]

    buttons, lists = build_ordered_hierarchy(
        rows,  # noqa
        is_hidden=lambda r: r.list_id == 3,
    )

    assert buttons == [
        {"list_id": 4, "list_title": "Child", "pos": "3.1."},
    ]
    assert lists == {
        4: "Child",
    }


def test_multiple_levels_with_hidden_middle():
    rows = [
        fake_list(1, "A", None, 1),
        fake_list(2, "B", 1, 2),
        fake_list(3, "C", 2, 1),
    ]

    buttons, lists = build_ordered_hierarchy(
        rows,  # noqa
        is_hidden=lambda r: r.list_id == 2,
    )

    assert buttons == [
        {"list_id": 1, "list_title": "A", "pos": "1."},
        {"list_id": 3, "list_title": "C", "pos": "1.2.1."},
    ]
    assert lists == {
        1: "A",
        3: "C",
    }


def test_sorting_by_position():
    rows = [
        fake_list(1, "A", None, 2),
        fake_list(2, "B", None, 1),
    ]

    buttons, lists = build_ordered_hierarchy(rows)  # noqa

    assert buttons[0]["list_id"] == 2
    assert buttons[1]["list_id"] == 1
    assert lists == {
        1: "A",
        2: "B",
    }


def test_lists_keys_match_buttons_ids():
    rows = [
        fake_list(1, "A", None, 1),
        fake_list(2, "B", 1, 1),
    ]

    buttons, lists = build_ordered_hierarchy(rows)  # noqa

    assert set(lists.keys()) == {b["list_id"] for b in buttons}
