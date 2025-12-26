from types import SimpleNamespace
from unittest.mock import patch, AsyncMock

import pytest

from app.bot.dialogs.enums import ListSelectionMode
from app.bot.dialogs.select_list.scenarios import (
    CreateTaskScenario,
    EditTaskScenario,
    CreateListScenario,
    EditListScenario,
    get_select_list_scenario,
)
from app.database.models import SystemListTypeEnum
from app.utils.serialization import to_dialog_safe

FAKE_LISTS = [
    SimpleNamespace(
        list_id=1,
        title="Inbox",
        parent_list_id=None,
        system_type=SystemListTypeEnum.INBOX,
        position=1
    ),
    SimpleNamespace(
        list_id=2,
        title="Archive",
        parent_list_id=None,
        system_type=SystemListTypeEnum.ARCHIVE,
        position=2
    ),
    SimpleNamespace(
        list_id=3,
        title="Work",
        parent_list_id=None,
        system_type=SystemListTypeEnum.NONE,
        position=3
    ),
    SimpleNamespace(
        list_id=4,
        title="Home",
        parent_list_id=None,
        system_type=SystemListTypeEnum.NONE,
        position=4
    ),
    SimpleNamespace(
        list_id=5,
        title="Buy",
        parent_list_id=3,
        system_type=SystemListTypeEnum.NONE,
        position=1
    ),
]


@pytest.mark.asyncio
async def test_create_task_scenario_get_lists(
        mock_session,
        fake_dialog_manager,
):
    scenario = CreateTaskScenario(ListSelectionMode.CREATE_TASK)

    with patch(
            "app.bot.dialogs.select_list.scenarios.fetch_user_lists_raw",
            return_value=FAKE_LISTS,
    ):
        buttons, lists = await scenario.get_lists(
            session=mock_session,
            dialog_manager=fake_dialog_manager,
        )

    assert buttons == [
        {"list_id": 3, "list_title": "Work", "pos": "3."},
        {"list_id": 5, "list_title": "Buy", "pos": "3.1."},
        {"list_id": 4, "list_title": "Home", "pos": "4."},
    ]
    assert lists == {3: "Work", 4: "Home", 5: "Buy"}


@pytest.mark.asyncio
async def test_create_task_scenario_apply(
        fake_dialog_manager,
):
    fake_dialog_manager.dialog_data = {
        "lists": to_dialog_safe({1: "Inbox", 3: "Work", 4: "Home", 5: "Buy"}),
    }
    scenario = CreateTaskScenario(ListSelectionMode.CREATE_TASK)

    result = await scenario.apply(
        session=None,
        dialog_manager=fake_dialog_manager,
        list_id=3,
    )

    assert result == {
        "selected_list_id": 3,
        "selected_list_title": "Work",
    }


@pytest.mark.asyncio
async def test_edit_task_get_lists(
        mock_session,
        fake_dialog_manager,
):
    fake_dialog_manager.dialog_data = {"list_id": 3}
    scenario = EditTaskScenario(ListSelectionMode.EDIT_TASK)

    with patch(
            "app.bot.dialogs.select_list.scenarios.fetch_user_lists_raw",
            AsyncMock(return_value=FAKE_LISTS),
    ):
        buttons, lists = await scenario.get_lists(
            session=mock_session,
            dialog_manager=fake_dialog_manager,
        )

    assert buttons == [
        {"list_id": 1, "list_title": "Inbox", "pos": "1."},
        {"list_id": 5, "list_title": "Buy", "pos": "3.1."},
        {"list_id": 4, "list_title": "Home", "pos": "4."},
    ]
    assert lists == {1: "Inbox", 5: "Buy", 4: "Home"}


