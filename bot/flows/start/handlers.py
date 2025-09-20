from aiogram.types import Message, CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Button

from bot.flows.start.states import StartSG
from bot.flows.add_task.states import GetTaskDialogSG
from bot.handlers.commands import logger


async def add_task(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        html_text: str
):
    logger.debug(
        "Запуск диалога добавления задачи. Функция %s",
        add_task.__name__
    )
    await dialog_manager.start(
        state=GetTaskDialogSG.add_task_window,
        data={"message_id": message.message_id, "task": html_text})


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
