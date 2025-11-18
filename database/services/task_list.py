import logging
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Sequence

from sqlalchemy import Row
from sqlalchemy.ext.asyncio import AsyncSession

from database.crud.achievement import (
    get_achievements_by_categories,
    get_user_achievements,
    upsert_user_achievements
)
from database.crud.stats import upsert_user_stats_on_list_added, \
    update_stats_on_list_deleted
from database.crud.task_list import (
    create_list_access,
    get_max_position,
    create_list, db_delete_list
)
from database.crud.tracking import log_activity

logger = logging.getLogger(__name__)


def build_ordered_hierarchy(rows: Sequence[Row]) -> list[dict]:
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
    logger.debug("Получено списков: %d", len(rows))
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
        parent_id = list_data.get("in_list_id")
        if parent_id:
            parent_id = int(parent_id)

        list_title = list_data["new_list_title"]

        task_list = await create_list(session, list_title, parent_id)

        max_pos = await get_max_position(session, user_id, parent_id)
        position = max_pos + 1

        await create_list_access(
            session=session,
            list_id=task_list.list_id,
            user_id=user_id,
            parent_id=parent_id,
            position=position,
        )

        await session.commit()
        logger.debug(
            "Добавлен список задач id=%d пользователю id=%d",
            task_list.list_id, user_id
        )
    except Exception as e:
        await session.rollback()
        logger.exception("Ошибка в db_add_list для пользователя "
                         f"{user_id}: {e}")
        raise

    await session.commit()
    logger.debug(
        "Список задач id=%d добавлен пользователю id=%d "
        "(parent_list_id=%s, position=%d)",
        task_list.list_id, user_id, parent_id, position,
    )

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
        user_stats = await upsert_user_stats_on_list_added(session, user_id)

        categories = ["lists_created"]
        achievements = await get_achievements_by_categories(session,
                                                            categories)
        user_achievements = await get_user_achievements(session, user_id)
        updates = []
        for achievement in achievements:
            prev_ach = achievement.previous_achievement_id
            if prev_ach and (not user_achievements[prev_ach]
                             or not user_achievements[prev_ach].is_completed):
                logger.debug(
                    "Пропуск достижения id=%d, т.к. для него требуется "
                    "выполнение предыдущего достижения id=%d",
                    achievement.achievement_id, prev_ach,
                )
                continue

            current_value = getattr(user_stats, achievement.category, 0)
            is_completed = current_value >= achievement.required_count

            updates.append({
                "user_id": user_id,
                "achievement_id": achievement.achievement_id,
                "progress": current_value,
                "is_completed": is_completed,
                "unlocked_at": (datetime.now(timezone.utc)
                                if is_completed else None),
            })

        if updates:
            await upsert_user_achievements(session, user_id, updates)

        await session.commit()
        logger.debug(
            "Обновлены статистика и достижения для пользователя id=%d",
            user_id,
        )
    except Exception as e:
        await session.rollback()
        logger.exception(
            "Ошибка в update_achievements_and_stats_on_list_added "
            "для пользователя id=%d: %s",
            user_id, e
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
