import logging

from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode, ShowMode
from sqlalchemy.ext.asyncio import AsyncSession

from bot.dialogs.states import StartSG, HelpSG
from database.services.user import upsert_user_with_log

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
    await upsert_user_with_log(
        session,
        user_id=user_id,
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
    await dialog_manager.start(
        state=StartSG.start_window,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.DELETE_AND_SEND,
    )


@commands_router.message(Command("help"))
async def cmd_help(
        message: Message,
        dialog_manager: DialogManager,
        session: AsyncSession
):
    logger.debug("Сообщение попало в хэндлер %s", cmd_start.__name__)
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    await upsert_user_with_log(
        session,
        user_id=user_id,
        first_name=first_name,
        last_name=last_name,
        username=username,
    )

    await dialog_manager.start(
        state=HelpSG.help_window,
        show_mode=ShowMode.DELETE_AND_SEND,
    )
