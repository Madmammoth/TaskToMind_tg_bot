import logging
from typing import Any

from aiogram.types import Message, CallbackQuery
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import MessageInput, ManagedTextInput
from aiogram_dialog.widgets.kbd import Button

from bot.dialogs.states import GetTaskDialogSG, StartSG
from database.models import LevelEnum
from locales.ru import PRIORITY_LABELS, URGENCY_LABELS

logger = logging.getLogger(__name__)


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


def empty_text_check(text: str) -> str:
    if text.strip():
        return text
    raise ValueError


async def correct_text_task_input(
        message: Message,
        _widget: ManagedTextInput,
        dialog_manager: DialogManager,
        _text: str,
):
    logger.debug("Запуск диалога добавления задачи")
    task_data = make_default_task_data(message.message_id, message.html_text)
    await dialog_manager.start(
        state=GetTaskDialogSG.add_task_window,
        data=task_data,
        show_mode=ShowMode.DELETE_AND_SEND,
    )


async def empty_text_input(
        message: Message,
        _widget: ManagedTextInput,
        dialog_manager: DialogManager,
        _error: ValueError
):
    await message.answer("Тут же нет текста 🤔")
    await dialog_manager.switch_to(
        state=StartSG.input_task_window,
        show_mode=ShowMode.DELETE_AND_SEND,
    )


async def wrong_text_task_input(
        message: Message,
        _widget: MessageInput,
        dialog_manager: DialogManager,
):
    logger.debug("Неправильный ввод текста задачи")
    await message.answer("Пожалуйста, отправь именно текстовое сообщение!")
    await dialog_manager.switch_to(
        state=StartSG.input_task_window,
        show_mode=ShowMode.DELETE_AND_SEND,
    )


async def go_settings(
        callback: CallbackQuery,
        _widget: Button,
        _dialog_manager: DialogManager
):
    logger.debug(
        "Заглушка-переход в окно настроек. Функция %s",
        go_settings.__name__
    )
    await callback.answer(
        "Когда-нибудь тут будет переход в настройки бота"
    )


async def go_features(
        callback: CallbackQuery,
        _widget: Button,
        _dialog_manager: DialogManager
):
    logger.debug(
        "Заглушка-переход в окно возможностей бота. Функция %s",
        go_features.__name__
    )
    await callback.answer(
        "Когда-нибудь тут будет переход к описанию возможностей бота"
    )


async def go_support(
        callback: CallbackQuery,
        _widget: Button,
        _dialog_manager: DialogManager
):
    logger.debug(
        "Заглушка-переход в окно технической поддержки. Функция %s",
        go_support.__name__
    )
    await callback.answer(
        "Когда-нибудь тут будет соединение с технической поддержкой"
    )
