import logging

from aiogram_dialog import DialogManager

logger = logging.getLogger(__name__)


async def get_new_list(dialog_manager: DialogManager, **_kwargs):
    logger.debug("Апдейт здесь")
    return dialog_manager.dialog_data
