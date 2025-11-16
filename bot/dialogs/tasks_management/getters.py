import logging

from aiogram.types import User
from aiogram_dialog import DialogManager

from database.crud.task import get_user_tasks

logger = logging.getLogger(__name__)


async def get_all_tasks(
        dialog_manager: DialogManager,
        event_from_user: User,
        **_kwargs
) -> dict:
    logger.debug("Апдейт здесь")
    session = dialog_manager.middleware_data["session"]
    user_id = event_from_user.id
    mode = dialog_manager.dialog_data.get("show_tasks_mode", "default")
    tasks = await get_user_tasks(session, user_id, mode)
    dialog_manager.dialog_data["tasks"] = {
        task.task_id: task.title for task in tasks
    }
    logger.debug("Словарь dialog_data:")
    logger.debug(dialog_manager.dialog_data)
    task_buttons = [
        {"pos": i, "task_id": task.task_id, "task_title": task.title}
        for i, task in enumerate(tasks, 1)
    ]
    logger.debug("Получившийся список для кнопок:")
    logger.debug(task_buttons)
    window_data = {
        "time_back": True,
        "task_buttons": task_buttons,
    }
    return window_data
