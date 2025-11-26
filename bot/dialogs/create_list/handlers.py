import logging
from typing import cast

from aiogram.types import Message, CallbackQuery
from aiogram_dialog import DialogManager, ShowMode, SubManager
from aiogram_dialog.widgets.input import ManagedTextInput, MessageInput
from aiogram_dialog.widgets.kbd import Button
from sqlalchemy.ext.asyncio import AsyncSession

from bot.dialogs.states import CreateListDialogSG
from database.orchestration.task_list import add_list_with_stats_achievs_log

logger = logging.getLogger(__name__)


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
            state=CreateListDialogSG.input_list_title_window,
            show_mode=ShowMode.DELETE_AND_SEND,
        )
        return
    dialog_manager.dialog_data.update({
        "message_id": str(message.message_id),
        "new_list_title": list_title,
        "show_lists_mode": "add_list",
    })
    await dialog_manager.switch_to(
        state=CreateListDialogSG.add_list_window,
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
        state=CreateListDialogSG.input_list_title_window,
        show_mode=ShowMode.DELETE_AND_SEND,
    )


async def wrong_title_list_input(
        message: Message,
        _widget: MessageInput,
        dialog_manager: DialogManager,
):
    logger.debug("Неправильный ввод названия списка")
    await message.answer("Пожалуйста, отправь именно текстовое сообщение!")
    await dialog_manager.show(ShowMode.DELETE_AND_SEND)
    dialog_manager.show_mode = ShowMode.NO_UPDATE


async def go_insert_in_list(
        _callback: CallbackQuery,
        _widget: Button,
        dialog_manager: DialogManager
):
    logger.debug("Вложение списка задач в другой список задач")
    dialog_manager.dialog_data["show_lists_mode"] = "add_in_list"
    await dialog_manager.switch_to(
        state=CreateListDialogSG.in_list_window,
    )


async def go_save_new_list(
        callback: CallbackQuery,
        _widget: Button,
        dialog_manager: DialogManager
):
    logger.debug("Сохранение списка задач")
    session: AsyncSession = dialog_manager.middleware_data["session"]
    user_id = callback.from_user.id
    message_id = int(dialog_manager.dialog_data["message_id"])
    list_id = await add_list_with_stats_achievs_log(
        session=session,
        user_id=user_id,
        list_data=dialog_manager.dialog_data,
    )
    list_title = dialog_manager.dialog_data.get("new_list_title")
    in_list_id = dialog_manager.dialog_data.get("in_list_id")
    in_list_title = dialog_manager.dialog_data.get("in_list_title")
    result = {
        "list_id": list_id,
        "list_title": list_title,
        "in_list_id": in_list_id,
        "in_list_title": in_list_title,
    }
    logger.debug("result=%s", result)
    await callback.bot.send_message(
        chat_id=callback.message.chat.id,
        text="Список задач успешно добавлен!",
        reply_to_message_id=message_id,
    )
    await dialog_manager.done(
        result=result,
        show_mode=ShowMode.DELETE_AND_SEND,
    )


async def clear_in_list(
        _callback: CallbackQuery,
        _widget: Button,
        dialog_manager: DialogManager
):
    logger.debug("Возврат статуса корневого списка для нового списка")
    dialog_manager.dialog_data.update({"in_list_id": None,
                                       "in_list_title": None})


async def go_cancel_yes(
        callback: CallbackQuery,
        _widget: Button,
        dialog_manager: DialogManager
):
    logger.debug("Отмена создания списка")
    message_id = int(dialog_manager.dialog_data["message_id"])
    await callback.bot.send_message(
        chat_id=callback.message.chat.id,
        text="Создание списка было отменено",
        reply_to_message_id=message_id,
    )
    await dialog_manager.done(show_mode=ShowMode.DELETE_AND_SEND)


async def select_list(
        callback: CallbackQuery,
        _widget: Button,
        dialog_manager: DialogManager,
):
    logger.debug("Выбор родительского списка...")
    sub_manager = cast(SubManager, dialog_manager)
    dialog_manager = sub_manager.manager
    list_id = sub_manager.item_id
    logger.debug("Нажата кнопка для item_id=%s", list_id)
    lists = dialog_manager.dialog_data.get("lists", {})
    dialog_manager.dialog_data.update({"in_list_id": str(list_id),
                                       "in_list_title": lists[list_id]})
    logger.debug("Словарь dialog_data:")
    logger.debug(dialog_manager.dialog_data)
    await callback.answer(f"Выбран список: {lists[list_id]}")
    await dialog_manager.switch_to(
        state=CreateListDialogSG.add_list_window
    )
    logger.debug(
        "Установлен список задач id=%s, title=%s",
        list_id, lists[list_id]
    )
