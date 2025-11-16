import logging

from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert as upsert
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Achievement, UserAchievement

logger = logging.getLogger(__name__)


async def get_achievements_by_categories(
        session: AsyncSession,
        categories: list,
):
    logger.debug("Получение категорий достижений %s", categories)
    result = await session.execute(
        select(Achievement).where(Achievement.category.in_(categories))
    )
    achievements = result.scalars().all()
    logger.debug(
        "Получено %d категорий достижений из %d",
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


async def upsert_user_achievements(
        session: AsyncSession,
        user_id: int,
        data: list[dict],
):
    logger.debug(
        "Вставка связей %s user_achievement пользователя id=%d",
        data, user_id,
    )
    stmt = upsert(UserAchievement).values(data)
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
