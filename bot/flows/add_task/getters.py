from copy import deepcopy
from typing import Any

from aiogram.types import User
from aiogram_dialog import DialogManager

from bot.handlers.basic import logger, fake_database, template_data_for_new_user


async def get_lists(
        dialog_manager: DialogManager,
        event_from_user: User, **kwargs
) -> dict[str, list[dict[str, int | Any]]]:
    logger.debug("Апдейт попал в геттер %s", get_lists.__name__)
    if event_from_user.id not in fake_database:
        user_id = event_from_user.id
        username = event_from_user.username
        first_name = event_from_user.first_name
        user_data: dict[str, Any] = deepcopy(template_data_for_new_user)
        user_data.update(username=username, first_name=first_name)
        fake_database[user_id] = user_data
        logger.debug(
            "Пользователь %s (имя: %s, id: %d) добавлен в базу данных",
            username, first_name, user_id
        )
    user_lists = fake_database[event_from_user.id]["lists"].keys()
    user_lists_dict = [{"number": number, "title": user_list}
                       for number, user_list
                       in enumerate(user_lists, start=1)]
    user_lists = [(number, user_list)
                  for number, user_list
                  in enumerate(user_lists, start=1)]
    return {"user_lists_dict": user_lists_dict, "user_lists": user_lists}


async def get_task(dialog_manager: DialogManager, **kwargs):
    logger.debug("Апдейт попал в геттер %s", get_task.__name__)
    return dialog_manager.start_data
