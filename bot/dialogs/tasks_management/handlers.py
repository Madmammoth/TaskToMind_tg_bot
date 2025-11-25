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
    logger.debug("Переход к задаче пользователя...")
    user_id = callback.from_user.id
    logger.debug("...id=%d", user_id)
    sub_manager = cast(SubManager, dialog_manager)
    dialog_manager = sub_manager.manager
    task_id = int(sub_manager.item_id)
    data = {"task_id": task_id}
    logger.debug(
        "Пользователем id=%d выбрана задача id=%s, data=%s",
        user_id, task_id, data
    )
    await dialog_manager.start(
        state=TaskActionsDialogSG.main_task_window,
        data=data,
    )
