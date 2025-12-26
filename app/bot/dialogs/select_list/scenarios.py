from aiogram_dialog import DialogManager
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.dialogs.enums import ListSelectionMode
from app.database.crud.task_list import fetch_user_lists_raw
from app.database.models import SystemListTypeEnum
from app.database.orchestration.task import change_list_for_task_with_log
from app.database.orchestration.task_list import change_parent_list_with_log
from app.database.services.task_list import build_ordered_hierarchy
from app.utils.serialization import from_dialog_safe


class SelectListScenario:
    def __init__(self, mode: ListSelectionMode):
        self.mode = mode

    async def get_lists(
            self,
            *,
            session: AsyncSession,
            dialog_manager: DialogManager,
    ) -> tuple[list[dict], dict]:
        ...

    async def apply(
            self,
            *,
            session: AsyncSession | None,
            dialog_manager: DialogManager,
            list_id: int,
    ) -> dict:
        ...


class CreateTaskScenario(SelectListScenario):
    async def get_lists(self, *, session, dialog_manager):
        user_id = dialog_manager.event.from_user.id

        rows = await fetch_user_lists_raw(session, user_id)

        def is_hidden(row):
            return row.system_type in {SystemListTypeEnum.INBOX, SystemListTypeEnum.ARCHIVE}

        return build_ordered_hierarchy(rows, is_hidden=is_hidden)

    async def apply(self, *, session, dialog_manager, list_id):
        lists = from_dialog_safe(dialog_manager.dialog_data["lists"])
        return {
            "selected_list_id": list_id,
            "selected_list_title": lists[list_id],
        }


class EditTaskScenario(SelectListScenario):
    async def get_lists(self, *, session, dialog_manager):
        user_id = dialog_manager.event.from_user.id
        old_list_id = dialog_manager.dialog_data["list_id"]

        rows = await fetch_user_lists_raw(session, user_id)

        def is_hidden(row):
            return (
                    row.system_type == SystemListTypeEnum.ARCHIVE
                    or row.list_id == old_list_id
            )

        return build_ordered_hierarchy(rows, is_hidden=is_hidden)

    async def apply(self, *, session, dialog_manager, list_id):
        await change_list_for_task_with_log(
            session,
            dialog_manager.event.from_user.id,
            dialog_manager.dialog_data["task_id"],
            dialog_manager.dialog_data["list_id"],
            list_id,
        )

        lists = from_dialog_safe(dialog_manager.dialog_data["lists"])
        return {
            "selected_list_id": list_id,
            "selected_list_title": lists[list_id],
        }


class CreateListScenario(SelectListScenario):
    async def get_lists(self, *, session, dialog_manager):
        user_id = dialog_manager.event.from_user.id

        rows = await fetch_user_lists_raw(session, user_id)

        def is_hidden(row):
            return row.system_type in {SystemListTypeEnum.INBOX, SystemListTypeEnum.ARCHIVE}

        return build_ordered_hierarchy(rows, is_hidden=is_hidden)

    async def apply(self, *, session, dialog_manager, list_id):
        lists = from_dialog_safe(dialog_manager.dialog_data["lists"])
        return {
            "selected_list_id": list_id,
            "selected_list_title": lists[list_id],
        }


class EditListScenario(SelectListScenario):
    async def get_lists(self, *, session, dialog_manager):
        user_id = dialog_manager.event.from_user.id
        current_list_id = dialog_manager.dialog_data["list_id"]
        old_parent_list_id = dialog_manager.dialog_data.get("parent_list_id")

        rows = await fetch_user_lists_raw(session, user_id)

        def is_hidden(row):
            return (
                    row.system_type in {SystemListTypeEnum.INBOX, SystemListTypeEnum.ARCHIVE}
                    or row.list_id in {current_list_id, old_parent_list_id}
            )

        return build_ordered_hierarchy(rows, is_hidden=is_hidden)

    async def apply(self, *, session, dialog_manager, list_id):
        user_id = dialog_manager.event.from_user.id
        current_list_id = dialog_manager.dialog_data["list_id"]
        new_parent_list_id = list_id
        old_parent_list_id = dialog_manager.dialog_data["parent_list_id"]

        await change_parent_list_with_log(
            session,
            user_id,
            current_list_id,
            old_parent_list_id,
            new_parent_list_id,
        )

        lists = from_dialog_safe(dialog_manager.dialog_data["lists"])
        return {
            "selected_list_id": list_id,
            "selected_list_title": lists[list_id],
        }


def get_select_list_scenario(mode: ListSelectionMode) -> SelectListScenario:
    return {
        ListSelectionMode.CREATE_TASK: CreateTaskScenario(mode),
        ListSelectionMode.EDIT_TASK: EditTaskScenario(mode),
        ListSelectionMode.CREATE_LIST: CreateListScenario(mode),
        ListSelectionMode.EDIT_LIST: EditListScenario(mode),
    }[mode]
