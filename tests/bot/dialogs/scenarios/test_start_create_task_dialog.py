import pytest

from app.bot.dialogs.common.handlers import update_dialog_data_from_start
from app.bot.dialogs.start.handlers import go_create_task
from app.bot.dialogs.states import CreateTaskDialogSG
from tests.bot.mocks import MockButton


@pytest.mark.asyncio
async def test_start_from_predict_dialog(dm, mock_callback):
    dm.dialog_data = {
        "message_id": 777,
        "text": "Новая задача\nОписание задачи",
    }
    btn = MockButton(widget_id="new_task", text="Новая задача")

    await go_create_task(mock_callback, btn, dm)  # noqa

    assert dm.last_state == CreateTaskDialogSG.add_task_window
    assert dm.start_data["message_id"] == 777
    assert dm.start_data["task_title"] == "Новая задача"
    assert dm.start_data["task_description"] == "Описание задачи"
    assert dm.start_data["selected_list_title"] == "Входящие"
    assert dm.start_data["priority"] == {"__enum__": "LevelEnum.LOW"}
    assert dm.start_data["priority_label"] == "Низкий"
    assert dm.start_data["urgency"] == {"__enum__": "LevelEnum.LOW"}
    assert dm.start_data["urgency_label"] == "Низкая"
    assert dm.start_data["mode"] == "create_task"

    await update_dialog_data_from_start(dm.start_data, dm)

    assert dm.last_state == CreateTaskDialogSG.add_task_window
    assert dm.dialog_data["message_id"] == 777
    assert dm.dialog_data["task_title"] == "Новая задача"
    assert dm.dialog_data["task_description"] == "Описание задачи"
    assert dm.dialog_data["selected_list_title"] == "Входящие"
    assert dm.dialog_data["priority"] == {"__enum__": "LevelEnum.LOW"}
    assert dm.dialog_data["priority_label"] == "Низкий"
    assert dm.dialog_data["urgency"] == {"__enum__": "LevelEnum.LOW"}
    assert dm.dialog_data["urgency_label"] == "Низкая"
    assert dm.dialog_data["mode"] == "create_task"
