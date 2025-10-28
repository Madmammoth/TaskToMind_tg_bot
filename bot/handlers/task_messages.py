import logging
from typing import Any

from aiogram import F, Router
from aiogram.types import Message
from aiogram_dialog import DialogManager, ShowMode

from bot.dialogs.states import GetTaskDialogSG
from database.models import LevelEnum
from locales.ru import PRIORITY_LABELS, URGENCY_LABELS

logger = logging.getLogger(__name__)

task_messages_router = Router()


def split_title_and_description(text: str):
    cleaned = text.strip()
    if not cleaned:
        return "Моя задача", None
    lines = cleaned.split("\n", 1)
    title = lines[0].strip()
    description = lines[1].strip() if len(lines) > 1 else None
    return title, description


def make_default_task_data(message_id, task_text) -> dict[str, str | Any]:
    task_title, task_description = split_title_and_description(task_text)
    task_data = {
        "message_id": message_id,
        "task_title": task_title,
        "task_description": task_description,
        "list_title": "Входящие",
        "priority": LevelEnum.LOW,
        "priority_label": PRIORITY_LABELS[LevelEnum.LOW],
        "urgency": LevelEnum.LOW,
        "urgency_label": URGENCY_LABELS[LevelEnum.LOW],
    }
    return task_data


@task_messages_router.message(F.text)
async def get_task_handler(message: Message, dialog_manager: DialogManager):
    logger.debug("Апдейт здесь")
    task_data = make_default_task_data(message.message_id, message.html_text)
    await dialog_manager.start(
        state=GetTaskDialogSG.add_task_window,
        data=task_data,
        show_mode=ShowMode.DELETE_AND_SEND,
    )
