from enum import StrEnum
from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.crud.task_list import fetch_user_lists_raw
from app.database.models import SystemListTypeEnum
from app.database.services.task_list import build_ordered_hierarchy


class ListSelectionMode(StrEnum):
    CREATE_TASK = "create_task"
    EDIT_TASK = "edit_task"
    CREATE_LIST = "create_list"
    EDIT_LIST = "edit_list"


class ListSelectionStrategy(Protocol):
    async def get_lists(
            self,
            session: AsyncSession,
            user_id: int,
    ) -> tuple[list[dict], dict]:
        ...


class CreateTaskListSelection:
    @staticmethod
    async def get_lists(session: AsyncSession, user_id: int):
        rows = await fetch_user_lists_raw(session, user_id)

        filtered = [
            row for row in rows
            if row.system_type != SystemListTypeEnum.ARCHIVE
        ]

        buttons, lists = build_ordered_hierarchy(filtered)

        return buttons, lists


class EditTaskListSelection:
    @staticmethod
    async def get_lists(session: AsyncSession, user_id: int):
        rows = await fetch_user_lists_raw(session, user_id)

        filtered = [
            row for row in rows
            if row.system_type not in {
                SystemListTypeEnum.INBOX,
                SystemListTypeEnum.ARCHIVE,
            }
        ]

        buttons, lists = build_ordered_hierarchy(filtered)

        return buttons, lists


class CreateListParentSelection:
    pass


class EditListParentSelection:
    pass


STRATEGIES: dict[ListSelectionMode, ListSelectionStrategy] = {
    ListSelectionMode.CREATE_TASK: CreateTaskListSelection(),
    ListSelectionMode.EDIT_TASK: EditTaskListSelection(),
    ListSelectionMode.CREATE_LIST: CreateListParentSelection(),
    ListSelectionMode.EDIT_LIST: EditListParentSelection(),
}
