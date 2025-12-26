from unittest.mock import Mock, AsyncMock

import pytest

from app.bot.dialogs.enums import ListSelectionMode
from app.bot.dialogs.select_list.handlers import select_list_core
from tests.bot.mocks import FakeSubManager


@pytest.mark.asyncio
async def test_select_list_core_happy_path(monkeypatch, fake_dialog_manager, mock_session):
    fake_dialog_manager.start_data = {"mode": ListSelectionMode.CREATE_TASK}
    fake_dialog_manager.dialog_data = {
        "lists": {"__int__1": "Inbox", "__int__3": "Work", "__int__5": "Buy", "__int__4": "Home"}
    }
    sub_manager = FakeSubManager(manager=fake_dialog_manager, item_id="3")

    fake_result = {
        "selected_list_id": 3,
        "selected_list_title": "Work",
    }

    fake_scenario = Mock()
    fake_scenario.apply = AsyncMock(return_value=fake_result)

    monkeypatch.setattr(
        "app.bot.dialogs.select_list.handlers.get_select_list_scenario",
        lambda mode: fake_scenario,
    )

    session = mock_session

    await select_list_core(
        callback=Mock(),
        _widget=Mock(),
        dialog_manager=sub_manager,  # type: ignore
        session=session,
    )

    fake_scenario.apply.assert_called_once_with(
        session=session,
        dialog_manager=fake_dialog_manager,
        list_id=3,
    )

    assert fake_dialog_manager.finished is True
    assert fake_dialog_manager.result == fake_result


@pytest.mark.asyncio
async def test_select_list_core_passes_mode_to_scenario(monkeypatch, fake_dialog_manager):
    captured_mode = None

    def fake_get_scenario(mode):
        nonlocal captured_mode
        captured_mode = mode
        scenario = Mock()
        scenario.apply = AsyncMock(return_value={})
        return scenario

    monkeypatch.setattr(
        "app.bot.dialogs.select_list.handlers.get_select_list_scenario",
        fake_get_scenario,
    )

    fake_dialog_manager.start_data = {"mode": ListSelectionMode.EDIT_LIST}
    fake_dialog_manager.dialog_data = {
        "lists": {"__int__1": "Inbox", "__int__3": "Work", "__int__5": "Buy", "__int__4": "Home"}
    }
    sub_manager = FakeSubManager(manager=fake_dialog_manager, item_id="3")

    await select_list_core(
        callback=Mock(),
        _widget=Mock(),
        dialog_manager=sub_manager,  # type: ignore
        session=Mock(),
    )

    assert captured_mode == ListSelectionMode.EDIT_LIST


@pytest.mark.asyncio
async def test_select_list_core_missing_mode(fake_dialog_manager):
    fake_dialog_manager.start_data = {}
    fake_dialog_manager.dialog_data = {
        "lists": {"__int__1": "Inbox", "__int__3": "Work", "__int__5": "Buy", "__int__4": "Home"}
    }
    sub_manager = FakeSubManager(manager=fake_dialog_manager, item_id="3")

    with pytest.raises(KeyError):
        await select_list_core(
            callback=Mock(),
            _widget=Mock(),
            dialog_manager=sub_manager,  # type: ignore
            session=Mock(),
        )
