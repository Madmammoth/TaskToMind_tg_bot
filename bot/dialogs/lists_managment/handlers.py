import logging
from typing import cast

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, SubManager, ShowMode
from aiogram_dialog.widgets.input import ManagedTextInput, MessageInput
from aiogram_dialog.widgets.kbd import Button
from sqlalchemy.ext.asyncio import AsyncSession

from bot.dialogs.states import (
    TaskListsDialogSG,
    TaskSettingsDialogSG,
)
from database.requests import (
    add_list_with_stats_achievs_log,
    delete_lists_with_stats_achievs_log,
)

logger = logging.getLogger(__name__)


async def go_selected_list(
        callback: CallbackQuery,
        _widget: Button,
        dialog_manager: DialogManager,
):
    logger.debug("Открытие списка задач...")
    sub_manager = cast(SubManager, dialog_manager)
    dialog_manager = sub_manager.manager
    list_id = sub_manager.item_id
    logger.debug("Нажата кнопка для item_id=%s", list_id)
    lists = dialog_manager.dialog_data.get("lists", {})
    dialog_manager.dialog_data["list_id"] = str(list_id)
    logger.debug("Словарь dialog_data:")
    logger.debug(dialog_manager.dialog_data)
    await callback.answer(f"Выбран список: {lists[list_id]}")
    await dialog_manager.switch_to(
        state=TaskListsDialogSG.list_with_tasks
    )
    logger.debug(
        "Установлен список задач id=%s, title=%s",
        list_id, lists[list_id]
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
        "message_id": str(message.message_id),
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


async def go_save_new_list(
        callback: CallbackQuery,
        _widget: Button,
        dialog_manager: DialogManager
):
    logger.debug("Сохранение списка задач")
    session: AsyncSession = dialog_manager.middleware_data["session"]
    user_id = callback.from_user.id
    message_id = int(dialog_manager.dialog_data["message_id"])
    await add_list_with_stats_achievs_log(
        session=session,
        user_id=user_id,
        list_data=dialog_manager.dialog_data,
    )
    dialog_manager.dialog_data.update({"in_list_id": None,
                                       "in_list_title": None})
    await callback.bot.send_message(
        chat_id=callback.message.chat.id,
        text="Список задач успешно добавлен!",
        reply_to_message_id=message_id,
    )
    await dialog_manager.switch_to(
        state=TaskListsDialogSG.main_lists_window,
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
    await dialog_manager.switch_to(
        state=TaskListsDialogSG.main_lists_window,
        show_mode=ShowMode.DELETE_AND_SEND,
    )


async def go_selected_task(
        callback: CallbackQuery,
        _widget: Button,
        dialog_manager: DialogManager,
):
    logger.debug("Открытие задачи...")
    sub_manager = cast(SubManager, dialog_manager)
    dialog_manager = sub_manager.manager
    task_id = str(sub_manager.item_id)
    logger.debug("Нажата кнопка для item_id=%s", task_id)
    tasks = dialog_manager.dialog_data.get("tasks", {})
    task_title = tasks.get(task_id)
    if not task_title:
        await callback.answer("Ошибка: задача не найдена.")
        return
    list_id = dialog_manager.dialog_data.get("list_id")
    list_title = dialog_manager.dialog_data.get("list_title")
    data = {
        "list_id": list_id,
        "list_title": list_title,
        "task_id": task_id,
        "task_title": task_title,
    }
    await callback.answer(f"Выбрана задача: {task_title}")
    await dialog_manager.start(
        state=TaskSettingsDialogSG.main_task_window,
        data=data
    )
    logger.debug(
        "Выбрана задача id=%s, title=%s",
        task_id, task_title
    )


async def go_pass(
        callback: CallbackQuery,
        _widget: Button,
        _dialog_manager: DialogManager
):
    logger.debug("Заглушка для кнопки-разделителя")
    await callback.answer("Эта кнопка пока не работает")


async def go_delete_lists(
        callback: CallbackQuery,
        _widget: Button,
        dialog_manager: DialogManager
):
    logger.debug("Апдейт здесь")
    logger.debug("Словарь dialog_data:")
    logger.debug(dialog_manager.dialog_data)
    selected_ids = dialog_manager.find("m_lists").get_checked()
    if not selected_ids:
        await callback.answer("Ничего не выбрано!", show_alert=True)
        return
    selected_ids = list(map(str, sorted(map(int, selected_ids))))
    logger.debug("selected_ids = %s", list(selected_ids))
    lists = dialog_manager.dialog_data.get("lists", {})
    logger.debug("lists = %s", lists)
    selected_lists = [
        (i, lst_id, lists[lst_id])
        for i, lst_id in enumerate(selected_ids, start=1)
        if lst_id in lists
    ]
    logger.debug("selected_lists = %s", selected_lists)
    dialog_manager.dialog_data["selected_lists"] = selected_lists
    logger.debug("Словарь dialog_data:")
    logger.debug(dialog_manager.dialog_data)
    await dialog_manager.switch_to(
        state=TaskListsDialogSG.ack_delete_lists_window)


async def go_delete_lists_yes(
        callback: CallbackQuery,
        _widget: Button,
        dialog_manager: DialogManager
):
    logger.debug("Апдейт здесь")
    logger.debug("Словарь dialog_data:")
    logger.debug(dialog_manager.dialog_data)
    session: AsyncSession = dialog_manager.middleware_data["session"]
    user_id = callback.from_user.id
    lists_to_delete = dialog_manager.dialog_data.get("selected_lists", {})
    list_ids_to_delete = [
        int(list_id) for i, list_id, title in lists_to_delete
    ]
    await delete_lists_with_stats_achievs_log(
        session, user_id, list_ids_to_delete
    )
    if len(lists_to_delete) == 1:
        await callback.answer("Список успешно удалён!")
    else:
        await callback.answer("Списки успешно удалены!")
    del dialog_manager.dialog_data["selected_lists"]
    await dialog_manager.switch_to(state=TaskListsDialogSG.main_lists_window)


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
    lists = dialog_manager.dialog_data.get("lists_for_parent", {})
    dialog_manager.dialog_data.update({"in_list_id": str(list_id),
                                       "in_list_title": lists[list_id]})
    logger.debug("Словарь dialog_data:")
    logger.debug(dialog_manager.dialog_data)
    await callback.answer(f"Выбран список: {lists[list_id]}")
    await dialog_manager.switch_to(
        state=TaskListsDialogSG.add_list_window
    )
    logger.debug(
        "Установлен список задач id=%s, title=%s",
        list_id, lists[list_id]
    )
