import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.crud.task_list import create_default_lists_for_user
from app.database.crud.user import (
    upsert_user_row,
    create_user_stats,
    assign_default_tags,
)
from app.database.models import User

logger = logging.getLogger(__name__)


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

        user = await upsert_user_row(
            session, telegram_id, first_name, last_name, username
        )

        if not old_user:
            await create_default_lists_for_user(session, telegram_id)
            create_user_stats(session, telegram_id)
            assign_default_tags(session, telegram_id)
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
        logger.exception(
            "Ошибка в upsert_user для пользователя id=%d: %s",
            telegram_id, e
        )
        raise
