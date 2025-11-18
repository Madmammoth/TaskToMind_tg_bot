import logging
from typing import cast

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, SubManager
from aiogram_dialog.widgets.kbd import Button

from bot.dialogs.states import TaskActionsDialogSG

logger = logging.getLogger(__name__)


async def go_selected_task(
        callback: CallbackQuery,
        _widget: Button,
        dialog_manager: DialogManager,
):
    logger.debug("Переход к задаче...")
    sub_manager = cast(SubManager, dialog_manager)
    dialog_manager = sub_manager.manager
    task_id = str(sub_manager.item_id)
    tasks = dialog_manager.dialog_data.get("tasks")
    task_title = tasks[task_id]
    dialog_manager.dialog_data.update({
        "task_id": task_id,
        "task_title": task_title,
    })
    data = {}
    await callback.answer(f"Выбрана задача: {task_title}")
    await dialog_manager.start(
        state=TaskActionsDialogSG.main_task_window,
        data=data,
    )
    logger.debug(
        "Выбрана задача id=%s, title=%s",
        task_id, task_title
    )
