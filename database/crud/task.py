import logging
from datetime import datetime, timezone

from sqlalchemy import select, update, and_, exists, func
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import (
    TaskAccess,
    AccessRoleEnum,
    Task,
    TaskStatusEnum,
    TaskList,
    ListAccess,
    TaskInList,
    LevelEnum,
    User
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


def make_list_query_by_list_id(
        user_id: int,
        list_id: int,
):
    logger.debug(
        "Составление для пользователя id=%d запроса списка id=%d",
        user_id, list_id,
    )
    list_query = (
        select(TaskList)
        .join(ListAccess)
        .where(
            TaskList.list_id == list_id,
            ListAccess.user_id == user_id,
            ListAccess.role.in_([
                AccessRoleEnum.OWNER,
                AccessRoleEnum.EDITOR,
            ]),
        )
    )
    return list_query


def make_list_query_by_list_title(
        user_id: int,
        list_title: str,
):
    logger.debug(
        "Составление для пользователя id=%d запроса списка «%s»",
        user_id, list_title,
    )
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
    return list_query


async def create_task(
        session: AsyncSession,
        task_data: dict,
) -> Task:
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

    return task


def create_list_task_link(
        session: AsyncSession,
        list_id: int,
        task_id: int,
):
    session.add(
        TaskInList(
            list_id=list_id,
            task_id=task_id,
        )
    )


def create_task_access(
        session: AsyncSession,
        user_id: int,
        task_id: int,
):
    session.add(
        TaskAccess(
            task_id=task_id,
            user_id=user_id,
            role=AccessRoleEnum.OWNER,
            granted_by=user_id,
        )
    )


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
        mode: str,
):
    """
    Запрос задач в списке задач
    :param session: сессия СУБД
    :param user_id: ID пользователя
    :param list_id: ID списка задач
    :param mode: режим сортировки задач
    :return: список задач
    """
    logger.debug(
        "Запрос задач в списке id=%d пользователя id=%d",
        list_id, user_id,
    )

    rule = Task.updated_at
    if mode == "default":
        rule = Task.updated_at.desc()

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
        .order_by(rule)
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


async def get_task_for_user(
        session: AsyncSession,
        user_id: int,
        task_id: int,
) -> Task:
    logger.debug(
        "Запрос задачи id=%d для пользователя id=%d", task_id, user_id
    )
    stmt = (
        select(Task)
        .join(TaskAccess, TaskAccess.task_id == Task.task_id)
        .where(TaskAccess.user_id == user_id, Task.task_id == task_id)
    )
    result = await session.execute(stmt)
    task = result.scalar_one_or_none()
    return task


async def get_list_for_task(
        session: AsyncSession,
        task_id: int,
) -> TaskList:
    stmt = (
        select(TaskList)
        .join(TaskInList, TaskInList.list_id == TaskList.list_id)
        .where(TaskInList.task_id == task_id)
    )
    result = await session.execute(stmt)
    task_list = result.scalar_one_or_none()
    return task_list


async def get_task_access(
        session: AsyncSession,
        user_id: int,
        task_id: int,
) -> TaskAccess:
    stmt = (
        select(TaskAccess)
        .where(
            TaskAccess.task_id == task_id,
            TaskAccess.user_id == user_id,
        )
    )
    result = await session.execute(stmt)
    task_access = result.scalar_one_or_none()
    return task_access


async def complete_task(
        session: AsyncSession,
        task_id: int,
):
    logger.debug("Установка статуса «Выполнена» у задачи id=%d", task_id)
    stmt = update(Task).where(Task.task_id == task_id).values(
        status=TaskStatusEnum.DONE,
        completed_at=func.now(),
        updated_at=func.now(),
    )
    await session.execute(stmt)
    logger.debug("Задача id=%d выполнена", task_id)