@pytest.mark.asyncio
async def test_edit_task_scenario_apply(
        mock_session,
        fake_dialog_manager,
):
    fake_dialog_manager.dialog_data = {
        "task_id": 33,
        "list_id": 3,
        "lists": to_dialog_safe({1: "Inbox", 3: "Work", 4: "Home", 5: "Buy"})
    }
    scenario = EditTaskScenario(ListSelectionMode.EDIT_TASK)

    change_mock = AsyncMock()
    with patch(
            "app.bot.dialogs.select_list.scenarios.change_list_for_task_with_log",
            change_mock,
    ):
        result = await scenario.apply(
            session=mock_session,
            dialog_manager=fake_dialog_manager,
            list_id=4,
        )

    change_mock.assert_awaited_once_with(
        mock_session,
        42,  # user_id
        33,  # task_id
        3,  # old_list_id
        4,  # new_list_id
    )

    assert result == {
        "selected_list_id": 4,
        "selected_list_title": "Home",
    }


@pytest.mark.asyncio
async def test_create_list_scenario_get_lists(
        mock_session,
        fake_dialog_manager,
):
    scenario = CreateListScenario(ListSelectionMode.CREATE_LIST)

    with patch(
            "app.bot.dialogs.select_list.scenarios.fetch_user_lists_raw",
            return_value=FAKE_LISTS,
    ):
        buttons, lists = await scenario.get_lists(
            session=mock_session,
            dialog_manager=fake_dialog_manager,
        )

    assert buttons == [
        {"list_id": 3, "list_title": "Work", "pos": "3."},
        {"list_id": 5, "list_title": "Buy", "pos": "3.1."},
        {"list_id": 4, "list_title": "Home", "pos": "4."},
    ]
    assert lists == {3: "Work", 4: "Home", 5: "Buy"}


@pytest.mark.asyncio
async def test_create_list_scenario_apply(
        fake_dialog_manager,
):
    fake_dialog_manager.dialog_data = {
        "lists": to_dialog_safe({3: "Work", 4: "Home", 5: "Buy"}),
    }
    scenario = CreateListScenario(ListSelectionMode.CREATE_LIST)

    result = await scenario.apply(
        session=None,
        dialog_manager=fake_dialog_manager,
        list_id=3,
    )

    assert result == {
        "selected_list_id": 3,
        "selected_list_title": "Work",
    }


@pytest.mark.asyncio
async def test_edit_list_get_lists(
        mock_session,
        fake_dialog_manager,
):
    fake_dialog_manager.dialog_data = {
        "list_id": 5,
        "parent_list_id": 3
    }
    scenario = EditListScenario(ListSelectionMode.EDIT_LIST)

    with patch(
            "app.bot.dialogs.select_list.scenarios.fetch_user_lists_raw",
            AsyncMock(return_value=FAKE_LISTS),
    ):
        buttons, lists = await scenario.get_lists(
            session=mock_session,
            dialog_manager=fake_dialog_manager,
        )

    assert buttons == [
        {"list_id": 4, "list_title": "Home", "pos": "4."},
    ]
    assert lists == {4: "Home"}


@pytest.mark.asyncio
async def test_edit_list_scenario_apply(
        mock_session,
        fake_dialog_manager,
):
    fake_dialog_manager.dialog_data = {
        "list_id": 5,
        "parent_list_id": 3,
        "lists": to_dialog_safe({3: "Work", 4: "Home", 5: "Buy"})
    }
    scenario = EditListScenario(ListSelectionMode.EDIT_LIST)

    change_mock = AsyncMock()
    with patch(
            "app.bot.dialogs.select_list.scenarios.change_parent_list_with_log",
            change_mock,
    ):
        result = await scenario.apply(
            session=mock_session,
            dialog_manager=fake_dialog_manager,
            list_id=4,
        )

    change_mock.assert_awaited_once_with(
        mock_session,
        42,  # user_id
        5,  # current_list_id
        3,  # old_parent_list_id
        4,  # new_parent_list_id
    )

    assert result == {
        "selected_list_id": 4,
        "selected_list_title": "Home",
    }


@pytest.mark.parametrize(
    "mode, selected_scenario",
    [
        (ListSelectionMode.CREATE_TASK, CreateTaskScenario),
        (ListSelectionMode.EDIT_TASK, EditTaskScenario),
        (ListSelectionMode.CREATE_LIST, CreateListScenario),
        (ListSelectionMode.EDIT_LIST, EditListScenario),
    ],
)
def test_get_select_list_scenario(mode, selected_scenario):
    scenario = get_select_list_scenario(mode)
    assert isinstance(scenario, selected_scenario)
