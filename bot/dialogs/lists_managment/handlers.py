import logging
from typing import cast

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, SubManager, ShowMode
from aiogram_dialog.widgets.kbd import Button
from sqlalchemy.ext.asyncio import AsyncSession

from bot.dialogs.states import (
    ListsManagementDialogSG,
    TaskActionsDialogSG,
)
from database.services.task_list import delete_list_with_stats_log

logger = logging.getLogger(__name__)


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
        state=TaskActionsDialogSG.main_task_window,
        data=data
    )
    logger.debug(
        "Выбрана задача id=%s, title=%s",
        task_id, task_title
    )


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
        state=ListsManagementDialogSG.list_with_tasks
    )
    logger.debug(
        "Установлен список задач id=%s, title=%s",
        list_id, lists[list_id]
    )


async def go_delete_list_yes(
        callback: CallbackQuery,
        _widget: Button,
        dialog_manager: DialogManager,
):
    logger.debug("Удаление списка задач")
    session: AsyncSession = dialog_manager.middleware_data["session"]
    user_id = callback.from_user.id
    list_id = dialog_manager.dialog_data.get("list_id")
    if not list_id:
        logger.debug("Не найден list_id в dialog_data")
        await callback.answer("Список не найден")
        return
    lists = dialog_manager.dialog_data.get("lists")
    if not lists:
        logger.debug("Не найдены списки пользователя в dialog_data")
        await callback.answer("Списки не найдены")
        return
    list_title = lists[list_id]
    await delete_list_with_stats_log(
        session=session,
        user_id=user_id,
        list_id=int(list_id),
    )
    text = f"Успешно удалён список задач: {list_title}"
    await callback.message.answer(text=text)
    await dialog_manager.switch_to(
        state=ListsManagementDialogSG.main_lists_window,
        show_mode=ShowMode.DELETE_AND_SEND,
    )
