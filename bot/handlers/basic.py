import logging
from copy import deepcopy
from typing import Any

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton, User, CallbackQuery
)
from aiogram_dialog import Dialog, Window, DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Row, Button
from aiogram_dialog.widgets.text import Const, Format

from bot.dialogs.states import GetTaskDialogSG, StartSG

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


async def start_add_task(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager
):
    logger.debug(
        "Запуск диалога добавления задачи. Функция %s",
        start_add_task.__name__
    )
    await dialog_manager.start(state=GetTaskDialogSG.create_task_window,
                               data={"task": "✍️ Введите задачу ниже"})


async def go_tasks(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager
):
    logger.debug(
        "Заглушка-переход в окно с задачами. Функция %s",
        go_tasks.__name__
    )
    await callback.answer(
        "Когда-нибудь тут будет переход к уже добавленным задачам"
    )


async def go_settings(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager
):
    logger.debug(
        "Заглушка-переход в окно настроек. Функция %s",
        go_settings.__name__
    )
    await callback.answer(
        "Когда-нибудь тут будет переход в настройки бота"
    )


async def go_features(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager
):
    logger.debug(
        "Заглушка-переход в окно возможностей бота. Функция %s",
        go_features.__name__
    )
    await callback.answer(
        "Когда-нибудь тут будет переход к описанию возможностей бота"
    )


async def go_support(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager
):
    logger.debug(
        "Заглушка-переход в окно технической поддержки. Функция %s",
        go_support.__name__
    )
    await callback.answer(
        "Когда-нибудь тут будет соединение с технической поддержкой"
    )


async def go_inbox(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager
):
    pass


async def go_cancel(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager
):
    logger.debug(
        "Переход в окно отмены добавления задачи. Функция %s",
        go_cancel.__name__
    )
    await dialog_manager.switch_to(state=GetTaskDialogSG.cancel_window)


async def on_cancel_yes_click(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager
):
    logger.debug(
        "Закрытие диалога добавления задачи. Функция %s",
        on_cancel_yes_click.__name__
    )
    await dialog_manager.done()


async def get_username(
        dialog_manager: DialogManager,
        event_from_user: User, **kwargs
):
    return {"username": event_from_user.first_name}


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


start_dialog = Dialog(
    Window(
        Const("Отправь мне планируемую задачу, "
              "чтобы не забыть о ней! 🔘 ⚪ ⬜ 🔳 🔲"),
        Row(
            Button(text=Const("Добавить задачу"),
                   id="add_task",
                   on_click=start_add_task),
            Button(text=Const("Посмотреть задачи"),
                   id="tasks",
                   on_click=go_tasks),
        ),
        Row(
            Button(text=Const("Настройки"),
                   id="settings",
                   on_click=go_settings),
            Button(text=Const("Возможности бота"),
                   id="features",
                   on_click=go_features),
        ),
        Button(text=Const("Поддержка"),
               id="support",
               on_click=go_support),
        state=StartSG.start_window
    ),
)

create_task_dialog = Dialog(
    Window(
        Format("{task}"),
        Row(
            Button(text=Const("Списки"),
                   id="lists",
                   on_click=go_tasks),
            Button(text=Const("Входящие"),
                   id="inbox",
                   on_click=go_inbox),
            Button(text=Const("Отмена"),
                   id="cancel",
                   on_click=go_cancel),
        ),
        getter=get_task,
        state=GetTaskDialogSG.create_task_window
    ),
)


@router.message(F.text)
async def get_task_handler(message: Message, dialog_manager: DialogManager):
    logger.debug("Апдейт попал в хэндлер %s", get_task_handler.__name__)
    await dialog_manager.start(state=GetTaskDialogSG.create_task_window,
                               data={"task": message.html_text})


@router.message()
async def other_msgs_process(message: Message):
    logger.debug("Апдейт попал в хэндлер %s", other_msgs_process.__name__)
    await message.reply("Какое-то необычное сообщение для меня.")
