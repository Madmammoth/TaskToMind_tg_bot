import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.crud.tracking import log_activity
from app.database.services.user import upsert_user

logger = logging.getLogger(__name__)


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
        logger.debug("Successfully upsert user: %d", user_id)
    except Exception as e:
        logger.exception("Failed to upsert user: %s", e)
        await log_activity(session, "new_user", False, user_id=user_id)
