import logging

from sqlalchemy.ext.asyncio import AsyncSession

from database.crud.task import (
    make_list_query_by_list_id,
    make_list_query_by_list_title,
    create_task,
    create_list_task_link,
    create_task_access
)
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
            action="create_task",
            success=True,
            user_id=user_id,
            list_id=list_id,
            task_id=task_id,
        )
    except Exception as e:
        logger.exception("Failed to add task: %s", e)
        await log_activity(
            session,
            action="create_task",
            success=False,
            user_id=user_id,
        )


async def db_add_task(
        session: AsyncSession,
        user_id: int,
        task_data: dict,
):
    """
    Добавление задачи пользователем
    :param session: сессия СУБД
    :param user_id: ID пользователя
    :param task_data: настройки задачи
    """
    logger.debug(
        "Внесение изменений в базу данных "
        "при создании задачи пользователем id=%d",
        user_id,
    )
    try:
        if "list_id" in task_data:
            list_id = int(task_data["list_id"])
            list_query = make_list_query_by_list_id(user_id, list_id)
        else:
            list_title = task_data.get("list_title", "Входящие")
            list_query = make_list_query_by_list_title(user_id, list_title)
        task_list = (await session.execute(list_query)).scalar_one_or_none()
        if not task_list:
            raise ValueError("Список не найден или недоступен пользователю")

        task = await create_task(session, task_data)

        create_list_task_link(
            session=session,
            list_id=task_list.list_id,
            task_id=task.task_id,
        )

        create_task_access(
            session=session,
            user_id=user_id,
            task_id=task.task_id,
        )

        logger.debug(
            "Задача id=%d пользователя id=%d добавлена",
            task.task_id, user_id,
        )
        await session.commit()
    except Exception as e:
        await session.rollback()
        logger.exception("Ошибка в db_add_task для пользователя "
                         f"{user_id}: {e}")
        raise
    return task_list.list_id, task.task_id
