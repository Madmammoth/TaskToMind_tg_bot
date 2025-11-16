import logging

from sqlalchemy import select, update, and_, exists
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import (
    TaskAccess,
    AccessRoleEnum,
    Task,
    TaskStatusEnum,
    TaskList,
    ListAccess,
    TaskInList
)

logger = logging.getLogger(__name__)


async def mark_task_in_process(
        session: AsyncSession,
        task_id: int,
        user_id: int
):
    """
    Смена статуса задачи при взаимодействии пользователя с задачей
    :param session: сессия СУБД
    :param task_id: ID задачи
    :param user_id: ID пользователя
    :return: None
    """
    access_exists = (
        select(TaskAccess).where(
            TaskAccess.task_id == task_id,
            TaskAccess.user_id == user_id,
            TaskAccess.role.in_([
                AccessRoleEnum.OWNER,
                AccessRoleEnum.EDITOR,
            ]),
        ).exists()
    )
    stmt = (
        update(Task)
        .where(
            Task.task_id == task_id,
            Task.status == TaskStatusEnum.NEW,
            access_exists,
        )
        .values(status=TaskStatusEnum.IN_PROGRESS)
    )
    await session.execute(stmt)
    await session.commit()


async def db_add_task(
        session: AsyncSession,
        user_id: int,
        task_data: dict,
):
    """
    Добавление задачи пользователем
    :param session: сессия СУБД
    :param user_id: ID пользователя
    :param task_data: настройки задачи
    """
    try:
        if "list_id" in task_data:
            list_query = (
                select(TaskList)
                .join(ListAccess)
                .where(
                    TaskList.list_id == int(task_data["list_id"]),
                    ListAccess.user_id == user_id,
                    ListAccess.role.in_([
                        AccessRoleEnum.OWNER,
                        AccessRoleEnum.EDITOR,
                    ]),
                )
            )
        else:
            list_title = task_data.get("list_title", "Входящие")
            list_query = (
                select(TaskList)
                .join(ListAccess)
                .where(
                    TaskList.title == list_title,
                    ListAccess.user_id == user_id,
                    ListAccess.role.in_([
                        AccessRoleEnum.OWNER,
                        AccessRoleEnum.EDITOR,
                    ]),
                )
            )
        task_list = (await session.execute(list_query)).scalar_one_or_none()
        if not task_list:
            raise ValueError("Список не найден или недоступен пользователю")

        task = Task(
            title=task_data["task_title"],
            description=task_data["task_description"],
            message_id=task_data.get("message_id"),
            priority=task_data.get("priority"),
            urgency=task_data.get("urgency"),
            status=TaskStatusEnum.NEW,
            parent_task_id=task_data.get("parent_task_id"),
            deadline=task_data.get("deadline"),
            is_recurring=task_data.get("is_recurring", False),
            recurrence_rule_id=task_data.get("recurrence_rule_id"),
            duration=task_data.get("duration"),
            remind=task_data.get("remind", False),
        )
        session.add(task)
        await session.flush()

        session.add(
            TaskInList(
                list_id=task_list.list_id,
                task_id=task.task_id,
            )
        )

        session.add(
            TaskAccess(
                task_id=task.task_id,
                user_id=user_id,
                role=AccessRoleEnum.OWNER,
                granted_by=user_id,
            )
        )
        logger.debug(
            "Задача id=%d пользователя id=%d добавлена",
            task.task_id, user_id,
        )
        await session.commit()
    except Exception as e:
        await session.rollback()
        logger.exception("Ошибка в db_add_task для пользователя "
                         f"{user_id}: {e}")
        raise
    return task_list.list_id, task.task_id


async def get_user_tasks(
        session: AsyncSession,
        user_id: int,
        mode: str,
):
    """
    Запрос всех задач пользователя
    :param session: сессия СУБД
    :param user_id: ID пользователя
    :param mode: режим сортировки задач
    :return: список задач
    """
    logger.debug("Запрос задач пользователя id=%d", user_id)

    rule = Task.updated_at
    if mode == "default":
        rule = Task.updated_at.desc()

    stmt = (
        select(Task)
        .where(
            and_(
                TaskAccess.task_id == Task.task_id,
                TaskAccess.user_id == user_id,
                Task.parent_task_id.is_(None),
            )
        ).order_by(rule)
    )

    result = await session.scalars(stmt)
    tasks = result.all()

    if not tasks:
        return []

    logger.debug(
        "Получено задач: %d, пользователя id=%d",
        len(tasks), user_id,
    )
    return tasks


async def get_user_tasks_in_list(
        session: AsyncSession,
        user_id: int,
        list_id: int,
):
    """
    Запрос задач в списке задач
    :param session: сессия СУБД
    :param user_id: ID пользователя
    :param list_id: ID списка задач
    :return: список задач
    """
    logger.debug(
        "Запрос задач в списке id=%d пользователя id=%d",
        list_id, user_id,
    )
    stmt = (
        select(Task)
        .join(TaskInList)
        .where(
            TaskInList.list_id == list_id,
            exists().where(
                and_(
                    TaskAccess.task_id == Task.task_id,
                    TaskAccess.user_id == user_id,
                )
            )
        )
    )

    result = await session.scalars(stmt)
    tasks = result.all()

    if not tasks:
        return []

    logger.debug(
        "Получено задач: %d, списка id=%d, пользователя id=%d",
        len(tasks), list_id, user_id,
    )
    return tasks
