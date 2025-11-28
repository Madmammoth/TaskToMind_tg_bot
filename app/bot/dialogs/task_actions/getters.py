import logging

from aiogram.types import User
from aiogram_dialog import DialogManager

from app.database.crud.task import mark_task_in_process
from app.database.models import TaskStatusEnum
from app.database.services.task import (
    get_full_task_info,
    make_task_data_for_dialog
)
from app.utils.serialization import to_dialog_safe

logger = logging.getLogger(__name__)


async def get_task(
        dialog_manager: DialogManager,
        event_from_user: User,
        **_kwargs
):
    logger.debug("Получение данных задачи")
    session = dialog_manager.middleware_data["session"]
    user_id = event_from_user.id
    task_id = dialog_manager.dialog_data.get("task_id")
    if not task_id:
        logger.debug("В словаре диалога нет task_id")
        return {}
    task, task_list, access, timezone = await get_full_task_info(
        session, user_id, task_id
    )
    task_data = make_task_data_for_dialog(task, task_list, access, timezone)
    dialog_manager.dialog_data.update(to_dialog_safe(task_data))
    if task_data["status"] == TaskStatusEnum.NEW:
        await mark_task_in_process(session, task_id, user_id)
        logger.debug("Статус задачи изменён с «Новая» на «В работе»")
    logger.debug("Получен task_data=%s", task_data)
    return task_data
