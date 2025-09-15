import logging
from copy import deepcopy
from typing import Any

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton, User, CallbackQuery, Update
)
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Row, Button
from aiogram_dialog.widgets.text import Const, Format

from bot.dialogs.states import GetTaskDialogSG

logger = logging.getLogger(__name__)

router = Router()

fake_database = {}
template_data_for_new_user = {
    "lists": {
        "Работа": {},
        "Быт": {},
    },
    "other": {},
}


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
    user_id = message.from_user.id
    if user_id not in fake_database:
        user_data: dict[str, Any] = deepcopy(template_data_for_new_user)
        user_data["username"] = username
        fake_database[user_id] = user_data
        logger.debug("Пользователь %s (id: %d) добавлен в базу данных")
    else:
        logger.debug("Пользователь %s (id: %d) уже есть в базе данных")
    await message.answer(
        f"Приветствую, {username}!\n\nЯ — бот, который со временем "
        "станет твоим удобным и надёжным планировщиком дел, "
        "умным каталогизатором всех твоих пересланных сообщений, "
        "твоей второй памятью и даже — твоим вторым мозгом!\n\n"
        "Но пока я могу следующее:\n1. Ответить тебе твоим же сообщением!"
    )


async def on_lists_click_process(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager
):
    pass


async def on_inbox_click_process(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager
):
    pass


async def get_lists(event_from_user: User, **kwargs) -> dict:
    logger.debug("Апдейт попал в геттер %s", get_lists.__name__)
    return fake_database[event_from_user.id]


async def get_task(dialog_manager: DialogManager, **kwargs):
    logger.debug("Апдейт попал в геттер %s", get_task.__name__)
    return dialog_manager.start_data


menu_task_dialog = Dialog(
    Window(
        Format("{task}"),
        Row(
            Button(text=Const("Списки"),
                   id="lists",
                   on_click=on_lists_click_process),
            Button(text=Const("Входящие"),
                   id="inbox",
                   on_click=on_inbox_click_process),
        ),
        getter=get_task,
        state=GetTaskDialogSG.menu_window
    ),
)


@router.message(F.text)
async def get_task_process(message: Message, dialog_manager: DialogManager):
    logger.debug("Апдейт попал в хэндлер %s", get_task_process.__name__)
    await dialog_manager.start(state=GetTaskDialogSG.menu_window,
                               data={"task": message.html_text})


@router.message()
async def other_msgs_process(message: Message):
    logger.debug("Апдейт попал в хэндлер %s", other_msgs_process.__name__)
    await message.reply("Какое-то необычное сообщение для меня.")
