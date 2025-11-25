from aiogram_dialog import DialogManager

from bot.dialogs.lists_managment.getters import logger
from database.models import User
from database.services.task_list import build_ordered_hierarchy
from database.crud.task_list import fetch_user_lists_raw
from utils.serialization import from_dialog_safe


async def get_dialog_data(
        dialog_manager: DialogManager,
        **_kwargs
):
    logger.debug("Получение словаря из dialog_data")
    return from_dialog_safe(dialog_manager.dialog_data)


async def get_lists(
        dialog_manager: DialogManager,
        event_from_user: User,
        **_kwargs
) -> dict:
    logger.debug("Апдейт здесь")
    session = dialog_manager.middleware_data["session"]
    user_id = event_from_user.id
    mode = dialog_manager.dialog_data.get("show_lists_mode", "default")
    rows = await fetch_user_lists_raw(session, user_id, mode)
    list_buttons = build_ordered_hierarchy(rows)
    dialog_manager.dialog_data["lists"] = {
        lst["list_id"]: lst["list_title"] for lst in list_buttons
    }
    logger.debug("Словарь dialog_data:")
    logger.debug(dialog_manager.dialog_data)
    logger.debug("Получившийся список для кнопок:")
    logger.debug(list_buttons)
    return {
        "lists": list_buttons,
    }
