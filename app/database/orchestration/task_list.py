import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.crud.stats import update_stats_on_list_deleted
from app.database.crud.task_list import db_delete_list, change_parent_list
from app.database.crud.tracking import log_activity
from app.database.services.task_list import (
    db_add_list,
    update_stats_achievs_on_list_added,
)

logger = logging.getLogger(__name__)


async def add_list_with_stats_achievs_log(
        session: AsyncSession,
        user_id: int,
        list_data: dict,
):
    """
    Проверяет и обновляет статистику и достижения пользователя
    с записью лога при добавлении списка
    :param session: сессия СУБД
    :param user_id: ID пользователя
    :param list_data: параметры добавляемого списка задач
    :return:
    """
    try:
        list_id = await db_add_list(session, user_id, list_data)
        await update_stats_achievs_on_list_added(session, user_id)
        await log_activity(
            session,
            action="add_list",
            success=True,
            user_id=user_id,
            list_id=list_id,
        )
        return list_id
    except Exception as e:
        logger.exception("Failed to add list: %s", e)
        await log_activity(
            session,
            action="add_list",
            success=False,
            user_id=user_id,
        )


async def delete_list_with_stats_log(
        session: AsyncSession,
        user_id: int,
        list_id: int,
):
    try:
        list_id = await db_delete_list(session, user_id, list_id)
        await update_stats_on_list_deleted(session, user_id)
        await log_activity(
            session,
            action="delete_list",
            success=True,
            user_id=user_id,
            list_id=list_id,
        )
    except Exception as e:
        logger.exception("Failed to add list: %s", e)
        await log_activity(
            session,
            action="delete_list",
            success=False,
            user_id=user_id,
        )


async def change_parent_list_with_log(
        session: AsyncSession,
        user_id: int,
        list_id: int,
        old_parent_list_id: int | None,
        new_parent_list_id: int,
):
    logger.debug(
        "Обновление базы данны при изменении для пользователя id=%d "
        "у списка id=%d родительского списка с id=%r на id=%d",
        user_id, list_id, old_parent_list_id, new_parent_list_id
    )
    try:
        await change_parent_list(session, list_id, new_parent_list_id)
        await log_activity(
            session,
            action="change_parent_list",
            success=True,
            user_id=user_id,
            list_id=list_id,
            old_value=old_parent_list_id,
            new_value=new_parent_list_id,
        )
        logger.debug(
            "Обновлена база данных при изменении для пользователя id=%d "
            "у списка id=%d родительского списка с id=%r на id=%d",
            user_id, list_id, old_parent_list_id, new_parent_list_id
        )
    except Exception as e:
        logger.exception(
            "Ошибка при обновлении базы данных при изменении для "
            "пользователя id=%d у списка id=%d родительского списка с id=%r на id=%d: %s",
            user_id, list_id, old_parent_list_id, new_parent_list_id, e
        )
        await log_activity(
            session,
            action="change_parent_list",
            success=False,
            user_id=user_id,
            list_id=list_id,
            old_value=old_parent_list_id,
        )
