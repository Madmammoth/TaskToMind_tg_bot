from typing import cast

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, SubManager
from aiogram_dialog.widgets.kbd import Button

from bot.dialogs.add_task.handlers import logger
from bot.dialogs.lists_managment.handlers import logger
from bot.dialogs.states import TaskListsDialogSG


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


async def go_pass(
        callback: CallbackQuery,
        _widget: Button,
        _dialog_manager: DialogManager
):
    logger.debug("Функция-заглушка")
    await callback.answer("Эта кнопка пока не работает")
