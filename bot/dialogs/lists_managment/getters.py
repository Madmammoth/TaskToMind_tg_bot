import logging

from aiogram_dialog import DialogManager

from database.crud.task import get_user_tasks_in_list
from database.crud.task_list import get_user_sub_lists_in_list
from database.models import User
from utils.serialization import from_dialog_safe, to_dialog_safe

logger = logging.getLogger(__name__)


async def get_tasks(
        dialog_manager: DialogManager,
        event_from_user: User,
        **_kwargs
) -> dict:
    logger.debug("Получение задач пользователя...")
    user_id = event_from_user.id
    logger.debug("...id=%d", user_id)
    logger.debug("Словарь dialog_data до обновления:")
    logger.debug(dialog_manager.dialog_data)
    session = dialog_manager.middleware_data["session"]
    data = from_dialog_safe(dialog_manager.dialog_data)
    list_id = data.get("selected_list_id")
    list_title = data["lists"][list_id]
    mode = data.get("show_tasks_mode", "default")
    user_tasks = await get_user_tasks_in_list(session, user_id, list_id, mode)
    tasks = {task.task_id: task.title for task in user_tasks}
    dialog_manager.dialog_data["tasks"] = to_dialog_safe(tasks)
    sub_lists = await get_user_sub_lists_in_list(
        session, user_id, list_id,
    )
    sub_lists = tuple(
        [(i, sub_list.title) for i, sub_list in enumerate(sub_lists, start=1)]
    )
    dialog_manager.dialog_data["sub_lists"] = to_dialog_safe(sub_lists)
    logger.debug("Словарь dialog_data после обновления:")
    logger.debug(dialog_manager.dialog_data)
    task_buttons = [
        {"pos": i, "task_id": task.task_id, "task_title": task.title}
        for i, task in enumerate(user_tasks, 1)
    ]
    logger.debug("Получившийся список для кнопок:")
    logger.debug(task_buttons)
    return {
        "list_title": list_title,
        "sub_lists": sub_lists,
        "task_buttons": task_buttons,
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
