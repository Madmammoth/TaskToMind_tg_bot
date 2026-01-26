import logging

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Button
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.dialogs.enums import ListSelectionMode
from app.bot.dialogs.states import TaskActionsDialogSG, SelectListDialogSG
from app.database.orchestration.task import (
    complete_task_with_stats_achievs_log,
    not_complete_task_with_stats_achievs_log,
    cancel_task_with_stats_achievs_log,
    not_cancel_task_with_stats_achievs_log,
)
from app.utils.serialization import from_dialog_safe

logger = logging.getLogger(__name__)


async def go_complete_yes(
        callback: CallbackQuery,
        _widget: Button,
        dialog_manager: DialogManager,
):
    logger.debug("Изменение статуса на «Выполнена» задачи...")
    user_id = callback.from_user.id
    task_id = dialog_manager.dialog_data.get("task_id")
    logger.debug("...id=%d пользователем id=%d", task_id, user_id)
    session: AsyncSession = dialog_manager.middleware_data["session"]
    task_data = from_dialog_safe(dialog_manager.dialog_data)
    task_title = task_data.get("task_title")

    await complete_task_with_stats_achievs_log(
        session=session,
        user_id=user_id,
        task_data=task_data,
    )

    await callback.message.answer(
        f"Задача\n\n{task_title}\n\nуспешно выполнена!"
    )

    logger.debug(
        "Статус «Выполнена» присвоен задаче id=%d пользователем id=%d",
        task_id, user_id
    )
    await dialog_manager.switch_to(
        state=TaskActionsDialogSG.main_task_window,
        show_mode=ShowMode.DELETE_AND_SEND,
    )


async def go_not_complete_yes(
        callback: CallbackQuery,
        _widget: Button,
        dialog_manager: DialogManager,
):
    logger.debug("Изменение статуса на «В работе» задачи...")
    user_id = callback.from_user.id
    task_id = dialog_manager.dialog_data.get("task_id")
    logger.debug("...id=%d пользователем id=%d", task_id, user_id)
    session: AsyncSession = dialog_manager.middleware_data["session"]
    task_data = from_dialog_safe(dialog_manager.dialog_data)
    task_title = task_data.get("task_title")

    await not_complete_task_with_stats_achievs_log(
        session=session,
        user_id=user_id,
        task_data=task_data,
    )

    await callback.message.answer(
        f"Задача\n\n{task_title}\n\nуспешно возвращена в работу!"
    )

    logger.debug(
        "Статус «В работе» присвоен задаче id=%d пользователем id=%d",
        task_id, user_id
    )
    await dialog_manager.switch_to(
        state=TaskActionsDialogSG.main_task_window,
        show_mode=ShowMode.DELETE_AND_SEND,
    )


async def go_cancel_yes(
        callback: CallbackQuery,
        _widget: Button,
        dialog_manager: DialogManager,
):
    logger.debug("Изменение статуса на «Отменена» задачи...")
    user_id = callback.from_user.id
    task_id = dialog_manager.dialog_data.get("task_id")
    logger.debug("...id=%d пользователем id=%d", task_id, user_id)
    session: AsyncSession = dialog_manager.middleware_data["session"]
    task_data = from_dialog_safe(dialog_manager.dialog_data)
    task_title = task_data.get("task_title")

    await cancel_task_with_stats_achievs_log(
        session=session,
        user_id=user_id,
        task_data=task_data,
    )

    await callback.message.answer(
        f"Задача\n\n{task_title}\n\nуспешно отменена!"
    )

    logger.debug(
        "Статус «Отменена» присвоен задаче id=%d пользователем id=%d",
        task_id, user_id
    )
    await dialog_manager.switch_to(
        state=TaskActionsDialogSG.main_task_window,
        show_mode=ShowMode.DELETE_AND_SEND,
    )


async def go_not_cancel_yes(
        callback: CallbackQuery,
        _widget: Button,
        dialog_manager: DialogManager,
):
    logger.debug("Изменение статуса с «Отменена» на «В работе» задачи...")
    user_id = callback.from_user.id
    task_id = dialog_manager.dialog_data.get("task_id")
    logger.debug("...id=%d пользователем id=%d", task_id, user_id)
    session: AsyncSession = dialog_manager.middleware_data["session"]
    task_data = from_dialog_safe(dialog_manager.dialog_data)
    task_title = task_data.get("task_title")

    await not_cancel_task_with_stats_achievs_log(
        session=session,
        user_id=user_id,
        task_data=task_data,
    )

    await callback.message.answer(
        f"Задача\n\n{task_title}\n\nуспешно возвращена в работу!"
    )

    logger.debug(
        "Статус «В работе» присвоен задаче id=%d пользователем id=%d",
        task_id, user_id
    )
    await dialog_manager.switch_to(
        state=TaskActionsDialogSG.main_task_window,
        show_mode=ShowMode.DELETE_AND_SEND,
    )


async def go_to_list_selection(
        callback: CallbackQuery,
        _widget: Button,
        dialog_manager: DialogManager,
):
    user_id = callback.from_user.id
    logger.debug("Переход пользователя id=%d к выбору списка при редактировании задачи", user_id)
    data = {
        "mode": ListSelectionMode.EDIT_TASK.value,
        "task_id": dialog_manager.dialog_data["task_id"],
        "list_id": dialog_manager.dialog_data["selected_list_id"],
    }
    logger.debug(
        "Запуск пользователем id=%d диалога выбора списка с data=%r",
        user_id, data,
    )
    await dialog_manager.start(
        state=SelectListDialogSG.select_list_window,
        data=data,
    )


async def postpone(
        _callback: CallbackQuery,
        _widget: Button,
        _dialog_manager: DialogManager,
):
    pass
