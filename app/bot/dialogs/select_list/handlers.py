import logging
from typing import cast

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, SubManager
from aiogram_dialog.widgets.kbd import Button
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.dialogs.enums import ListSelectionMode
from app.bot.dialogs.select_list.scenarios import get_select_list_scenario

logger = logging.getLogger(__name__)


async def select_list_core(
        callback: CallbackQuery,
        _widget: Button,
        dialog_manager: DialogManager,
        session: FromDishka[AsyncSession],
):
    sub_manager = cast(SubManager, dialog_manager)
    dialog_manager = sub_manager.manager
    list_id = int(sub_manager.item_id)
    user_id = callback.from_user.id
    mode = ListSelectionMode(dialog_manager.start_data["mode"])
    logger.debug(
        "Выбор списка id=%d пользователем id=%d в режиме mode=%r",
        list_id, user_id, mode.value,
    )

    scenario = get_select_list_scenario(mode)

    result = await scenario.apply(
        session=session,
        dialog_manager=dialog_manager,
        list_id=list_id,
    )

    await dialog_manager.done(result)

    logger.debug(
        "Пользователем id=%d в режиме mode=%r выбран список с result=%r",
        user_id, mode.value, result,
    )


select_list = inject(select_list_core)
