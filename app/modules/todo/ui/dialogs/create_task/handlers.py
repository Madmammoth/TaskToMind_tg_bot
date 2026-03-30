import logging
from typing import Any

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import ManagedTextInput, MessageInput
from aiogram_dialog.widgets.kbd import Button
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.todo.ui.dialogs.states import CreateTaskDialogSG
from app.modules.todo.models import LevelEnum
from app.modules.todo.facade.task import add_task_with_stats_achievs_log
from app.core.locales.ru import PRIORITY_LABELS, URGENCY_LABELS
from app.core.utils.dialog_serialization import to_dialog_safe, from_dialog_safe

logger = logging.getLogger(__name__)


async def go_priority(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager
):
    logger.debug("Установка приоритета задачи...")

    priority_id = widget.widget_id

    try:
        priority_enum = LevelEnum(priority_id)
    except ValueError:
        await callback.answer("Неизвестный уровень приоритета.")
        return

    priority_text = await widget.text.render_text(
        data=dialog_manager.dialog_data, manager=dialog_manager
    )
    dialog_manager.dialog_data["priority"] = to_dialog_safe(priority_enum)
    dialog_manager.dialog_data["priority_label"] = (
        PRIORITY_LABELS.get(priority_enum)
    )
    await callback.answer(f"Установлен {priority_text.lower()} "
                          "приоритет задачи")
    logger.debug("Приоритет задачи установлен: %s", priority_enum.value)


async def go_urgency(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager
):
    logger.debug("Установка срочности задачи...")
    urgency_id = widget.widget_id

    try:
        urgency_enum = LevelEnum(urgency_id)
    except ValueError:
        await callback.answer("Неизвестный уровень срочности.")
        return

    urgency_text = await widget.text.render_text(
        data=dialog_manager.dialog_data, manager=dialog_manager
    )
    dialog_manager.dialog_data["urgency"] = to_dialog_safe(urgency_enum)
    dialog_manager.dialog_data["urgency_label"] = (
        URGENCY_LABELS.get(urgency_enum)
    )
    await callback.answer(f"Установлена {urgency_text.lower()} "
                          "срочность задачи")
    logger.debug("Срочность задачи установлена: %s", urgency_enum)


async def go_save_yes(
        callback: CallbackQuery,
        _widget: Button,
        dialog_manager: DialogManager,
):
    logger.debug("Сохранение задачи пользователем...")
    user_id = callback.from_user.id
    logger.debug("...id=%d", user_id)
    session: AsyncSession = dialog_manager.middleware_data["session"]
    task_data = from_dialog_safe(dialog_manager.dialog_data)
    message_id = task_data["message_id"]

    await add_task_with_stats_achievs_log(
        session=session,
        user_id=user_id,
        task_data=task_data,
    )

    await callback.bot.send_message(
        chat_id=callback.message.chat.id,
        text="Задача успешно добавлена!",
        reply_to_message_id=message_id,
    )
    logger.debug("Задача создана пользователем id=%d", user_id)
    await dialog_manager.done(
        result={"1": "1"},
        show_mode=ShowMode.DELETE_AND_SEND
    )


async def go_cancel_yes(
        callback: CallbackQuery,
        _widget: Button,
        dialog_manager: DialogManager
):
    logger.debug(
        "Отмена добавления задачи. Функция %s",
        go_cancel_yes.__name__
    )
    message_id = dialog_manager.dialog_data["message_id"]
    await callback.bot.send_message(
        chat_id=callback.message.chat.id,
        text="Добавление задачи было отменено",
        reply_to_message_id=message_id,
    )
    await dialog_manager.done(show_mode=ShowMode.DELETE_AND_SEND)


def split_title_and_description(text: str):
    cleaned = text.strip()
    if not cleaned:
        return "Новая задача", None
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
        "selected_list_title": "Входящие",
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
    dialog_manager.dialog_data.update(to_dialog_safe(task_data))

    await dialog_manager.switch_to(
        state=CreateTaskDialogSG.add_task_window,
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
        state=CreateTaskDialogSG.input_task_window,
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
        state=CreateTaskDialogSG.input_task_window,
        show_mode=ShowMode.DELETE_AND_SEND,
    )


async def update_dialog_data_from_result(
        _start_data,
        result,
        dialog_manager: DialogManager,
):
    logger.debug(
        "Передача result=%s из предыдущего диалога в диалог создания задачи",
        result,
    )
    if type(result) is dict:
        dialog_manager.dialog_data.update(result),
        await dialog_manager.switch_to(
            state=CreateTaskDialogSG.add_task_window,
            show_mode=ShowMode.DELETE_AND_SEND,
        )
        logger.debug(
            "Переход в окно настройки создаваемой задачи диалога создания задачи"
        )
    else:
        logger.debug("Переход в окно выбора списка диалога создания задачи")
