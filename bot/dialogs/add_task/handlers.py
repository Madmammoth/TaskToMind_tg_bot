import logging

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button
from sqlalchemy.ext.asyncio import AsyncSession

from bot.dialogs.states import StartSG
from database.models import LevelEnum
from database.requests import add_task_with_stats_achievs_log
from locales.ru import PRIORITY_LABELS, URGENCY_LABELS

logger = logging.getLogger(__name__)


async def go_pass(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager
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
    logger.debug(
        "Установка приоритета задачи. Функция %s",
        go_priority.__name__
    )

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
    logger.debug(
        "Установка срочности задачи. Функция %s",
        go_urgency.__name__
    )
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
        widget: Button,
        dialog_manager: DialogManager,
):
    logger.debug(
        "Сохранение задачи. Функция %s",
        go_save_yes.__name__
    )
    session: AsyncSession = dialog_manager.middleware_data["session"]
    user_id = callback.from_user.id
    data = {**dialog_manager.start_data, **dialog_manager.dialog_data}
    message_id = data["message_id"]
    await add_task_with_stats_achievs_log(session, user_id, data)
    await callback.bot.send_message(
        chat_id=callback.message.chat.id,
        text="Задача успешно добавлена!",
        reply_to_message_id=message_id,
    )
    await callback.message.delete()
    await dialog_manager.start(state=StartSG.start_window,
                               mode=StartMode.RESET_STACK)


async def go_cancel_yes(
        callback: CallbackQuery,
        widget: Button,
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
    await callback.message.delete()
    await dialog_manager.start(state=StartSG.start_window,
                               mode=StartMode.RESET_STACK)
