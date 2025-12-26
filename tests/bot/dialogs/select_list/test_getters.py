from typing import List
from unittest.mock import AsyncMock, Mock

import pytest
from pydantic import BaseModel, ValidationError

from app.bot.dialogs.enums import ListSelectionMode
from app.bot.dialogs.select_list.getters import lists_getter_core
from app.utils.serialization import to_dialog_safe
from tests.bot.mocks.mock_dialog import FakeSelectListScenario


class SelectListItemContract(BaseModel):
    list_id: int
    list_title: str
    pos: str


class SelectListWindowContract(BaseModel):
    buttons: List[SelectListItemContract]


@pytest.mark.asyncio
async def test_lists_getter_window_contract(monkeypatch, fake_dialog_manager):
    fake_buttons = [
        {"list_id": 1, "list_title": "Inbox", "pos": "1."},
        {"list_id": 3, "list_title": "Work", "pos": "3."},
        {"list_id": 5, "list_title": "Buy", "pos": "3.1."},
        {"list_id": 4, "list_title": "Home", "pos": "4."},
    ]

    fake_lists = {button["list_id"]: button["list_title"] for button in fake_buttons}

    fake_scenario = Mock()
    fake_scenario.get_lists = AsyncMock(
        return_value=(fake_buttons, fake_lists)
    )

    monkeypatch.setattr(
        "app.bot.dialogs.select_list.getters.get_select_list_scenario",
        lambda mode: fake_scenario,
    )

    fake_dialog_manager.start_data = {"mode": ListSelectionMode.CREATE_TASK}

    data = await lists_getter_core(
        dialog_manager=fake_dialog_manager,
        di_session=Mock(),
    )

    SelectListWindowContract.model_validate(data)

    assert "lists" in fake_dialog_manager.dialog_data
    assert fake_dialog_manager.dialog_data["lists"] == to_dialog_safe(fake_lists)


@pytest.mark.asyncio
async def test_lists_getter_allows_empty_buttons(monkeypatch, fake_dialog_manager):
    fake_scenario = Mock()
    fake_scenario.get_lists = AsyncMock(return_value=([], {}))

    monkeypatch.setattr(
        "app.bot.dialogs.select_list.getters.get_select_list_scenario",
        lambda mode: fake_scenario,
    )

    fake_dialog_manager.start_data = {"mode": ListSelectionMode.CREATE_TASK}

    data = await lists_getter_core(
        dialog_manager=fake_dialog_manager,
        di_session=Mock(),
    )

    SelectListWindowContract.model_validate(data)
    assert data["buttons"] == []


@pytest.mark.asyncio
async def test_lists_getter_missing_buttons_is_invalid(monkeypatch, fake_dialog_manager):
    fake_scenario = Mock()
    fake_scenario.get_lists = AsyncMock(return_value=(None, {}))

    monkeypatch.setattr(
        "app.bot.dialogs.select_list.getters.get_select_list_scenario",
        lambda mode: fake_scenario,
    )

    fake_dialog_manager.start_data = {"mode": ListSelectionMode.CREATE_TASK}

    data = await lists_getter_core(
        dialog_manager=fake_dialog_manager,
        di_session=Mock(),
    )

    with pytest.raises(ValidationError):
        SelectListWindowContract.model_validate(data)


@pytest.mark.asyncio
async def test_lists_getter_happy_path(monkeypatch, fake_dialog_manager):
    buttons = [
        {"list_id": 1, "list_title": "Inbox", "pos": "1."},
        {"list_id": 3, "list_title": "Work", "pos": "3."},
        {"list_id": 5, "list_title": "Buy", "pos": "3.1."},
        {"list_id": 4, "list_title": "Home", "pos": "4."},
    ]
    lists = {button["list_id"]: button["list_title"] for button in buttons}

    fake_scenario = FakeSelectListScenario(buttons, lists)

    monkeypatch.setattr(
        "app.bot.dialogs.select_list.getters.get_select_list_scenario",
        lambda mode: fake_scenario,
    )

    fake_dialog_manager.start_data = {"mode": ListSelectionMode.CREATE_TASK}

    session = AsyncMock()

    result = await lists_getter_core(
        dialog_manager=fake_dialog_manager,
        di_session=session,
    )

    assert result == {"buttons": buttons}
    assert "lists" in fake_dialog_manager.dialog_data
    assert fake_dialog_manager.dialog_data["lists"] == to_dialog_safe(lists)
    assert fake_scenario.called_with == (session, fake_dialog_manager)


@pytest.mark.asyncio
async def test_lists_getter_invalid_mode(fake_dialog_manager):
    fake_dialog_manager.start_data = {"mode": "unknown"}

    session = AsyncMock()

    with pytest.raises(ValueError):
        await lists_getter_core(
            dialog_manager=fake_dialog_manager,
            di_session=session,
        )


@pytest.mark.asyncio
async def test_lists_getter_without_mode(fake_dialog_manager):
    fake_dialog_manager.start_data = {}
    session = AsyncMock()

    with pytest.raises(KeyError):
        await lists_getter_core(
            dialog_manager=fake_dialog_manager,
            di_session=session,
        )
