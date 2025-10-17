import logging
from datetime import datetime, timezone

from sqlalchemy import select, update, func
from sqlalchemy.dialects.postgresql import insert as upsert
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import (
    User, TaskList, UserList, UserTags, ListAccess, AccessRoleEnum,
    ActivityLog, Task, TaskStatusEnum, UserListTask, TaskAccess,
    UserAchievements, Achievement, LevelEnum,
)
from database.models.user import UserStats

logger = logging.getLogger(__name__)


def filter_kwargs(model, kwargs: dict) -> dict:
    """
    Фильтрация по доступности ключей в таблице
    :param model: модель таблицы
    :param kwargs: ключи-значения для фильтрации
    :return: словарь с ключами-значениями, подходящими для таблицы
    """
    columns = {c.name for c in model.__table__.columns}
    return {k: v for k, v in kwargs.items() if k in columns}


async def log_activity(
        session: AsyncSession,
        action: str,
        success: bool = True,
        **kwargs,
):
    """
    Запись логов действий пользователя
    :param session: сессия СУБД
    :param action: наименование действия
    :param success: успешность записи действия в БД
    :param kwargs: дополнительные сведения о действии
    :return: None
    """
    data = filter_kwargs(ActivityLog, kwargs)
    try:
        log_entry = ActivityLog(
            action=action,
            success=success,
            **data,
        )
        session.add(log_entry)
        await session.commit()
    except Exception as e:
        logger.exception("Failed to write activity log (%s): %s", action, e)
        await session.rollback()


async def upsert_user(
        session: AsyncSession,
        telegram_id: int,
        first_name: str,
        last_name: str | None = None,
        username: str | None = None,
):
    """
    Добавление или обновление пользователя
    в таблице users
    :param session: сессия СУБД
    :param telegram_id: ID пользователя
    :param first_name: имя пользователя
    :param last_name: фамилия пользователя
    :param username: ник пользователя
    """
    try:
        old_user = await session.get(User, telegram_id)

        user_stmt = upsert(User).values(
            telegram_id=telegram_id,
            first_name=first_name,
            last_name=last_name,
            username=username,
        ).on_conflict_do_update(
            index_elements=["telegram_id"],
            set_={
                "first_name": first_name,
                "last_name": last_name,
                "username": username,
            },
        )
        await session.execute(user_stmt)

        if not old_user:
            default_lists = [
                TaskList(list_name=name)
                for name in ("Входящие", "Работа", "Быт")
            ]
            session.add_all(default_lists)
            await session.flush()

            session.add_all([
                UserList(
                    user_id=telegram_id,
                    list_id=lst.list_id,
                    is_owner=True
                ) for lst in default_lists
            ])

            session.add_all([
                ListAccess(
                    user_id=telegram_id,
                    list_id=lst.list_id,
                    role=AccessRoleEnum.OWNER,
                    granted_by=telegram_id
                ) for lst in default_lists
            ])

            session.add_all([
                UserTags(user_id=telegram_id, tag_id=tag_id)
                for tag_id in range(1, 14)
            ])

            session.add(UserStats(user_id=telegram_id))
            await session.commit()
            logger.info("Добавлен новый пользователь id=%d", telegram_id)
            return {"action": "new_user"}

        changes = {
            field: {"old": getattr(old_user, field), "new": locals()[field]}
            for field in ("first_name", "last_name", "username")
            if getattr(old_user, field) != locals()[field]
        }
        await session.commit()
        if changes:
            logger.debug("Обновлены данные пользователя id=%d", telegram_id)
            return {"action": "update_user", "extra": changes}
        logger.debug("Нет новых данных у пользователя id=%d", telegram_id)
        return {"action": "update_user"}
    except Exception as e:
        await session.rollback()
        logger.exception("Ошибка в db_upsert_user для пользователя "
                         f"{telegram_id}: {e}")
        raise


# TODO заменить owner_id на связь из таблицы доступа,
#  заменить строки на энумы
async def mark_task_in_process(
        session: AsyncSession,
        task_id: int,
        user_id: int
):
    """
    Смена статуса задачи при взаимодействии пользователя с задачей
    :param session: сессия СУБД
    :param task_id: ID задачи
    :param user_id: ID пользователя
    :return: None
    """
    stmt = (
        update(Task)
        .where(
            Task.task_id == task_id,
            Task.owner_id == user_id,
            Task.status == "NEW")
        .values(status="IN_PROCESS")
    )
    await session.execute(stmt)
    await session.commit()


