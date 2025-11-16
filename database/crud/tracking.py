import logging

from sqlalchemy.ext.asyncio import AsyncSession

from database.crud.common import filter_kwargs
from database.models import ActivityLog

logger = logging.getLogger(__name__)


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
        logger.debug("Successfully write activity log (%s)", action)
    except Exception as e:
        logger.exception("Failed to write activity log (%s): %s", action, e)
        await session.rollback()