async def get_task_users(
        session: AsyncSession,
        task_id: int,
):
    logger.debug("Получение пользователей, связанных с задачей id=%d", task_id)
    stmt = (
        select(User)
        .join(TaskAccess, TaskAccess.user_id == User.telegram_id)
        .where(
            TaskAccess.task_id == task_id,
            TaskAccess.role.in_([
                AccessRoleEnum.OWNER,
                AccessRoleEnum.EDITOR,
            ])
        ))

    result = await session.scalars(stmt)
    users = result.all()

    if not users:
        logger.debug("Связанные с задачей id=%d пользователей не найдены")
        return []

    logger.debug(
        "Получено пользователей: %d, задачи id=%d",
        len(users), task_id,
    )
    return users


def get_stats_and_achievs_categories(
        task_data: dict,
        action: str
) -> list[str]:
    logger.debug(
        "Определение категорий статистики и достижений по параметрам задачи"
    )

    priority_level_enum = task_data.get("priority")
    if not priority_level_enum:
        logger.debug("В task_data нет данных о приоритете задачи")
        priority_level_enum = LevelEnum.LOW
    priority = priority_level_enum.value.lower()
    urgency_level_enum = task_data.get("urgency")
    if not urgency_level_enum:
        logger.debug("В task_data нет данных о срочности задачи")
        urgency_level_enum = LevelEnum.LOW
    urgency = urgency_level_enum.value.lower()

    categories = []
    if action == "create":
        categories.append("tasks_created")
        priority_category = f"{priority}_priority_tasks_created"
        urgency_category = f"{urgency}_urgency_tasks_created"
        categories.extend([priority_category, urgency_category])
        if task_data.get("parent_task_id"):
            categories.append("checked_tasks_created")
    elif action == "complete":
        categories.append("tasks_completed")
        priority_category = f"{priority}_priority_tasks_completed"
        urgency_category = f"{urgency}_urgency_tasks_completed"
        categories.extend([priority_category, urgency_category])
        if task_data.get("parent_task_id"):
            categories.append("checked_tasks_completed")
        if task_data.get("is_shared"):
            categories.append("shared_tasks_completed")
        if deadline := task_data.get("deadline"):
            if datetime.now(timezone.utc) < deadline:
                categories.append("tasks_completed_before_deadline")
            else:
                categories.append("tasks_completed_after_deadline")
    elif action == "cancel":
        categories.append("tasks_canceled")
        if task_data.get("parent_task_id"):
            categories.append("checked_tasks_canceled")
        if task_data.get("is_shared"):
            categories.append("shared_tasks_canceled")
    elif action == "postpone":
        if task_data.get("postponed_count"):
            categories.append("postpones_per_task")
        else:
            categories.append("tasks_postponed")
            if task_data.get("is_shared"):
                categories.append("shared_tasks_postponed")
    elif action == "share":
        categories.append("tasks_shared")
    else:
        logger.debug("Неожиданный action=%s", action)
    logger.debug("Получен список категорий %s", categories)
    return categories


async def not_complete_task(
        session: AsyncSession,
        task_id: int,
):
    logger.debug("Установка статуса «В работе» у задачи id=%d", task_id)
    stmt = update(Task).where(Task.task_id == task_id).values(
        status=TaskStatusEnum.IN_PROGRESS,
        completed_at=None,
        updated_at=func.now(),
    )
    await session.execute(stmt)
    logger.debug("Задача id=%d в работе", task_id)


async def cancel_task(
        session: AsyncSession,
        task_id: int,
):
    logger.debug("Установка статуса «Отменена» у задачи id=%d", task_id)
    stmt = update(Task).where(Task.task_id == task_id).values(
        status=TaskStatusEnum.CANCELED,
        canceled_at=func.now(),
        updated_at=func.now(),
    )
    await session.execute(stmt)
    logger.debug("Задача id=%d отменена", task_id)


async def not_cancel_task(
        session: AsyncSession,
        task_id: int,
):
    logger.debug("Установка статуса «В работе» у задачи id=%d", task_id)
    stmt = update(Task).where(Task.task_id == task_id).values(
        status=TaskStatusEnum.IN_PROGRESS,
        canceled_at=None,
        updated_at=func.now(),
    )
    await session.execute(stmt)
    logger.debug("Задача id=%d в работе", task_id)
