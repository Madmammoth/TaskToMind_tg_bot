import logging

from aiogram import Router
from aiogram.types import Message

logger = logging.getLogger(__name__)

others_router = Router()


@others_router.message()
async def other_msgs_process(message: Message):
    logger.debug("Апдейт попал в хэндлер %s", other_msgs_process.__name__)
    await message.reply("Какое-то необычное сообщение для меня.")
