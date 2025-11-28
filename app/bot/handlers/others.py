import logging

from aiogram import Router
from aiogram.types import Message

logger = logging.getLogger(__name__)

others_router = Router()


@others_router.message()
async def other_msgs_process(message: Message):
    logger.debug("Апдейт здесь")
    await message.reply(
        "Упс! Как ты вообще здесь оказался?!\n\n Попробуй нажать /start"
    )
