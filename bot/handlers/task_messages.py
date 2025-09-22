import logging

from aiogram import F, Router
from aiogram.types import Message
from aiogram_dialog import DialogManager

from bot.dialogs.states import GetTaskDialogSG

logger = logging.getLogger(__name__)

task_messages_router = Router()


@task_messages_router.message(F.text)
async def get_task_handler(message: Message, dialog_manager: DialogManager):
    logger.debug("Апдейт попал в хэндлер %s", get_task_handler.__name__)
    await dialog_manager.start(
        state=GetTaskDialogSG.add_task_window,
        data={
            "message_id": message.message_id,
            "task": message.html_text,
            "in_list": "Входящие",
            "priority": "Низкий",
            "urgency": "Низкая",
        }
    )
