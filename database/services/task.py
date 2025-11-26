import logging
from typing import Any
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncSession

from database.crud.achievement import (
    get_achievements_by_categories,
    get_user_achievements,
    upsert_user_achievements,
    get_user_achievements_updates,
    get_user_achievements_rollback_updates,
    rollback_user_achievements
)
from database.crud.stats import (
    upsert_user_stats_on_task_completed,
    update_user_stats_on_task_uncompleted,
    upsert_user_stats_on_task_canceled,
    update_user_stats_on_task_uncanceled
)
from database.crud.task import (
    make_list_query_by_list_id,
    make_list_query_by_list_title,
    create_task,
    create_list_task_link,
    create_task_access,
    complete_task,
    get_task_users,
    get_stats_and_achievs_categories,
    get_task_for_user,
    get_list_for_task,
    get_task_access,
    not_complete_task,
    cancel_task,
    not_cancel_task,
    change_list_for_task,
)
from database.crud.task_list import(
    get_user_trash_list_id,
    get_user_archive_list_id,
    get_previous_list_id,
)
from database.crud.tracking import log_activity
from database.crud.user import get_user_timezone
from database.models import Task, TaskList, TaskAccess, TaskStatusEnum
from database.services.achievement import update_stats_achievs_on_task_added
from locales.ru import (
    PRIORITY_LABELS,
    URGENCY_LABELS,
    TASK_STATUS_LABELS,
    ACCESS_LABELS,
)

logger = logging.getLogger(__name__)


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


async def get_full_task_info(
        session: AsyncSession,
        user_id: int,
        task_id: int,
):
    logger.debug(
        "Получение полной информации о задаче id=%d пользователем id=%d",
        task_id, user_id
    )
    task = await get_task_for_user(session, user_id, task_id)
    if not task:
        logger.debug(
            "Задача id=%d не найдена или недоступна для пользователя id=%d",
            task_id, user_id
        )
        return None

    task_list = await get_list_for_task(session, task_id)
    if not task_list:
        logger.debug("Не найден список для задачи id=%d", task_id)
        return None

    access = await get_task_access(session, user_id, task_id)
    if not access:
        logger.debug(
            "Задача id=%d недоступна для пользователя id=%d",
            task_id, user_id
        )
        return None

    timezone = await get_user_timezone(session, user_id)

    return task, task_list, access, timezone


def make_task_data_for_dialog(
        task: Task,
        task_list: TaskList,
        access: TaskAccess,
        timezone: str,
) -> dict[str, Any]:
    logger.debug("Создание словаря параметров задачи id=%d", task.task_id)
    user_timezone = ZoneInfo(timezone)

    completed_at_format = task.completed_at
    if completed_at_format:
        completed_at_local = task.completed_at.astimezone(user_timezone)
        completed_at_format = completed_at_local.strftime("%d.%m.%Y в %H:%M")

    canceled_at_format = task.canceled_at
    if canceled_at_format:
        canceled_at_local = canceled_at_format.astimezone(user_timezone)
        canceled_at_format = canceled_at_local.strftime("%d.%m.%Y в %H:%M")

    task_data = {
        "task_id": task.task_id,
        "task_title": task.title,
        "description": task.description,
        "priority": task.priority,
        "priority_label": PRIORITY_LABELS.get(task.priority).capitalize(),
        "urgency": task.urgency,
        "urgency_label": URGENCY_LABELS.get(task.urgency).capitalize(),
        "status": task.status,
        "status_label": TASK_STATUS_LABELS.get(task.status).capitalize(),
        "is_shared": task.is_shared,
        "users": [],
        "parent_task_id": task.parent_task_id,
        "deadline": task.deadline,
        "completed_at": completed_at_format,
        "canceled_at": canceled_at_format,
        "postponed_count": task.postponed_count,
        "is_recurring": task.is_recurring,
        "recurrence_rule_id": task.recurrence_rules,
        "recurrence_rule_text": "",
        "duration": task.duration,
        "remind": task.remind,
        "list_id": task_list.list_id,
        "list_title": task_list.title,
        "role": ACCESS_LABELS.get(access.role).capitalize(),
        "has_checklist": False,
    }
    return task_data


