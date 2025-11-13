import logging

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button

logger = logging.getLogger(__name__)


async def go_pass(
        callback: CallbackQuery,
        _widget: Button,
        _dialog_manager: DialogManager
):
    logger.debug("Функция-заглушка")
    await callback.answer("Эта кнопка пока не работает")
