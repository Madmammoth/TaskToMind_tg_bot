import logging
from typing import cast

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, SubManager
from aiogram_dialog.widgets.kbd import Button
from sqlalchemy.ext.asyncio import AsyncSession

from database.orchestration.task import change_list_for_task_with_log
from utils.serialization import from_dialog_safe

logger = logging.getLogger(__name__)


async def select_list(
        callback: CallbackQuery,
        _widget: Button,
        dialog_manager: DialogManager,
):
    sub_manager = cast(SubManager, dialog_manager)
    dialog_manager = sub_manager.manager
    list_id = int(sub_manager.item_id)
    user_id = callback.from_user.id
    logger.debug("Выбор списка id=%d пользователем id=%d", list_id, user_id)

    session: AsyncSession = dialog_manager.middleware_data["session"]
    data = from_dialog_safe(dialog_manager.dialog_data)
    task_id = data.get("task_id")
    lists = data.get("lists", {})

    mode = data.get("mode")
    logger.debug("mode=%s", mode)

    if mode == "task_action":
        old_list_id = data.get("selected_list_id")
        await change_list_for_task_with_log(
            session, user_id, task_id, old_list_id, list_id
        )
        logger.debug(
            "Пользователем id=%d для задачи id=%d "
            "изменён список с id=%d на id=%d",
            user_id, task_id, old_list_id, list_id
        )

    selected_list_data = {
        "selected_list_id": list_id,
        "selected_list_title": lists[list_id],
    }
    logger.debug("selected_list_data=%s", selected_list_data)

    await dialog_manager.done(selected_list_data)
