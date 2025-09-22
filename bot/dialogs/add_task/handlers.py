import logging

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button

from bot.dialogs.states import StartSG

logger = logging.getLogger(__name__)


async def go_pass(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager
):
    logger.debug(
        "Заглушка для перехода в другое окно. Функция %s",
        go_pass.__name__
    )
    await callback.answer(
        "Когда-нибудь тут будет переход в другое окно"
    )


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
