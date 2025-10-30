import logging
from typing import cast

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, SubManager, ShowMode
from aiogram_dialog.widgets.input import ManagedTextInput, MessageInput
from aiogram_dialog.widgets.kbd import Button
from sqlalchemy.ext.asyncio import AsyncSession

from bot.dialogs.states import TaskManagementDialogSG, TaskListsDialogSG
from database.requests import add_list_with_stats_achievs_log

logger = logging.getLogger(__name__)


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
    await dialog_manager.switch_to(
        state=TaskManagementDialogSG.main_tasks_window
    )
    logger.debug(
        "Установлен список задач id=%s, title=%s",
        list_id, list_title
    )


async def correct_title_list_input(
        message: Message,
        _widget: ManagedTextInput,
        dialog_manager: DialogManager,
        _text: str,
):
    logger.debug("Переход в окно добавления списка")
    lists = dialog_manager.dialog_data.get("lists", {})
    list_title = message.html_text
    existing_titles = [v.lower() for v in lists.values()]
    if list_title.lower() in existing_titles:
        await message.answer("Список с таким названием уже существует")
        await dialog_manager.switch_to(
            state=TaskListsDialogSG.input_list_title_window,
            show_mode=ShowMode.DELETE_AND_SEND,
        )
        return
    dialog_manager.dialog_data.update({
        "message_id": message.message_id,
        "new_list_title": list_title
    })
    await dialog_manager.switch_to(
        state=TaskListsDialogSG.add_list_window,
        show_mode=ShowMode.DELETE_AND_SEND,
    )


async def empty_title_input(
        message: Message,
        _widget: ManagedTextInput,
        dialog_manager: DialogManager,
        _error: ValueError
):
    await message.answer("Тут же нет текста 🤔")
    await dialog_manager.switch_to(
        state=TaskListsDialogSG.input_list_title_window,
        show_mode=ShowMode.DELETE_AND_SEND,
    )


async def wrong_title_list_input(
        message: Message,
        _widget: MessageInput,
        dialog_manager: DialogManager,
):
    logger.debug("Неправильный ввод названия списка")
    await message.answer("Пожалуйста, отправь именно текстовое сообщение!")
    await dialog_manager.switch_to(
        state=TaskListsDialogSG.input_list_title_window,
        show_mode=ShowMode.DELETE_AND_SEND,
    )


async def go_save_yes(
        callback: CallbackQuery,
        _widget: Button,
        dialog_manager: DialogManager
):
    logger.debug("Сохранение списка задач")
    session: AsyncSession = dialog_manager.middleware_data["session"]
    user_id = callback.from_user.id
    message_id = dialog_manager.dialog_data["message_id"]
    await add_list_with_stats_achievs_log(
        session=session,
        user_id=user_id,
        list_data=dialog_manager.dialog_data,
    )
    await callback.bot.send_message(
        chat_id=callback.message.chat.id,
        text="Список задач успешно добавлен!",
        reply_to_message_id=message_id,
    )
    await dialog_manager.switch_to(
        state=TaskListsDialogSG.main_lists_window,
        show_mode=ShowMode.DELETE_AND_SEND,
    )


async def go_cancel_yes(
        callback: CallbackQuery,
        _widget: Button,
        dialog_manager: DialogManager
):
    logger.debug("Отмена создания списка")
    message_id = dialog_manager.dialog_data["message_id"]
    await callback.bot.send_message(
        chat_id=callback.message.chat.id,
        text="Создание списка было отменено",
        reply_to_message_id=message_id,
    )
    await dialog_manager.switch_to(
        state=TaskListsDialogSG.main_lists_window,
        show_mode=ShowMode.DELETE_AND_SEND,
    )
