import pytest

from app.bot.dialogs.common.handlers import update_dialog_data_from_start
from app.bot.dialogs.start.handlers import go_create_task
from app.bot.dialogs.states import CreateTaskDialogSG
from tests.bot.mocks import MockButton


@pytest.mark.asyncio
async def test_start_from_predict_dialog(fake_dialog_manager, mock_callback):
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

    await update_dialog_data_from_start(fake_dialog_manager.start_data, fake_dialog_manager)

    assert dm.dialog_data["mode"] == "create_task"
    assert fake_dialog_manager.last_state == CreateTaskDialogSG.add_task_window
    assert fake_dialog_manager.dialog_data["message_id"] == 777
    assert fake_dialog_manager.dialog_data["task_title"] == "Новая задача"
    assert fake_dialog_manager.dialog_data["task_description"] == "Описание задачи"
    assert fake_dialog_manager.dialog_data["selected_list_title"] == "Входящие"
    assert fake_dialog_manager.dialog_data["priority"] == {"__enum__": "LevelEnum.LOW"}
    assert fake_dialog_manager.dialog_data["priority_label"] == "Низкий"
    assert fake_dialog_manager.dialog_data["urgency"] == {"__enum__": "LevelEnum.LOW"}
    assert fake_dialog_manager.dialog_data["urgency_label"] == "Низкая"
