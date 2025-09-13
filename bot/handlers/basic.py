import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

logger = logging.getLogger(__name__)

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    logger.debug("Сообщение попало в хэндлер %s", cmd_start.__name__)
    username = message.from_user.username
    await message.answer(
        f"Приветствую, {username}!\n\nЯ — бот, который со временем "
        "станет твоим удобным и надёжным планировщиком дел, "
        "умным каталогизатором всех твоих пересланных сообщений, "
        "твоей второй памятью и даже — твоим вторым мозгом!\n\n"
        "Но пока я могу следующее:\n1. Ответить тебе твоим же сообщением!"
    )





@router.message()
async def send_echo(message: Message):
    logger.debug("Сообщение попало в хэндлер %s", send_echo.__name__)
    try:
        await message.send_copy(chat_id=message.chat.id,
                                reply_to_message_id=message.message_id)
    except TypeError:
        await message.reply("Какое-то необычное сообщение для меня.")
