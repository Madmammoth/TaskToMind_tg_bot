import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.crud.task import (
    complete_task,
    change_list_for_task,
    not_complete_task,
    cancel_task,
    not_cancel_task,
    db_delete_task,
)
from app.database.crud.task_list import (
    get_user_archive_list_id,
    get_previous_list_id,
    get_user_trash_list_id,
)
from app.database.crud.tracking import log_activity
from app.database.models import TaskStatusEnum
from app.database.services.achievement import update_stats_achievs_on_task_added
from app.database.services.task import (
    db_add_task,
    update_users_stats_achievs_on_task_completed,
    update_users_stats_achievs_on_task_uncompleted,
    update_users_stats_achievs_on_task_canceled,
    update_users_stats_achievs_on_task_uncanceled,
)

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


async def complete_task_with_stats_achievs_log(
        session: AsyncSession,
        user_id: int,
        task_data: dict,
):
    """
    Обновляет базу данных при выполнении задачи
    :param session: сессия СУБД
    :param user_id: ID пользователя,
    который отмечает задачу как выполненную
    :param task_data: параметры выполненной задачи
    :return: None
    """
    logger.debug("Обновление базы данных при выполнении задачи...")
    task_id = task_data.get("task_id")
    try:
        await complete_task(session, task_id)
        list_id = task_data.get("selected_list_id")
        archive_list_id = await get_user_archive_list_id(session, user_id)
        await change_list_for_task(session, task_id, list_id, archive_list_id)
        await update_users_stats_achievs_on_task_completed(session, task_data)
        await log_activity(
            session,
            action="complete_task",
            success=True,
            user_id=user_id,
            task_id=task_id,
            extra={"old_list_id": list_id, "new_list_id": archive_list_id}
        )
        logger.debug(
            "Обновлена база данных при выполнении задачи id=%d", task_id
        )
    except Exception as e:
        logger.exception(
            "Ошибка при обновлении базы данных "
            "при выполнении задачи id=%d: %s",
            task_id, e,
        )
        await log_activity(
            session,
            action="complete_task",
            success=False,
            user_id=user_id,
            task_id=task_id,
        )


async def not_complete_task_with_stats_achievs_log(
        session: AsyncSession,
        user_id: int,
        task_data: dict,
):
    """
    Обновляет базу данных при возвращении задачи в работу
    :param session: сессия СУБД
    :param user_id: ID пользователя,
    который возвращает задачу в работу
    :param task_data: параметры возвращаемой в работу задачи
    :return: None
    """
    task_id = task_data.get("task_id")
    logger.debug(
        "Обновление базы данных при возвращении пользователем id=%d в работу задачи id=%d",
        user_id, task_id,
    )
    try:
        await not_complete_task(session, task_id)
        list_id = task_data.get("selected_list_id")
        previous_list_id = await get_previous_list_id(
            session, task_id, list_id
        )
        await change_list_for_task(session, task_id, list_id, previous_list_id)
        await update_users_stats_achievs_on_task_uncompleted(session,
                                                             task_data)
        await log_activity(
            session,
            action="not_complete_task",
            success=True,
            user_id=user_id,
            task_id=task_id,
        )
        logger.debug(
            "Обновлена база данных при возвращении "
            "пользователем id=%d в работу задачи id=%d",
            user_id, task_id
        )
    except Exception as e:
        logger.exception(
            "Ошибка при обновлении базы данных при возвращении "
            "пользователем id=%d в работу задачи id=%d: %s",
            user_id, task_id, e,
        )
        await log_activity(
            session,
            action="not_complete_task",
            success=False,
            user_id=user_id,
            task_id=task_id,
        )


async def cancel_task_with_stats_achievs_log(
        session: AsyncSession,
        user_id: int,
        task_data: dict,
):
    """
    Обновляет базу данных при отмене задачи
    :param session: сессия СУБД
    :param user_id: ID пользователя, который отменяет задачу
    :param task_data: параметры отменяемой задачи
    :return: None
    """
    logger.debug(
        "Обновление базы данных при отмене пользователем id=%d задачи...",
        user_id
    )
    task_id = task_data.get("task_id")
    logger.debug("...id=%d", task_id)
    try:
        await cancel_task(session, task_id)
        list_id = task_data.get("selected_list_id")
        trash_list_id = await get_user_trash_list_id(session, user_id)
        await change_list_for_task(session, task_id, list_id, trash_list_id)
        await update_users_stats_achievs_on_task_canceled(session, task_data)
        await log_activity(
            session,
            action="cancel_task",
            success=True,
            user_id=user_id,
            task_id=task_id,
            old_value=task_data.get("status"),
            new_value=TaskStatusEnum.CANCELED,
            extra={"old_list_id": list_id, "new_list_id": trash_list_id}
        )
        logger.debug(
            "Обновлена база данных при отмене пользователем id=%d "
            "задачи id=%d",
            user_id, task_id
        )
    except Exception as e:
        logger.exception(
            "Ошибка при обновлении базы данных при отмене "
            "пользователем id=%d задачи id=%d: %s",
            user_id, task_id, e,
        )
        await log_activity(
            session,
            action="cancel_task",
            success=False,
            user_id=user_id,
            task_id=task_id,
            old_value=task_data.get("status"),
            new_value=task_data.get("status"),
        )