async def update_users_stats_achievs_on_task_completed(
        session: AsyncSession,
        task_data: dict,
):
    """
    Проверяет и обновляет статистику и достижения пользователей
    при выполнении задачи
    :param session: сессия СУБД
    :param task_data: параметры выполненной задачи
    """
    logger.debug(
        "Обновление статистики и достижений пользователей "
        "при выполнении задачи..."
    )
    task_id = task_data.get("task_id")
    users = await get_task_users(session, task_id)
    categories = get_stats_and_achievs_categories(task_data, "complete")
    achievements = await get_achievements_by_categories(session, categories)
    stats_updates = dict.fromkeys(categories, 1)

    for user in users:
        user_id = user.telegram_id
        user_stats = await upsert_user_stats_on_task_completed(
            session, user_id, stats_updates
        )
        user_achievements = await get_user_achievements(session, user_id)
        achievs_updates = get_user_achievements_updates(
            user_id, achievements, user_achievements, user_stats
        )
        if achievs_updates:
            await upsert_user_achievements(session, user_id, achievs_updates)

        logger.debug(
            "Обновлены статистика и достижения для пользователя id=%d",
            user_id,
        )

    logger.debug(
        "Обновлена статистика и достижения при выполнении задачи "
        "для %d пользователей",
        len(users),
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
        list_id = task_data.get("list_id")
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


async def update_users_stats_achievs_on_task_uncompleted(
        session: AsyncSession,
        task_data: dict,
):
    """
    Проверяет и обновляет статистику и достижения пользователей
    при возвращении задачи в работу
    :param session: сессия СУБД
    :param task_data: параметры возвращаемой в работу задачи
    """
    logger.debug(
        "Обновление статистики и достижений пользователей "
        "при возвращении в работу задачи..."
    )
    task_id = task_data.get("task_id")
    logger.debug("...id=%d", task_id)
    users = await get_task_users(session, task_id)
    categories = get_stats_and_achievs_categories(task_data, "complete")
    achievements = await get_achievements_by_categories(session, categories)

    for user in users:
        user_id = user.telegram_id
        user_stats = await update_user_stats_on_task_uncompleted(
            session, user_id, categories
        )
        user_achievements = await get_user_achievements(session, user_id)
        achievs_rollback_updates = get_user_achievements_rollback_updates(
            user_id, achievements, user_achievements, user_stats
        )
        if achievs_rollback_updates:
            await rollback_user_achievements(
                session, user_id, achievs_rollback_updates
            )

        logger.debug(
            "Обновлены статистика и достижения для пользователя id=%d",
            user_id,
        )

    logger.debug(
        "Обновлена статистика и достижения "
        "при возвращении задачи в работу для %d пользователей",
        len(users),
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
    logger.debug(
        "Обновление базы данных при возвращении "
        "пользователем id=%d в работу задачи...",
        user_id
    )
    task_id = task_data.get("task_id")
    logger.debug("...id=%d", task_id)
    try:
        await not_complete_task(session, task_id)
        list_id = task_data.get("list_id")
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


async def update_users_stats_achievs_on_task_canceled(
        session: AsyncSession,
        task_data: dict,
):
    """
    Проверяет и обновляет статистику и достижения пользователей
    при отмене задачи
    :param session: сессия СУБД
    :param task_data: параметры отменяемой задачи
    """
    logger.debug(
        "Обновление статистики и достижений пользователей "
        "при отмене задачи..."
    )
    task_id = task_data.get("task_id")
    logger.debug("...id=%d", task_id)
    users = await get_task_users(session, task_id)
    categories = get_stats_and_achievs_categories(task_data, "cancel")
    achievements = await get_achievements_by_categories(session, categories)
    stats_updates = dict.fromkeys(categories, 1)

    for user in users:
        user_id = user.telegram_id
        user_stats = await upsert_user_stats_on_task_canceled(
            session, user_id, stats_updates
        )
        user_achievements = await get_user_achievements(session, user_id)
        achievs_updates = get_user_achievements_updates(
            user_id, achievements, user_achievements, user_stats
        )
        if achievs_updates:
            await upsert_user_achievements(session, user_id, achievs_updates)

        logger.debug(
            "Обновлены статистика и достижения для пользователя id=%d",
            user_id,
        )

    logger.debug(
        "Обновлена статистика и достижения при отмене задачи "
        "для %d пользователей",
        len(users),
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
        list_id = task_data.get("list_id")
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


async def update_users_stats_achievs_on_task_uncanceled(
        session: AsyncSession,
        task_data: dict,
):
    """
    Проверяет и обновляет статистику и достижения пользователей
    при смене статуса задачи с «Отменена» на «В работе»
    :param session: сессия СУБД
    :param task_data: параметры восстанавливаемой задачи
    """
    logger.debug(
        "Обновление статистики и достижений пользователей "
        "при смене статуса с «Отменена» на «В работе» задачи..."
    )
    task_id = task_data.get("task_id")
    logger.debug("...id=%d", task_id)
    users = await get_task_users(session, task_id)
    categories = get_stats_and_achievs_categories(task_data, "cancel")
    achievements = await get_achievements_by_categories(session, categories)

    for user in users:
        user_id = user.telegram_id
        user_stats = await update_user_stats_on_task_uncanceled(
            session, user_id, categories
        )
        user_achievements = await get_user_achievements(session, user_id)
        achievs_rollback_updates = get_user_achievements_rollback_updates(
            user_id, achievements, user_achievements, user_stats
        )
        if achievs_rollback_updates:
            await rollback_user_achievements(
                session, user_id, achievs_rollback_updates
            )

        logger.debug(
            "Обновлены статистика и достижения для пользователя id=%d",
            user_id,
        )

    logger.debug(
        "Обновлена статистика и достижения "
        "при возвращении задачи в работу для %d пользователей",
        len(users),
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
        list_id = task_data.get("list_id")
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