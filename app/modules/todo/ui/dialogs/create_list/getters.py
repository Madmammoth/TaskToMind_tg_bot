import logging

from aiogram_dialog import DialogManager

from app.core.utils.dialog_serialization import from_dialog_safe

logger = logging.getLogger(__name__)


async def get_new_list(dialog_manager: DialogManager, **_kwargs):
    logger.debug("Апдейт здесь")
    return from_dialog_safe(dialog_manager.dialog_data)
