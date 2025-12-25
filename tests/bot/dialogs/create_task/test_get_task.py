from typing import Optional

import pytest
from pydantic import BaseModel, ValidationError

from app.bot.dialogs.create_task.getters import get_task


class AddTaskWindowContract(BaseModel):
    task_title: str
    selected_list_title: str
    priority_label: str
    urgency_label: str
    task_description: Optional[str] = None
    deadline: Optional[str] = None
    remind: Optional[str] = None
    repeat: Optional[str] = None
    checklist: Optional[str] = None
    tag: Optional[str] = None


@pytest.mark.asyncio
async def test_window_contract_minimal(fake_dialog_manager):
    fake_dialog_manager.dialog_data = {
        "task_title": "Новая задача",
        "selected_list_title": "Название списка",
        "priority_label": "Низкий",
        "urgency_label": "Низкая",
    }

    data = await get_task(fake_dialog_manager)

    AddTaskWindowContract.model_validate(data)


@pytest.mark.asyncio
async def test_window_contract_insufficient(fake_dialog_manager):
    fake_dialog_manager.dialog_data = {
        "task_title": "Новая задача",
        "selected_list_title": "Название списка",
        "urgency_label": "Низкая",
    }

    data = await get_task(fake_dialog_manager)

    with pytest.raises(ValidationError):
        AddTaskWindowContract.model_validate(data)


@pytest.mark.asyncio
async def test_window_contract_wrong(fake_dialog_manager):
    fake_dialog_manager.dialog_data = {
        "task_title": "Новая задача",
        "list_title": "Название списка",
        "priority_level": "Низкий",
        "urgency_level": "Низкая",
    }

    data = await get_task(fake_dialog_manager)

    with pytest.raises(ValidationError):
        AddTaskWindowContract.model_validate(data)


@pytest.mark.asyncio
async def test_minimal_data(fake_dialog_manager):
    fake_dialog_manager.dialog_data = {
        "task_title": "Новая задача",
        "selected_list_title": "Название списка",
        "priority_label": "Низкий",
        "urgency_label": "Низкая",
    }

    data = await get_task(fake_dialog_manager)

    assert data["task_title"] == "Новая задача"
    assert data.get("task_description") is None
    assert data["selected_list_title"] == "Название списка"
    assert data["priority_label"] == "Низкий"
    assert data["urgency_label"] == "Низкая"


@pytest.mark.asyncio
async def test_with_description(fake_dialog_manager):
    fake_dialog_manager.dialog_data = {
        "task_title": "Новая задача",
        "task_description": "Описание задачи",
        "selected_list_title": "Название списка",
        "priority_label": "Низкий",
        "urgency_label": "Низкая",
    }

    data = await get_task(fake_dialog_manager)

    assert data["task_title"] == "Новая задача"
    assert data["task_description"] == "Описание задачи"
    assert data["selected_list_title"] == "Название списка"
    assert data["priority_label"] == "Низкий"
    assert data["urgency_label"] == "Низкая"