async def not_cancel_task_with_stats_achievs_log(
        session: AsyncSession,
        user_id: int,
        task_data: dict,
):
    """
    Обновляет базу данных при возвращении задачи в работу после отмены
    :param session: сессия СУБД
    :param user_id: ID пользователя,
    который возвращает задачу в работу
    :param task_data: параметры возвращаемой в работу задачи
    :return: None
    """
    logger.debug(
        "Обновление базы данных при возвращении "
        "пользователем id=%d в работу задачи...",
        user_id
    )
    task_id = task_data.get("task_id")
    logger.debug("...id=%d", task_id)
    try:
        await not_cancel_task(session, task_id)
        list_id = task_data.get("selected_list_id")
        previous_list_id = await get_previous_list_id(
            session, task_id, list_id
        )
        await change_list_for_task(session, task_id, list_id, previous_list_id)
        await update_users_stats_achievs_on_task_uncanceled(session,
                                                            task_data)
        await log_activity(
            session,
            action="not_cancel_task",
            success=True,
            user_id=user_id,
            task_id=task_id,
            old_value=task_data.get("status"),
            new_value=TaskStatusEnum.IN_PROGRESS,
        )
        logger.debug(
            "Обновлена база данных при возвращении "
            "пользователем id=%d в работу задачи id=%d",
            user_id, task_id
        )
    except Exception as e:
        logger.exception(
            "Ошибка при обновлении базы данных при возвращении "
            "пользователем id=%d в работу задачи id=%d: %s",
            user_id, task_id, e,
        )
        await log_activity(
            session,
            action="not_cancel_task",
            success=False,
            user_id=user_id,
            task_id=task_id,
            old_value=task_data.get("status"),
            new_value=task_data.get("status"),
        )


async def delete_task_with_log(
        session: AsyncSession,
        user_id: int,
        task_data: dict,
):
    """
    Обновляет базу данных при удалении задачи
    :param session: сессия СУБД
    :param user_id: ID пользователя, который удаляет задачу
    :param task_data: параметры удаляемой задачи
    :return: None
    """
    task_id = task_data.get("task_id")
    logger.debug(
        "Обновление базы данных при удалении пользователем id=%d задачи id=%d",
        user_id, task_id,
    )
    async with session.begin():
        await db_delete_task(session, task_id)
        await log_activity(
            session,
            action="delete_task",
            success=True,
            user_id=user_id,
        )
        logger.debug(
            "Обновлена база данных при удалении пользователем id=%d задачи id=%d",
            user_id, task_id
        )


async def change_list_for_task_with_log(
        session: AsyncSession,
        user_id: int,
        task_id: int,
        old_list_id: int,
        new_list_id: int,
):
    logger.debug(
        "Обновление базы данны при изменении для пользователя id=%d "
        "у задачи id=%d списка с id=%d на id=%d",
        user_id, task_id, old_list_id, new_list_id
    )
    try:
        await change_list_for_task(session, task_id, old_list_id, new_list_id)
        await log_activity(
            session,
            action="change_list_for_task",
            success=True,
            user_id=user_id,
            task_id=task_id,
            old_value=old_list_id,
            new_value=new_list_id,
        )
        logger.debug(
            "Обновлена база данных при изменении для пользователя id=%d "
            "у задачи id=%d списка с id=%d на id=%d",
            user_id, task_id, old_list_id, new_list_id
        )
    except Exception as e:
        logger.exception(
            "Ошибка при обновлении базы данных при изменении для "
            "пользователя id=%d у задачи id=%d списка с id=%d на id=%d: %s",
            user_id, task_id, old_list_id, new_list_id, e
        )
        await log_activity(
            session,
            action="change_list_for_task",
            success=False,
            user_id=user_id,
            task_id=task_id,
            list_id=old_list_id,
        )
