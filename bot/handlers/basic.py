import logging
import operator
from copy import deepcopy
from typing import Any

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton, User, CallbackQuery
)
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Row, Button, Select
from aiogram_dialog.widgets.text import Const, Format, Jinja

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
    first_name = message.from_user.first_name
    user_id = message.from_user.id
    if user_id not in fake_database:
        user_data: dict[str, Any] = deepcopy(template_data_for_new_user)
        user_data.update(username=username, first_name=first_name)
        fake_database[user_id] = user_data
        print(fake_database)
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
        "Но пока я могу следующее:\n1. Ответить тебе твоим же сообщением!"
    )


async def go_lists(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager
):
    logger.debug("Переход в окно со списками. Функция %s", go_lists.__name__)
    await dialog_manager.switch_to(state=GetTaskDialogSG.lists_window)


async def on_inbox_click_process(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager
):
    pass


async def get_lists(
        dialog_manager: DialogManager,
        event_from_user: User, **kwargs
) -> dict[str, list[dict[str, int | Any]]]:
    logger.debug("Апдейт попал в геттер %s", get_lists.__name__)
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


menu_task = Dialog(
    Window(
        Format("{task}"),
        Row(
            Button(text=Const("Списки"),
                   id="lists",
                   on_click=go_lists),
            Button(text=Const("Входящие"),
                   id="inbox",
                   on_click=on_inbox_click_process),
        ),
        getter=get_task,
        state=GetTaskDialogSG.menu_window
    ),
    Window(
        Jinja("""
{% for user_list in user_lists_dict %}
<b>{{ user_list.number }}</b>. {{ user_list.title }}
{% endfor %}
        """),
        Select(
            Format("{item[0]}"),
            id="list",
            item_id_getter=operator.itemgetter(0),
            items="user_lists"
        ),
        getter=get_lists,
        state=GetTaskDialogSG.lists_window
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
