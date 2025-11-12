from aiogram_dialog import DialogManager

from bot.dialogs.lists_managment.getters import logger
from database.models import User
from database.requests import get_ordered_user_lists


async def get_lists(
        dialog_manager: DialogManager,
        event_from_user: User,
        **_kwargs
) -> dict:
    logger.debug("Апдейт здесь")
    session = dialog_manager.middleware_data["session"]
    user_id = event_from_user.id
    mode = dialog_manager.dialog_data.get("show_lists_mode", "normal")
    buttons_data = await get_ordered_user_lists(session, user_id, mode)
    dialog_manager.dialog_data["lists"] = {
        lst["list_id"]: lst["list_title"] for lst in buttons_data
    }
    logger.debug("Словарь dialog_data:")
    logger.debug(dialog_manager.dialog_data)
    logger.debug("Получившийся список для кнопок:")
    logger.debug(buttons_data)
    return {
        "lists": buttons_data,
    }
