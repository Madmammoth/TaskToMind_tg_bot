import logging

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button

from bot.dialogs.states import StartSG
from database.db import fake_database

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
    priority = await widget.text.render_text(
        data=dialog_manager.dialog_data, manager=dialog_manager
    )
    dialog_manager.dialog_data["priority"] = priority
    await callback.answer(f"Установлен {priority.lower()} приоритет задачи")


async def go_urgency(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager
):
    logger.debug(
        "Установка срочности задачи. Функция %s",
        go_urgency.__name__
    )
    urgency = await widget.text.render_text(
        data=dialog_manager.dialog_data, manager=dialog_manager
    )
    dialog_manager.dialog_data["urgency"] = urgency
    await callback.answer(f"Установлена {urgency.lower()} срочность задачи")


async def go_save_yes(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager
):
    logger.debug(
        "Сохранение задачи. Функция %s",
        go_save_yes.__name__
    )
    user_id = callback.from_user.id
    username = callback.from_user.username
    first_name = callback.from_user.first_name
    message_id = dialog_manager.start_data["message_id"]
    data = {**dialog_manager.start_data, **dialog_manager.dialog_data}
    fake_database[user_id][username] = username
    fake_database[user_id][first_name] = first_name
    fake_database[user_id]["lists"][data["in_list"]][message_id] = {
        "task": data["task"],
        "priority": data.get("priority"),
        "urgency": data.get("urgency"),
        "deadline": data.get("deadline"),
        "deadline_show": data.get("deadline_show", False),
        "duration": data.get("duration"),
        "duration_show": data.get("duration_show", False),
        "remind": data.get("remind"),
        "remind_show": data.get("remind_show", False),
        "repeat": data.get("repeat"),
        "repeat_show": data.get("repeat_show", False),
        "checklist": data.get("checklist"),
        "checklist_show": data.get("checklist_show", False),
        "tag": data.get("tag"),
        "tag_show": data.get("tag_show", False),
    }
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
