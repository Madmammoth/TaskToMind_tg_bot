import logging

from aiogram.types import Message, CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Button

from bot.dialogs.states import GetTaskDialogSG, StartSG
from bot.handlers.task_messages import make_default_task_data

logger = logging.getLogger(__name__)


async def add_task(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
):
    logger.debug(
        "Запуск диалога добавления задачи. Функция %s",
        add_task.__name__
    )
    task_data = make_default_task_data(message.message_id, message.html_text)
    await dialog_manager.start(
        state=GetTaskDialogSG.add_task_window,
        data=task_data
    )


async def input_task(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager
):
    logger.debug(
        "Переход в окно запроса задачи. Функция %s",
        input_task.__name__
    )
    await dialog_manager.switch_to(state=StartSG.input_task_window)


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
