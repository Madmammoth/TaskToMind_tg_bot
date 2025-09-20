from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button

from bot.flows.start.states import StartSG
from bot.flows.add_task.states import GetTaskDialogSG
from bot.handlers.commands import logger


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


async def go_back_to_add_task(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager
):
    await dialog_manager.switch_to(state=GetTaskDialogSG.add_task_window)


async def go_cancel_yes(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager
):
    message_id = dialog_manager.start_data["message_id"]
    await callback.bot.send_message(
        chat_id=callback.message.chat.id,
        text="Добавление задачи было отменено",
        reply_to_message_id=message_id,
    )
    await callback.message.delete()
    await dialog_manager.start(state=StartSG.start_window,
                               mode=StartMode.RESET_STACK)


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
