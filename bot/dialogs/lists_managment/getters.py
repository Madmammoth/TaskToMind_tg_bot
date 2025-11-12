import logging

from aiogram_dialog import DialogManager

from database.models import User
from database.requests import (
    get_user_tasks_in_list,
    get_user_sub_lists_in_list,
)

logger = logging.getLogger(__name__)


async def get_new_list(dialog_manager: DialogManager, **_kwargs):
    logger.debug("Апдейт здесь")
    return dialog_manager.dialog_data


async def get_tasks(
        dialog_manager: DialogManager,
        event_from_user: User,
        **_kwargs
) -> dict:
    logger.debug("Апдейт здесь")
    logger.debug("Словарь dialog_data:")
    logger.debug(dialog_manager.dialog_data)
    session = dialog_manager.middleware_data["session"]
    user_id = event_from_user.id
    list_id = dialog_manager.dialog_data.get("list_id")
    list_title = dialog_manager.dialog_data["lists"][list_id]
    tasks = await get_user_tasks_in_list(session, user_id, int(list_id))
    dialog_manager.dialog_data["tasks"] = {
        task.task_id: task.title for task in tasks
    }
    sub_lists = await get_user_sub_lists_in_list(
        session, user_id, int(list_id),
    )
    sub_lists = tuple(
        [(i, sub_list.title) for i, sub_list in enumerate(sub_lists, start=1)]
    )
    dialog_manager.dialog_data["sub_lists"] = sub_lists
    logger.debug("Словарь dialog_data:")
    logger.debug(dialog_manager.dialog_data)
    buttons_data = [
        {"task_id": task.task_id, "task_title": task.title}
        for task in tasks
    ]
    logger.debug("Получившийся список для кнопок:")
    logger.debug(buttons_data)
    return {
        "list_title": list_title,
        "sub_lists": sub_lists,
        "tasks": buttons_data,
        "is_empty_list": not tasks and not sub_lists,
    }


async def get_list_title_to_delete(
        dialog_manager: DialogManager,
        **_kwargs
) -> dict:
    logger.debug("Апдейт здесь")
    logger.debug("Словарь dialog_data:")
    logger.debug(dialog_manager.dialog_data)
    list_id = dialog_manager.dialog_data.get("list_id")
    lists = dialog_manager.dialog_data.get("lists")
    list_title = lists[list_id]
    return {"list_title": list_title}
