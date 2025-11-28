import logging

from sqlalchemy import func, update
from sqlalchemy.dialects.postgresql import insert as upsert
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.stats import UserStats

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


def make_updates_on_conflict(model, stmt, updates: dict):
    return {
        key: getattr(model, key) + stmt.excluded[key]
        for key in updates.keys()
    }


async def upsert_user_stats_on_task_completed(
        session: AsyncSession,
        user_id: int,
        updates: dict,
):
    logger.debug(
        "Обновление при выполнении задачи "
        "статистики (updates=%s) пользователя id=%d",
        list(updates.keys()), user_id,
    )
    stmt = upsert(UserStats).values({"user_id": user_id, **updates})
    updates_on_conflict = make_updates_on_conflict(UserStats, stmt, updates)
    stmt = stmt.on_conflict_do_update(
        index_elements=["user_id"],
        set_={
            **updates_on_conflict,
            "updated_at": func.now(),
        }
    ).returning(UserStats)
    result = await session.execute(stmt)
    logger.debug("Обновлена статистика пользователя id=%d", user_id)
    return result.scalar_one()


async def get_user_stats(
        session: AsyncSession,
        user_id: int,
):
    logger.debug("Получение статистики пользователя id=%d", user_id)
    user_stats = await session.get(UserStats, user_id)
    return user_stats


def make_rollback_updates(model, categories):
    return {
        category: getattr(model, category) - 1
        for category in categories
    }


async def update_user_stats_on_task_uncompleted(
        session: AsyncSession,
        user_id: int,
        categories: list,
):
    logger.debug(
        "Обновление при возвращении задачи в работу "
        "статистики (categories=%s) пользователя id=%d",
        categories, user_id,
    )
    back_updates = make_rollback_updates(UserStats, categories)
    stmt = (
        update(UserStats)
        .where(UserStats.user_id == user_id)
        .values({
            **back_updates,
            "updated_at": func.now(),
        }).returning(UserStats))
    result = await session.execute(stmt)
    logger.debug("Обновлена статистика пользователя id=%d", user_id)
    return result.scalar_one()


async def upsert_user_stats_on_task_canceled(
        session: AsyncSession,
        user_id: int,
        updates: dict,
):
    logger.debug(
        "Обновление при отмене задачи "
        "статистики (updates=%s) пользователя id=%d",
        updates, user_id,
    )
    stmt = upsert(UserStats).values({"user_id": user_id, **updates})
    updates_on_conflict = make_updates_on_conflict(UserStats, stmt, updates)
    stmt = stmt.on_conflict_do_update(
        index_elements=["user_id"],
        set_={
            **updates_on_conflict,
            "updated_at": func.now(),
        }
    ).returning(UserStats)
    result = await session.execute(stmt)
    logger.debug("Обновлена статистика пользователя id=%d", user_id)
    return result.scalar_one()


async def update_user_stats_on_task_uncanceled(
        session: AsyncSession,
        user_id: int,
        categories: list,
):
    logger.debug(
        "Обновление при смене статуса задачи с «Отменена» на «В работе» "
        "статистики (categories=%s) пользователя id=%d",
        categories, user_id,
    )
    back_updates = make_rollback_updates(UserStats, categories)
    stmt = (
        update(UserStats)
        .where(UserStats.user_id == user_id)
        .values({
            **back_updates,
            "updated_at": func.now(),
        }).returning(UserStats))
    result = await session.execute(stmt)
    logger.debug("Обновлена статистика пользователя id=%d", user_id)
    return result.scalar_one()
