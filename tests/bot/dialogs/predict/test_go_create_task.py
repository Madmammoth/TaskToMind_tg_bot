from typing import Optional

import pytest
from pydantic import BaseModel

from app.bot.dialogs.start.handlers import go_create_task
from app.bot.dialogs.states import CreateTaskDialogSG
from tests.bot.conftest import mock_callback
from tests.bot.mocks import MockButton


class CreateTaskStartData(BaseModel):
    message_id: int
    task_title: str
    task_description: Optional[str] = None
    selected_list_title: str
    priority: dict[str, str]
    priority_label: str
    urgency: dict[str, str]
    urgency_label: str
    mode: str


@pytest.mark.asyncio
async def test_with_correct_data(fake_dialog_manager, mock_callback):
    fake_dialog_manager.dialog_data = {
        "message_id": 777,
        "text": "Новая задача\nОписание задачи",
    }
    btn = MockButton(widget_id="new_task", text="Новая задача")

    await go_create_task(mock_callback, btn, fake_dialog_manager)  # noqa

    assert dm.start_data["mode"] == "create_task"
    assert fake_dialog_manager.last_state == CreateTaskDialogSG.add_task_window
    assert fake_dialog_manager.start_data["message_id"] == 777
    assert fake_dialog_manager.start_data["task_title"] == "Новая задача"
    assert fake_dialog_manager.start_data["task_description"] == "Описание задачи"
    assert fake_dialog_manager.start_data["selected_list_title"] == "Входящие"
    assert fake_dialog_manager.start_data["priority"] == {"__enum__": "LevelEnum.LOW"}
    assert fake_dialog_manager.start_data["priority_label"] == "Низкий"
    assert fake_dialog_manager.start_data["urgency"] == {"__enum__": "LevelEnum.LOW"}
    assert fake_dialog_manager.start_data["urgency_label"] == "Низкая"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "dialog_data",
    [
        {},
        {"message_id": 777},
        {"text": "abc"}
    ],
)
async def test_missing_required_input(fake_dialog_manager, mock_callback, dialog_data):
    fake_dialog_manager.dialog_data = dialog_data
    btn = MockButton(widget_id="new_task", text="Новая задача")

    with pytest.raises(ValueError):
        await go_create_task(mock_callback, btn, fake_dialog_manager)  # noqa


@pytest.mark.asyncio
async def test_start_data_contract(fake_dialog_manager, mock_callback):
    fake_dialog_manager.dialog_data = {
        "message_id": 777,
        "text": "Новая задача\nОписание задачи",
    }
    btn = MockButton(widget_id="new_task", text="Новая задача")

    await go_create_task(mock_callback, btn, fake_dialog_manager)  # noqa

    CreateTaskStartData.model_validate(fake_dialog_manager.start_data)