async def update_stats_achievs_on_task_added(
        session: AsyncSession,
        user_id: int,
        task_data: dict,
):
    """
    Проверяет и обновляет достижения
    при добавлении задачи
    :param session: сессия СУБД
    :param user_id: ID пользователя
    :param task_data: свойства задачи
    """
    logger.debug(f"Entering update_stats_achievs...")
    try:
        priority_column = f"{task_data.get(
            'priority', LevelEnum.LOW
        ).value.lower()}_priority_tasks_created"
        urgency_column = f"{task_data.get(
            'urgency', LevelEnum.LOW
        ).value.lower()}_urgency_tasks_created"

        stmt_upsert_stats = upsert(UserStats).values(
            user_id=user_id,
            tasks_created=1,
            recurring_tasks_created=int(
                task_data.get("is_recurring", False)
            ),
            checked_tasks_created=int(
                task_data.get("parent_task_id") is not None
            ),
            **{
                priority_column: 1,
                urgency_column: 1,
                "tags_per_task": len(task_data.get("tags", [])),
                "tags_assigned": len(task_data.get("tags", [])),
            }
        )
        stmt_upsert_stats = stmt_upsert_stats.on_conflict_do_update(
            index_elements=["user_id"],
            set_={
                "tasks_created": (UserStats.tasks_created
                                  + stmt_upsert_stats.excluded.tasks_created),
                "recurring_tasks_created": (
                        UserStats.recurring_tasks_created
                        + stmt_upsert_stats.excluded.recurring_tasks_created
                ),
                "checked_tasks_created": (
                        UserStats.checked_tasks_created
                        + stmt_upsert_stats.excluded.checked_tasks_created
                ),
                priority_column: (getattr(
                    UserStats, priority_column)
                                  + stmt_upsert_stats.excluded[priority_column]
                                  ),
                urgency_column: (getattr(
                    UserStats, urgency_column)
                                 + stmt_upsert_stats.excluded[urgency_column]
                                 ),
                "tags_per_task": func.greatest(
                    UserStats.tags_per_task,
                    stmt_upsert_stats.excluded.tags_per_task
                ),
                "tags_assigned": (
                        UserStats.tags_assigned
                        + stmt_upsert_stats.excluded.tags_assigned
                ),
                "updated_at": func.now(),
            },
        ).returning(UserStats)
        result = await session.execute(stmt_upsert_stats)
        user_stats = result.scalar_one()
        logger.debug("Обновлена статистика пользователя id=%d", user_id)

        categories = [
            "tasks_created",
            priority_column,
            urgency_column,
        ]
        if task_data.get("tags"):
            logger.debug(
                "Добавление к категориям 'tags_created', 'tags_assigned'"
            )
            categories.extend(["tags_per_task", "tags_assigned"])
        if task_data.get("is_recurring"):
            logger.debug("Добавление к категориям 'recurring_tasks_created'")
            categories.append("recurring_tasks_created")

        achievements_query = await session.execute(
            select(Achievement).where(Achievement.category.in_(categories))
        )
        achievements = achievements_query.scalars().all()

        ua_query = await session.execute(
            select(UserAchievements).where(UserAchievements.user_id == user_id)
        )
        user_achievements_map = {
            ua.achievement_id: ua for ua in ua_query.scalars().all()
        }

        ua_upserts = []

        for achievement in achievements:
            if achievement.previous_achievement_id:
                logger.debug(
                    "Проверка ачивки id=%d на "
                    "необходимость предшествующей ачивки id=%d",
                    achievement.achievement_id,
                    achievement.previous_achievement_id,
                )
                previous_ua = user_achievements_map.get(
                    achievement.previous_achievement_id)
                if not previous_ua or not previous_ua.is_completed:
                    logger.debug(
                        "Пропуск ачивки id=%d, "
                        "т.к. нет связи юзер-предыдущая ачивка "
                        "или предыдущая ачивка ещё не получена",
                        achievement.achievement_id,
                    )
                    continue

            ua = user_achievements_map.get(achievement.achievement_id)
            if ua and ua.is_completed:
                logger.debug(
                    "Пропуск ачивки id=%d "
                    "т.к. нет связи юзер-ачика или "
                    "ачивка уже получена",
                    achievement.achievement_id,
                )
                continue

            current_value = getattr(user_stats, achievement.category, 0)
            ua_is_completed = current_value >= achievement.required_count

            ua_upserts.append(
                {
                    "user_id": user_id,
                    "achievement_id": achievement.achievement_id,
                    "progress": current_value,
                    "is_completed": ua_is_completed,
                    "unlocked_at": (datetime.now(timezone.utc)
                                    if ua_is_completed else None),
                }
            )

        if ua_upserts:
            logger.debug("Связи юзер-ачивка получены")
            stmt_bulk = upsert(UserAchievements).values(ua_upserts)
            stmt_bulk = stmt_bulk.on_conflict_do_update(
                index_elements=["user_id", "achievement_id"],
                set_={
                    "progress": stmt_bulk.excluded.progress,
                    "is_completed": stmt_bulk.excluded.is_completed,
                    "unlocked_at": stmt_bulk.excluded.unlocked_at,
                    "updated_at": func.now(),
                },
            )
            await session.execute(stmt_bulk)

        logger.debug("Обновлены связи в таблице 'user_achievements'")
        await session.commit()

    except Exception as e:
        await session.rollback()
        logger.exception(
            "Ошибка в update_achievements_and_stats_on_task_added "
            f"для пользователя {user_id}: {e}")
        raise


