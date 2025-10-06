import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode
from sqlalchemy.ext.asyncio import AsyncSession

from bot.dialogs.states import StartSG
from database.requests import db_upsert_user

logger = logging.getLogger(__name__)

commands_router = Router()


@commands_router.message(CommandStart())
async def cmd_start(
        message: Message,
        dialog_manager: DialogManager,
        session: AsyncSession
):
    logger.debug("Сообщение попало в хэндлер %s", cmd_start.__name__)
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    await db_upsert_user(
        session,
        telegram_id=user_id,
        first_name=first_name,
        last_name=last_name,
        username=username,
    )
    await message.answer(
        f"Приветствую, {first_name}!\n\nЯ — бот, который со временем "
        "станет твоим удобным и надёжным планировщиком дел, "
        "умным каталогизатором всех твоих пересланных сообщений, "
        "твоей второй памятью и даже — твоим вторым мозгом!\n\n"
        "Но пока я могу следующее:\n1. Сохранить твою задачу."
    )
    await dialog_manager.start(state=StartSG.start_window,
                               mode=StartMode.RESET_STACK)
