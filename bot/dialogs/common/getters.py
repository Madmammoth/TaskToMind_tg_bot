import logging

from aiogram_dialog import DialogManager

from database.crud.task_list import fetch_user_lists_raw
from database.models import User
from database.services.task_list import build_ordered_hierarchy
from utils.serialization import from_dialog_safe, to_dialog_safe

logger = logging.getLogger(__name__)


async def get_dialog_data(
        dialog_manager: DialogManager,
        **_kwargs
):
    data = from_dialog_safe(dialog_manager.dialog_data)
    logger.debug("Получение словаря из dialog_data: %s", data)
    return data


async def get_lists(
        dialog_manager: DialogManager,
        event_from_user: User,
        **_kwargs
) -> dict:
    logger.debug("Получение списков пользователя...")
    user_id = event_from_user.id
    logger.debug("...id=%d", user_id)
    session = dialog_manager.middleware_data["session"]
    mode = dialog_manager.dialog_data.get("mode", "default")
    rows = await fetch_user_lists_raw(session, user_id, mode)
    list_buttons = build_ordered_hierarchy(rows)
    lists = {lst["list_id"]: lst["list_title"] for lst in list_buttons}
    dialog_manager.dialog_data["lists"] = to_dialog_safe(lists)
    logger.debug("Словарь dialog_data:")
    logger.debug(dialog_manager.dialog_data)
    logger.debug("Получившийся список для кнопок:")
    logger.debug(list_buttons)
    return {"lists": list_buttons}
