import logging

from sqlalchemy import column
from sqlalchemy.dialects.postgresql import insert as upsert
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User, TaskList, UserList

logger = logging.getLogger(__name__)


async def db_upsert_user(
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
        user_stmt = upsert(User).values(
            telegram_id=telegram_id,
            first_name=first_name,
            last_name=last_name,
            username=username,
        ).on_conflict_do_update(
            index_elements=["telegram_id"],
            set_=dict(
                first_name=first_name,
                last_name=last_name,
                username=username,
            ),
        ).returning(column("xmax"))
        result = await session.execute(user_stmt)
        xmax_value = result.scalar_one()
        is_new_user = xmax_value == "0"

        if is_new_user:
            default_lists = [
                TaskList(list_name="Входящие"),
                TaskList(list_name="Работа"),
                TaskList(list_name="Быт"),
            ]
            session.add_all(default_lists)
            await session.flush()
            associations = [
                UserList(
                    user_id=telegram_id,
                    list_id=default_list.list_id,
                    is_owner=True
                ) for default_list in default_lists
            ]
            session.add_all(associations)
            logger.info(f"Добавлен новый пользователь {telegram_id}")
        else:
            logger.debug(f"Обновлены данные пользователя {telegram_id}")
        await session.commit()

    except Exception as e:
        await session.rollback()
        logger.error("Ошибка в db_upsert_user для пользователя "
                     f"{telegram_id}: {e}")
        raise


async def add_task(
        session: AsyncSession,
        telegram_id: int,
        task: str,
):
    pass
