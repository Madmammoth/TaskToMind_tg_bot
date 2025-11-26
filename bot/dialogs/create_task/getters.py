import logging

from aiogram_dialog import DialogManager

from utils.serialization import from_dialog_safe

logger = logging.getLogger(__name__)


async def get_task(dialog_manager: DialogManager, **_kwargs):
    logger.debug("Получение данных задачи")
    data = from_dialog_safe(dialog_manager.dialog_data)
    logger.debug("Получены данные задачи: %s", data)
    return data
