import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select, func, delete
from sqlalchemy.dialects.postgresql import insert as upsert
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Achievement, UserAchievement
from database.models.stats import UserStats

logger = logging.getLogger(__name__)


async def get_achievements_by_categories(
        session: AsyncSession,
        categories: list,
):
    logger.debug("Получение достижений по категориям %s", categories)
    result = await session.execute(
        select(Achievement).where(Achievement.category.in_(categories))
    )
    achievements = result.scalars().all()
    logger.debug(
        "Получено %d достижений из %d категорий",
        len(achievements), len(categories),
    )
    return achievements


async def get_user_achievements(
        session: AsyncSession,
        user_id: int,
):
    logger.debug(
        "Получение связей user_achievement пользователя id=%d",
        user_id,
    )
    result = await session.execute(
        select(UserAchievement).where(UserAchievement.user_id == user_id)
    )
    user_achievements_map = {
        user_achievement_link.achievement_id: user_achievement_link
        for user_achievement_link in result.scalars().all()
    }
    logger.debug("Получено %d связей", len(user_achievements_map))
    return user_achievements_map


def get_user_achievements_updates(
        user_id: int,
        achievements: list[Achievement],
        user_achievements: dict[int, UserAchievement],
        user_stats: list[UserStats]
) -> list[dict[str, Any]]:
    logger.debug(
        "Получение обновлений для связей пользователь-достижение "
        "пользователя id=%d",
        user_id
    )
    updates = []
    for achievement in achievements:
        prev_id = achievement.previous_achievement_id
        prev_completed = (
                prev_id is None
                or (user_achievements.get(prev_id)
                    and user_achievements[prev_id].is_completed)
        )
        if not prev_completed:
            logger.debug(
                "Пропуск достижения id=%d, т.к. для него требуется "
                "выполнение предыдущего достижения id=%d",
                achievement.achievement_id, prev_id,
            )
            continue

        current_value = getattr(user_stats, achievement.category, 0)
        new_completed = current_value >= achievement.required_count

        updates.append({
            "user_id": user_id,
            "achievement_id": achievement.achievement_id,
            "progress": current_value,
            "is_completed": new_completed,
            "unlocked_at": (datetime.now(timezone.utc)
                            if new_completed else None),
        })

    logger.debug(
        "Получено %d обновлений для связей пользователь-достижение",
        len(updates),
    )
    return updates


async def upsert_user_achievements(
        session: AsyncSession,
        user_id: int,
        updates: list[dict],
):
    logger.debug(
        "Вставка связей %s user_achievement пользователя id=%d",
        updates, user_id,
    )
    stmt = upsert(UserAchievement).values(updates)
    stmt = stmt.on_conflict_do_update(
        index_elements=["user_id", "achievement_id"],
        set_={
            "progress": stmt.excluded.progress,
            "is_completed": stmt.excluded.is_completed,
            "unlocked_at": stmt.excluded.unlocked_at,
            "updated_at": func.now(),
        },
    )
    await session.execute(stmt)
    logger.debug(
        "Обновлены связи user_achievement пользователя id=%d",
        user_id,
    )


def get_user_achievements_rollback_updates(
        user_id: int,
        achievements: list[Achievement],
        user_achievements: dict[int, UserAchievement],
        user_stats: list[UserStats]
) -> list[dict[str, Any]]:
    logger.debug(
        "Получение обратных обновлений для связей пользователь-достижение "
        "для пользователя id=%d",
        user_id
    )
    updates = []
    for achievement in achievements:
        prev_id = achievement.previous_achievement_id
        prev_completed = (
                prev_id is None
                or (user_achievements.get(prev_id)
                    and user_achievements[prev_id].is_completed)
        )

        current_value = getattr(user_stats, achievement.category, 0)
        still_completed = prev_completed and current_value >= achievement.required_count

        if not still_completed:
            updates.append({
                "user_id": user_id,
                "achievement_id": achievement.achievement_id,
                "progress": current_value,
                "is_completed": False,
                "unlocked_at": None,
            })
        else:
            updates.append({
                "user_id": user_id,
                "achievement_id": achievement.achievement_id,
                "progress": current_value,
                "is_completed": True,
            })

    logger.debug(
        "Получено %d обновлений для связей пользователь-достижение "
        "пользователя id=%d",
        len(updates), user_id
    )
    return updates


async def rollback_user_achievements(
        session: AsyncSession,
        user_id: int,
        updates: list[dict],
):
    logger.debug(
        "Откат связей %s user_achievement пользователя id=%d",
        updates, user_id,
    )
    to_delete = []
    to_upsert = []

    for upd in updates:
        if upd["progress"] == 0 and upd["is_completed"] is False:
            to_delete.append(upd["achievement_id"])
        else:
            to_upsert.append(upd)

    if to_delete:
        logger.debug("Удаление связей...")
        delete_stmt = (
            delete(UserAchievement)
            .where(
                UserAchievement.user_id == user_id,
                UserAchievement.achievement_id.in_(to_delete),
            )
        )
        await session.execute(delete_stmt)

    if to_upsert:
        logger.debug("Обновление связей...")
        upsert_stmt = upsert(UserAchievement).values(to_upsert)
        upsert_stmt = upsert_stmt.on_conflict_do_update(
            index_elements=["user_id", "achievement_id"],
            set_={
                "progress": upsert_stmt.excluded.progress,
                "is_completed": upsert_stmt.excluded.is_completed,
                "unlocked_at": upsert_stmt.excluded.unlocked_at,
                "updated_at": func.now(),
            },
        )
        await session.execute(upsert_stmt)
    logger.debug(
        "Удалено %d, обновлено %d связей user_achievement пользователя id=%d",
        len(to_delete), len(to_upsert), user_id,
    )
