import logging

from aiogram.types import User
from aiogram_dialog import DialogManager

from database.requests import get_user_lists

logger = logging.getLogger(__name__)


async def get_lists(
        dialog_manager: DialogManager,
        event_from_user: User, **_kwargs
) -> dict:
    logger.debug("Апдейт здесь")
    session = dialog_manager.middleware_data["session"]
    user_id = event_from_user.id
    lists = await get_user_lists(session, user_id)
    dialog_manager.dialog_data["lists"] = {
        lst.list_id: lst.title for lst in lists
    }
    buttons_data = [
        {"list_id": lst.list_id, "list_title": lst.title}
        for lst in lists
    ]
    logger.debug("Получившийся список для кнопок:")
    logger.debug(buttons_data)
    return {
        "lists": buttons_data,
    }


async def get_task(dialog_manager: DialogManager, **_kwargs):
    logger.debug("Апдейт попал в геттер %s", get_task.__name__)
    return dialog_manager.dialog_data
