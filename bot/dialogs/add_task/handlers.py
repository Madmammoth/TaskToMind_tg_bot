import logging
from typing import cast

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode, SubManager, ShowMode
from aiogram_dialog.widgets.kbd import Button
from sqlalchemy.ext.asyncio import AsyncSession

from bot.dialogs.states import StartSG, GetTaskDialogSG
from database.models import LevelEnum
from database.requests import add_task_with_stats_achievs_log
from locales.ru import PRIORITY_LABELS, URGENCY_LABELS

logger = logging.getLogger(__name__)


async def go_pass(
        callback: CallbackQuery,
        _widget: Button,
        _dialog_manager: DialogManager
):
    logger.debug(
        "Заглушка для перехода в другое окно. Функция %s",
        go_pass.__name__
    )
    await callback.answer(
        "Когда-нибудь тут будет переход в другое окно"
    )


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
    dialog_manager.dialog_data["priority"] = priority_enum
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
    dialog_manager.dialog_data["urgency"] = urgency_enum
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
    logger.debug(
        "Сохранение задачи. Функция %s",
        go_save_yes.__name__
    )
    session: AsyncSession = dialog_manager.middleware_data["session"]
    user_id = callback.from_user.id
    message_id = dialog_manager.dialog_data["message_id"]
    await add_task_with_stats_achievs_log(
        session=session,
        user_id=user_id,
        task_data=dialog_manager.dialog_data,
    )
    await callback.bot.send_message(
        chat_id=callback.message.chat.id,
        text="Задача успешно добавлена!",
        reply_to_message_id=message_id,
    )
    await callback.message.delete()
    await dialog_manager.start(state=StartSG.start_window,
                               mode=StartMode.RESET_STACK)


async def add_task_dialog_start(start_data, dialog_manager: DialogManager):
    logger.debug("Объединение стартового и основного словарей диалога")
    logger.debug("Исходные словари:")
    logger.debug("start_data: %s", start_data)
    logger.debug("dialog_manager.dialog_data: %s", dialog_manager.dialog_data)

    dialog_manager.dialog_data.update(start_data)

    logger.debug("Полученный словарь:")
    logger.debug("dialog_manager.dialog_data: %s", dialog_manager.dialog_data)


async def go_cancel_yes(
        callback: CallbackQuery,
        _widget: Button,
        dialog_manager: DialogManager
):
    logger.debug(
        "Отмена добавления задачи. Функция %s",
        go_cancel_yes.__name__
    )
    message_id = dialog_manager.start_data["message_id"]
    await callback.bot.send_message(
        chat_id=callback.message.chat.id,
        text="Добавление задачи было отменено",
        reply_to_message_id=message_id,
    )
    await dialog_manager.start(
        state=StartSG.start_window,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.DELETE_AND_SEND,
    )


async def go_selected_list(
        callback: CallbackQuery,
        _widget: Button,
        dialog_manager: DialogManager,
):
    logger.debug("Установка списка задач...")
    sub_manager = cast(SubManager, dialog_manager)
    dialog_manager = sub_manager.manager
    list_id = sub_manager.item_id
    logger.debug("Нажата кнопка для item_id=%s", list_id)
    lists = dialog_manager.dialog_data.get("lists", {})
    list_title = lists.get(list_id)
    if not list_title:
        await callback.answer("Ошибка: список не найден.")
        return
    dialog_manager.dialog_data.update({
        "list_id": int(list_id),
        "list_title": list_title,
    })
    await callback.answer(f"Выбран список: {list_title}")
    await dialog_manager.switch_to(state=GetTaskDialogSG.add_task_window)
    logger.debug(
        "Установлен список задач id=%s, title=%s",
        list_id, list_title
    )