async def db_add_task(
        session: AsyncSession,
        telegram_id: int,
        task_data: dict,
):
    """
    Добавляет задачу в базу данных
    :param session: сессия СУБД
    :param telegram_id: ID пользователя
    :param task_data: настройки задачи
    """
    try:
        if "list_id" in task_data:
            list_query = (
                select(TaskList)
                .join(UserList)
                .where(
                    TaskList.list_id == task_data["list_id"],
                    UserList.user_id == telegram_id,
                )
            )
        else:
            list_name = task_data.get("list_name", "Входящие")
            list_query = (
                select(TaskList)
                .join(UserList)
                .where(
                    TaskList.list_name == list_name,
                    UserList.user_id == telegram_id,
                )
            )
        task_list = (await session.execute(list_query)).scalar_one_or_none()
        if not task_list:
            raise ValueError("Список не найден или недоступен пользователю")

        task = Task(
            title=task_data["task_title"],
            description=task_data["task_description"],
            creator_id=telegram_id,
            message_id=task_data.get("message_id"),
            priority=task_data.get("priority"),
            urgency=task_data.get("urgency"),
            status=TaskStatusEnum.NEW,
            owner_id=telegram_id,
            parent_task_id=task_data.get("parent_task_id"),
            deadline=task_data.get("deadline"),
            is_recurring=task_data.get("is_recurring", False),
            recurrence_rule_id=task_data.get("recurrence_rule_id"),
            duration=task_data.get("duration"),
            remind=task_data.get("remind", False),
        )
        session.add(task)
        await session.flush()

        session.add(
            UserListTask(
                user_id=telegram_id,
                list_id=task_list.list_id,
                task_id=task.task_id,
            )
        )

        session.add(
            TaskAccess(
                task_id=task.task_id,
                user_id=telegram_id,
                role=AccessRoleEnum.OWNER,
                granted_by=telegram_id,
            )
        )
        logger.debug(
            "Задача id=%d пользователя id=%d добавлена",
            task.task_id, telegram_id,
        )
        await session.commit()
    except Exception as e:
        await session.rollback()
        logger.exception("Ошибка в add_task для пользователя "
                         f"{telegram_id}: {e}")
        raise
    return task_list.list_id, task.task_id


async def upsert_user_with_log(
        session: AsyncSession,
        user_id: int,
        first_name: str,
        last_name: str | None = None,
        username: str | None = None,
):
    try:
        data = await upsert_user(
            session, user_id, first_name, last_name, username
        )
        await log_activity(session, success=True, user_id=user_id, **data)
    except Exception as e:
        logger.exception("Failed to upsert user: %s", e)
        await log_activity(session, "new_user", False, user_id=user_id)


async def add_task_with_stats_achievs_log(
        session: AsyncSession,
        user_id: int,
        task_data: dict,
):
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
