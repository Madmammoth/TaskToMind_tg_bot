from unittest.mock import AsyncMock

import pytest

from app.bot.dialogs.create_task.handlers import correct_text_task_input
from tests.bot.mocks import MockMessage


@pytest.mark.asyncio
async def test_correct_data(fake_dialog_manager):
    message = MockMessage(message_id=10, text="Test task\nTest description")
    wgt = AsyncMock()
    txt = message.text

    await correct_text_task_input(message, wgt, fake_dialog_manager, txt)

    assert fake_dialog_manager.dialog_data == {
        "message_id": 10,
        "task_title": "Test task",
        "task_description": "Test description",
        "selected_list_title": "Входящие",
        "priority": {"__enum__": "LevelEnum.LOW"},
        "priority_label": "Низкий",
        "urgency": {"__enum__": "LevelEnum.LOW"},
        "urgency_label": "Низкая",
    }


@pytest.mark.asyncio
async def test_empty_text(fake_dialog_manager):
    message = MockMessage(message_id=77, text="\t\n")
    wgt = AsyncMock()
    txt = message.text

    await correct_text_task_input(message, wgt, fake_dialog_manager, txt)

    assert fake_dialog_manager.dialog_data == {
        "message_id": 77,
        "task_title": "Новая задача",
        "task_description": None,
        "selected_list_title": "Входящие",
        "priority": {"__enum__": "LevelEnum.LOW"},
        "priority_label": "Низкий",
        "urgency": {"__enum__": "LevelEnum.LOW"},
        "urgency_label": "Низкая",
    }
