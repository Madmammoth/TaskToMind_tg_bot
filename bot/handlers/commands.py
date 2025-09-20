import logging
from copy import deepcopy
from typing import Any

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

from bot.flows.start.states import StartSG

logger = logging.getLogger(__name__)

commands_router = Router()

fake_database = {}
template_data_for_new_user = {
    "lists": {
        "Работа": {},
        "Быт": {},
    },
    "other": {},
}


@commands_router.message(CommandStart())
async def cmd_start(
        message: Message,
        dialog_manager: DialogManager
):
    logger.debug("Сообщение попало в хэндлер %s", cmd_start.__name__)
    username = message.from_user.username
    first_name = message.from_user.first_name
    user_id = message.from_user.id
    if user_id not in fake_database:
        user_data: dict[str, Any] = deepcopy(template_data_for_new_user)
        user_data.update(username=username, first_name=first_name)
        fake_database[user_id] = user_data
        logger.debug(
            "Пользователь %s (имя: %s, id: %d) добавлен в базу данных",
            username, first_name, user_id
        )
    else:
        logger.debug(
            "Пользователь %s (имя: %s, id: %d) уже есть в базе данных",
            username, first_name, user_id
        )
    await message.answer(
        f"Приветствую, {username}!\n\nЯ — бот, который со временем "
        "станет твоим удобным и надёжным планировщиком дел, "
        "умным каталогизатором всех твоих пересланных сообщений, "
        "твоей второй памятью и даже — твоим вторым мозгом!\n\n"
        "Но пока я могу следующее:\n1. Сохранить твою задачу."
    )
    await dialog_manager.start(state=StartSG.start_window,
                               mode=StartMode.RESET_STACK)
