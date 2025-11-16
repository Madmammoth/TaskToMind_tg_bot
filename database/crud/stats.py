import logging

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert as upsert
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.stats import UserStats

logger = logging.getLogger(__name__)


async def upsert_user_stats_on_list_added(
        session: AsyncSession,
        user_id: int,
):
    logger.debug("Обновление статистки пользователя id=%d", user_id)
    stmt = upsert(UserStats).values(
        user_id=user_id,
        lists_created=1,
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=["user_id"],
        set_={
            "lists_created": (UserStats.lists_created
                              + stmt.excluded.lists_created),
            "updated_at": func.now(),
        },
    ).returning(UserStats)
    result = await session.execute(stmt)

    logger.debug("Обновлена статистика пользователя id=%d", user_id)
    return result.scalar_one()


async def update_stats_on_list_deleted(
        session: AsyncSession,
        user_id: int,
):
    logger.debug(
        "Обновление статистики пользователя id=%d при удалении списка",
        user_id
    )
    try:
        stmt_upsert_stats = upsert(UserStats).values(
            user_id=user_id,
            lists_deleted=1,
        )
        stmt_upsert_stats = stmt_upsert_stats.on_conflict_do_update(
            index_elements=["user_id"],
            set_={
                "lists_deleted": (UserStats.lists_deleted
                                  + stmt_upsert_stats.excluded.lists_deleted),
                "updated_at": func.now(),
            },
        )
        await session.execute(stmt_upsert_stats)
        await session.commit()
        logger.debug("Обновлена статистика пользователя id=%d", user_id)
    except Exception as e:
        await session.rollback()
        logger.exception(
            "Ошибка в update_stats_on_list_deleted "
            "для пользователя id=%d: %s",
            user_id, e,
        )
        raise
