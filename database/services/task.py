import logging

from sqlalchemy.ext.asyncio import AsyncSession

from database.crud.task import db_add_task
from database.crud.tracking import log_activity
from database.services.achievement import update_stats_achievs_on_task_added

logger = logging.getLogger(__name__)


async def add_task_with_stats_achievs_log(
        session: AsyncSession,
        user_id: int,
        task_data: dict,
):
    """
    Проверяет и обновляет статистику и достижения пользователя
    с записью лога при добавлении задачи
    :param session: сессия СУБД
    :param user_id: ID пользователя
    :param task_data: параметры добавляемой задачи
    :return: None
    """
    try:
        list_id, task_id = await db_add_task(session, user_id, task_data)
        await update_stats_achievs_on_task_added(session, user_id, task_data)
        await log_activity(
            session,
            action="add_task",
            success=True,
            user_id=user_id,
            list_id=list_id,
            task_id=task_id,
        )
    except Exception as e:
        logger.exception("Failed to add task: %s", e)
        await log_activity(
            session,
            action="add_task",
            success=False,
            user_id=user_id,
        )
