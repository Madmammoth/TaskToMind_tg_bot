import logging

from aiogram.types import User
from aiogram_dialog import DialogManager
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.orchestration.list_selection import STRATEGIES, ListSelectionMode
from app.utils.serialization import to_dialog_safe

logger = logging.getLogger(__name__)


@inject
async def lists_getter(
        dialog_manager: DialogManager,
        event_from_user: User,
        di_session: FromDishka[AsyncSession],
        **_kwargs
) -> dict:
    user_id = event_from_user.id
    session = di_session
    logger.debug("Получение списков пользователя id=%d", user_id)
    mode = ListSelectionMode(dialog_manager.start_data.get("mode"))

    if mode is None:
        raise ValueError("Missing required start_data: mode")

    strategy = STRATEGIES[mode]

    buttons, lists = await strategy.get_lists(session, user_id)

    dialog_manager.dialog_data["lists"] = to_dialog_safe(lists)

    return {"buttons": buttons}
