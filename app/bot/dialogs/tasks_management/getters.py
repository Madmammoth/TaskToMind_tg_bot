import logging

from aiogram.types import User
from aiogram_dialog import DialogManager

from app.database.crud.task import get_user_tasks, get_user_tasks_in_list
from app.database.crud.task_list import (
    get_user_trash_list_id,
    get_user_archive_list_id,
)
from app.utils.serialization import to_dialog_safe

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
    dialog_manager.dialog_data["tasks"] = to_dialog_safe({
        task.task_id: task.title for task in tasks
    })
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


async def get_tasks_in_trash(
        dialog_manager: DialogManager,
        event_from_user: User,
        **_kwargs
) -> dict:
    logger.debug("Получение отменённых задач пользователя...")
    user_id = event_from_user.id
    logger.debug("...id=%d", user_id)
    session = dialog_manager.middleware_data["session"]
    mode = dialog_manager.dialog_data.get("show_tasks_mode", "default")
    list_id = await get_user_trash_list_id(session, user_id)
    tasks = await get_user_tasks_in_list(session, user_id, list_id, mode)
    dialog_manager.dialog_data["tasks"] = to_dialog_safe({
        task.task_id: task.title for task in tasks
    })
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


async def get_tasks_in_archive(
        dialog_manager: DialogManager,
        event_from_user: User,
        **_kwargs
) -> dict:
    logger.debug("Получение выполненных задач пользователя...")
    user_id = event_from_user.id
    logger.debug("...id=%d", user_id)
    session = dialog_manager.middleware_data["session"]
    mode = dialog_manager.dialog_data.get("show_tasks_mode", "default")
    list_id = await get_user_archive_list_id(session, user_id)
    tasks = await get_user_tasks_in_list(session, user_id, list_id, mode)
    dialog_manager.dialog_data["tasks"] = to_dialog_safe({
        task.task_id: task.title for task in tasks
    })
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