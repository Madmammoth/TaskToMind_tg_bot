import logging
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as upsert
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import LevelEnum, Achievement, UserAchievement
from database.models.stats import UserStats

logger = logging.getLogger(__name__)


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
