import logging

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button

logger = logging.getLogger(__name__)


async def get_start_data(
        start_data: dict,
        dialog_manager: DialogManager,
):
    logger.debug("Передача в новый диалог start_data=%s", start_data)
    if start_data is None:
        start_data = {}
    dialog_manager.dialog_data.update(start_data)


async def go_pass(
        callback: CallbackQuery,
        _widget: Button,
        _dialog_manager: DialogManager
):
    logger.debug("Функция-заглушка")
    await callback.answer("Эта кнопка пока не работает")


async def on_process_result(
        _start_data,
        result: dict,
        dialog_manager: DialogManager
):
    logger.debug("Выполнение действий при закрытии предыдущего диалога")
    logger.debug("result=%s", result)
    if not result:
        return
    dialog_manager.dialog_data.update(result)
