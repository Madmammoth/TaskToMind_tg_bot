import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.crud.common import filter_kwargs
from app.database.models import ActivityLog

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
    logger.debug("Запись лога action=%s", action)
    data = filter_kwargs(ActivityLog, kwargs)
    log_entry = ActivityLog(
        action=action,
        success=success,
        **data,
    )
    session.add(log_entry)
    logger.debug("Successfully write activity log (%s)", action)
