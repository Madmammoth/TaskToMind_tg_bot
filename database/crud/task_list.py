import logging
from typing import Sequence

from sqlalchemy import select, Row, func, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import TaskList, ListAccess, AccessRoleEnum
from database.models.enums import SystemListTypeEnum

logger = logging.getLogger(__name__)


async def create_default_lists_for_user(
        session: AsyncSession,
        telegram_id: int
):
    titles = [
        ("Корзина", SystemListTypeEnum.TRASH),
        ("Входящие", SystemListTypeEnum.INBOX),
        ("Архив", SystemListTypeEnum.ARCHIVE),
        ("Работа", SystemListTypeEnum.NONE),
        ("Быт", SystemListTypeEnum.NONE),
    ]
    default_lists = [TaskList(title=title, system_type=system_type)
                     for title, system_type in titles]
    session.add_all(default_lists)
    await session.flush()

    session.add_all([
        ListAccess(
            user_id=telegram_id,
            list_id=lst.list_id,
            role=AccessRoleEnum.OWNER,
            granted_by=telegram_id,
            position=pos
        ) for pos, lst in enumerate(default_lists, start=0)
    ])


async def fetch_user_lists_raw(
        session: AsyncSession,
        user_id: int,
        mode: str = "default",
) -> Sequence[Row]:
    """
    Возвращает списки пользователя в зависимости от режима отображения
    :param session: сессия СУБД
    :param user_id: ID пользователя
    :param mode: режим отображения списков
    :return: список {list_id, list_title, pos}
    """
    logger.debug("Запрос списков пользователя id=%d", user_id)

    stmt = (
        select(
            TaskList.list_id,
            TaskList.title,
            TaskList.parent_list_id,
            TaskList.system_type,
            ListAccess.position,

        )
        .join(ListAccess, ListAccess.list_id == TaskList.list_id)
        .where(ListAccess.user_id == user_id)
        .where(ListAccess.position != 0)
    )

    if mode == "add_in_list":
        logger.debug("show_lists_mode=add_in_list")
        stmt = stmt.where(
            TaskList.system_type.not_in(
                [SystemListTypeEnum.INBOX, SystemListTypeEnum.ARCHIVE]
            )
        )
    elif mode == "add_task":
        logger.debug("show_lists_mode=add_task")
        stmt = stmt.where(TaskList.system_type != SystemListTypeEnum.ARCHIVE)

    rows = (await session.execute(stmt)).all()
    return rows


async def create_list_access(
        session: AsyncSession,
        list_id: int,
        user_id: int,
        parent_id: int | None,
        position: int
):
    list_access = ListAccess(
            list_id=list_id,
            user_id=user_id,
            role=AccessRoleEnum.OWNER,
            granted_by=user_id,
            position=position,
            parent_list_id=parent_id,
        )
    session.add(list_access)
    return list_access


async def get_max_position(
        session: AsyncSession,
        user_id: int,
        parent_id: int | None
) -> int:
    parent_condition = (
        TaskList.parent_list_id.is_(None)
        if parent_id is None
        else TaskList.parent_list_id == parent_id
    )

    stmt = (
        select(func.coalesce(func.max(ListAccess.position), 0))
        .join(TaskList, ListAccess.list_id == TaskList.list_id)
        .where(
            and_(
                ListAccess.user_id == user_id,
                parent_condition,
            )
        )
    )
    result = await session.execute(stmt)
    return result.scalar() or 0


async def create_list(
        session: AsyncSession,
        title: str,
        parent_id: int | None
) -> TaskList:

    task_list = TaskList(
        title=title,
        parent_list_id=parent_id,
    )
    session.add(task_list)
    await session.flush()

    return task_list


async def get_user_sub_lists_in_list(
        session: AsyncSession,
        user_id: int,
        list_id: int,
):
    """
    Запрос подсписков в списке задач
    :param session: сессия СУБД
    :param user_id: ID пользователя
    :param list_id: ID списка задач
    :return: список подсписков
    """
    logger.debug(
        "Запрос подсписков в списке id=%d пользователя id=%d",
        list_id, user_id,
    )

    stmt = (
        select(TaskList)
        .join(ListAccess, ListAccess.list_id == TaskList.list_id)
        .where(
            ListAccess.user_id == user_id,
            TaskList.parent_list_id == list_id,
        )
        .order_by(ListAccess.position)
    )

    result = await session.scalars(stmt)
    sub_lists = result.all()

    if not sub_lists:
        return []

    logger.debug(
        "Получено подсписков: %d, списка id=%d, пользователя id=%d",
        len(sub_lists), list_id, user_id,
    )
    return sub_lists


async def db_delete_list(
        session: AsyncSession,
        user_id: int,
        list_id: int,
):
    logger.debug(
        "Удаление списка id=%d пользователя id=%d",
        list_id, user_id,
    )

    try:
        stmt = delete(TaskList).where(TaskList.list_id == list_id)
        await session.execute(stmt)
        await session.commit()
        logger.debug(
            "Список задач id=%d удалён у пользователя id=%d",
            list_id, user_id,
        )
    except Exception as e:
        await session.rollback()
        logger.exception(
            "Ошибка в db_delete_list для пользователя id=%d: %s",
            user_id, e,
        )
        raise
