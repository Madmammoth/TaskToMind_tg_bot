import logging
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select, update, func, and_, exists, delete, case
from sqlalchemy.dialects.postgresql import insert as upsert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from database.models import (
    User, TaskList, UserTag, ListAccess, AccessRoleEnum,
    ActivityLog, Task, TaskStatusEnum, TaskInList, TaskAccess,
    UserAchievement, Achievement, LevelEnum,
)
from database.models.enums import SystemListTypeEnum
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
            titles = [
                ("Корзина", SystemListTypeEnum.TRASH),
                ("Входящие", SystemListTypeEnum.INBOX),
                ("Архив", SystemListTypeEnum.ARCHIVE),
                ("Работа", SystemListTypeEnum.NONE),
                ("Быт", SystemListTypeEnum.NONE),
            ]
            default_lists = [TaskList(title=title, is_protected=is_protected)
                             for title, is_protected in titles]
            session.add_all(default_lists)
            await session.flush()

            session.add_all([
                ListAccess(
                    user_id=telegram_id,
                    list_id=lst.list_id,
                    role=AccessRoleEnum.OWNER,
                    granted_by=telegram_id,
                    position=pos
                ) for pos, lst in enumerate(default_lists, start=0)
            ])

            session.add_all([
                UserTag(user_id=telegram_id, tag_id=tag_id)
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
    access_exists = (
        select(TaskAccess).where(
            TaskAccess.task_id == task_id,
            TaskAccess.user_id == user_id,
            TaskAccess.role.in_([
                AccessRoleEnum.OWNER,
                AccessRoleEnum.EDITOR,
            ]),
        ).exists()
    )
    stmt = (
        update(Task)
        .where(
            Task.task_id == task_id,
            Task.status == TaskStatusEnum.NEW,
            access_exists,
        )
        .values(status=TaskStatusEnum.IN_PROGRESS)
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
    logger.debug("Entering update_stats_achievs_on_task_added...")
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
            select(UserAchievement).where(UserAchievement.user_id == user_id)
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
                    "т.к. нет связи юзер-ачивка или "
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
            stmt_bulk = upsert(UserAchievement).values(ua_upserts)
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
        user_id: int,
        task_data: dict,
):
    """
    Добавление задачи пользователем
    :param session: сессия СУБД
    :param user_id: ID пользователя
    :param task_data: настройки задачи
    """
    try:
        if "list_id" in task_data:
            list_query = (
                select(TaskList)
                .join(ListAccess)
                .where(
                    TaskList.list_id == int(task_data["list_id"]),
                    ListAccess.user_id == user_id,
                    ListAccess.role.in_([
                        AccessRoleEnum.OWNER,
                        AccessRoleEnum.EDITOR,
                    ]),
                )
            )
        else:
            list_title = task_data.get("list_title", "Входящие")
            list_query = (
                select(TaskList)
                .join(ListAccess)
                .where(
                    TaskList.title == list_title,
                    ListAccess.user_id == user_id,
                    ListAccess.role.in_([
                        AccessRoleEnum.OWNER,
                        AccessRoleEnum.EDITOR,
                    ]),
                )
            )
        task_list = (await session.execute(list_query)).scalar_one_or_none()
        if not task_list:
            raise ValueError("Список не найден или недоступен пользователю")

        task = Task(
            title=task_data["task_title"],
            description=task_data["task_description"],
            message_id=task_data.get("message_id"),
            priority=task_data.get("priority"),
            urgency=task_data.get("urgency"),
            status=TaskStatusEnum.NEW,
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
            TaskInList(
                list_id=task_list.list_id,
                task_id=task.task_id,
            )
        )

        session.add(
            TaskAccess(
                task_id=task.task_id,
                user_id=user_id,
                role=AccessRoleEnum.OWNER,
                granted_by=user_id,
            )
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


async def upsert_user_with_log(
        session: AsyncSession,
        user_id: int,
        first_name: str,
        last_name: str | None = None,
        username: str | None = None,
):
    """
    Запись лога при добавлении или обновлении
    данных пользователя в таблице users
    :param session: сессия СУБД
    :param user_id: ID пользователя
    :param first_name: имя пользователя
    :param last_name: фамилия пользователя
    :param username: ник пользователя
    :return: None
    """
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


async def get_ordered_user_lists(
        session: AsyncSession,
        user_id: int,
        mode: str = "normal",
) -> list[dict[str, Any]]:
    """
    Возвращает иерархию списков пользователя с позиционными префиксами
    :param session: сессия СУБД
    :param user_id: ID пользователя
    :param mode: режим отображения списков
    :return: список {list_id, list_title, pos}
    """
    logger.debug(
        "Запрос и сортировка по позиции списков пользователя id=%d",
        user_id,
    )

    stmt = (
        select(
            TaskList.list_id,
            TaskList.title,
            TaskList.parent_list_id,
            TaskList.system_type,
            ListAccess.position,

        )
        .join(ListAccess, ListAccess.list_id == TaskList.list_id)
        .where(ListAccess.user_id == user_id)
        .where(ListAccess.position != 0)
    )

    if mode == "add_in_list":
        logger.debug("show_lists_mode=add_in_list")
        stmt = stmt.where(TaskList.system_type
        .not_in([
            SystemListTypeEnum.INBOX,
            SystemListTypeEnum.ARCHIVE,
        ]))
    elif mode == "add_task":
        logger.debug("show_lists_mode=add_task")
        stmt = stmt.where(TaskList.system_type != SystemListTypeEnum.ARCHIVE)

    result = await session.execute(stmt)
    rows = result.all()
    if not rows:
        logger.debug("rows is empty")
        return []
    logger.debug("rows=%s", rows)

    sub_lists_map: dict[int | None, list] = defaultdict(list)
    nodes: dict[int, dict] = {}
    for (list_id, title, parent_list_id, system_type, position) in rows:
        nodes[list_id] = {
            "list_id": list_id,
            "list_title": title,
            "parent_list_id": parent_list_id,
            "system_type": system_type,
            "position": position,
        }
        sub_lists_map[parent_list_id].append(nodes[list_id])

    ordered_lists: list[dict[str, Any]] = []

    def traverse(parent_id: int | None, prefix: str):
        sub_lists = sub_lists_map.get(parent_id, [])
        sub_lists.sort(key=lambda n: n["position"])
        for sub_list in sub_lists:
            comp = f"{sub_list['position']}."
            pos = f"{prefix}{comp}"
            ordered_lists.append({
                "list_id": str(sub_list["list_id"]),
                "list_title": sub_list["list_title"],
                "pos": pos,
            })
            traverse(sub_list["list_id"], pos)

    traverse(None, "")
    logger.debug(
        "Получено списков: %d, пользователя id=%d", len(rows), user_id
    )
    return ordered_lists


async def db_add_list(
        session: AsyncSession,
        user_id: int,
        list_data: dict,
):
    """
    Добавление списка задач пользователем
    :param session: сессия СУБД
    :param user_id: ID пользователя
    :param list_data: параметры добавляемого списка задач
    :return: присвоенный list_id списка задач
    """
    try:
        in_list_id = list_data.get("in_list_id")
        if in_list_id:
            in_list_id = int(in_list_id)
        list_title = list_data.get("new_list_title")

        task_list = TaskList(
            title=list_title,
            parent_list_id=in_list_id,
        )
        session.add(task_list)
        await session.flush()

        parent_condition = (
            TaskList.parent_list_id.is_(None)
            if in_list_id is None
            else TaskList.parent_list_id == in_list_id
        )

        stmt = (
            select(func.coalesce(func.max(ListAccess.position), 0))
            .join(TaskList, ListAccess.list_id == TaskList.list_id)
            .where(
                and_(
                    ListAccess.user_id == user_id,
                    parent_condition,
                )
            )
        )
        result = await session.execute(stmt)
        max_pos = result.scalar() or 0
        position = max_pos + 1

        session.add(
            ListAccess(
                list_id=task_list.list_id,
                user_id=user_id,
                role=AccessRoleEnum.OWNER,
                granted_by=user_id,
                position=position,
                parent_list_id=in_list_id,
            )
        )

        await session.commit()
        logger.debug(
            "Список задач id=%d добавлен пользователю id=%d "
            "(parent_list_id=%s, position=%d)",
            task_list.list_id, user_id, in_list_id, position,
        )
    except Exception as e:
        await session.rollback()
        logger.exception("Ошибка в db_add_list для пользователя "
                         f"{user_id}: {e}")
        raise

    return task_list.list_id


async def update_stats_achievs_on_list_added(
        session: AsyncSession,
        user_id: int,
):
    """
    Проверяет и обновляет статистику и достижения пользователя
    при добавлении списка
    :param session: сессия СУБД
    :param user_id: ID пользователя
    """
    logger.debug("Entering update_stats_achievs_on_list_added...")
    try:
        stmt_upsert_stats = upsert(UserStats).values(
            user_id=user_id,
            lists_created=1,
        )
        stmt_upsert_stats = stmt_upsert_stats.on_conflict_do_update(
            index_elements=["user_id"],
            set_={
                "lists_created": (UserStats.lists_created
                                  + stmt_upsert_stats.excluded.lists_created),
                "updated_at": func.now(),
            },
        ).returning(UserStats)
        result = await session.execute(stmt_upsert_stats)
        user_stats = result.scalar_one()
        logger.debug("Обновлена статистика пользователя id=%d", user_id)

        category = "lists_created"
        achievements_query = await session.execute(
            select(Achievement).where(Achievement.category == category)
        )
        achievements = achievements_query.scalars().all()

        ua_query = await session.execute(
            select(UserAchievement).where(UserAchievement.user_id == user_id)
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
                    "т.к. нет связи юзер-ачивка или "
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
            stmt_bulk = upsert(UserAchievement).values(ua_upserts)
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
            "Ошибка в update_achievements_and_stats_on_list_added "
            "для пользователя id=%d: %s", user_id, e
        )
        raise


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
    except Exception as e:
        logger.exception("Failed to add list: %s", e)
        await log_activity(
            session,
            action="add_list",
            success=False,
            user_id=user_id,
        )


async def get_user_tasks_in_list(
        session: AsyncSession,
        user_id: int,
        list_id: int,
):
    """
    Запрос задач в списке задач
    :param session: сессия СУБД
    :param user_id: ID пользователя
    :param list_id: ID списка задач
    :return: список задач
    """
    logger.debug(
        "Запрос задач в списке id=%d пользователя id=%d",
        list_id, user_id,
    )
    stmt = (
        select(Task)
        .join(TaskInList)
        .where(
            TaskInList.list_id == list_id,
            exists().where(
                and_(
                    TaskAccess.task_id == Task.task_id,
                    TaskAccess.user_id == user_id,
                )
            )
        )
    )

    result = await session.scalars(stmt)
    tasks = result.all()

    if not tasks:
        return []

    logger.debug(
        "Получено задач: %d, списка id=%d, пользователя id=%d",
        len(tasks), list_id, user_id,
    )
    return tasks


async def get_user_sub_lists_in_list(
        session: AsyncSession,
        user_id: int,
        list_id: int,
):
    """
    Запрос подсписков в списке задач
    :param session: сессия СУБД
    :param user_id: ID пользователя
    :param list_id: ID списка задач
    :return: список подсписков
    """
    logger.debug(
        "Запрос подсписков в списке id=%d пользователя id=%d",
        list_id, user_id,
    )

    stmt = (
        select(TaskList)
        .join(ListAccess, ListAccess.list_id == TaskList.list_id)
        .where(
            ListAccess.user_id == user_id,
            TaskList.parent_list_id == list_id,
        )
        .order_by(ListAccess.position)
    )

    result = await session.scalars(stmt)
    sub_lists = result.all()

    if not sub_lists:
        return []

    logger.debug(
        "Получено подсписков: %d, списка id=%d, пользователя id=%d",
        len(sub_lists), list_id, user_id,
    )
    return sub_lists
