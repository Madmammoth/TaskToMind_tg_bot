import logging

from aiogram import Router, html
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

logger = logging.getLogger(__name__)

router = Router()


def make_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text="В список",
                callback_data="to_list"
            ),
            InlineKeyboardButton(
                text="В неразобранное",
                callback_data="to_unassembled"
            ),
        ],
        [
            InlineKeyboardButton(
                text="Редактировать",
                callback_data="edit"
            ),
            InlineKeyboardButton(
                text="Отмена",
                callback_data="cancel"
            )
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


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
async def get_task(message: Message):
    logger.debug("Сообщение попало в хэндлер %s", get_task.__name__)
    try:
        await message.answer(
            text=message.html_text,
            reply_markup=make_keyboard()
        )
    except TypeError:
        await message.reply("Какое-то необычное сообщение для меня.")
