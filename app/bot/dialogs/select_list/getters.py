import logging

from aiogram_dialog import DialogManager
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.dialogs.enums import ListSelectionMode
from app.bot.dialogs.select_list.scenarios import get_select_list_scenario
from app.utils.serialization import to_dialog_safe

logger = logging.getLogger(__name__)


async def lists_getter_core(
        dialog_manager: DialogManager,
        di_session: FromDishka[AsyncSession],
        **_kwargs,
) -> dict:
    user_id = dialog_manager.event.from_user.id
    mode = ListSelectionMode(dialog_manager.start_data["mode"])
    logger.debug("Получение списков пользователя id=%d в режиме mode=%r", user_id, mode)

    scenario = get_select_list_scenario(mode)

    buttons, lists = await scenario.get_lists(
        session=di_session,
        dialog_manager=dialog_manager,
    )

    dialog_manager.dialog_data["lists"] = to_dialog_safe(lists)
    logger.debug(
        "Для пользователя id=%d в режиме mode=%r получены buttons=%r, lists=%r",
        user_id, mode, buttons, lists
    )
    return {"buttons": buttons}


lists_getter = inject(lists_getter_core)
