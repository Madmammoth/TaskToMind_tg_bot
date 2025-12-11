from aiogram import F
from aiogram_dialog import Dialog
from aiogram_dialog.widgets.kbd import (
    Button,
    Cancel,
    ListGroup,
    ScrollingGroup,
    Start,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const, Format

from app.bot.dialogs.common.handlers import combine_result_with_dialog_data
from app.bot.dialogs.components import WindowWithInput
from app.bot.dialogs.states import TasksManagementDialogSG, CreateTaskDialogSG
from app.bot.dialogs.tasks_management.getters import (
    get_all_tasks,
    get_tasks_in_trash,
    get_tasks_in_archive,
)
from app.bot.dialogs.tasks_management.handlers import go_selected_task

tasks_management_dialog = Dialog(
    WindowWithInput(
        Const("Показаны все задачи в порядке"),
        Const("от последних к более ранним", when="time_back"),
        ScrollingGroup(
            ListGroup(
                Button(
                    Format("{item[pos]}. {item[task_title]}"),
                    id="select_task",
                    on_click=go_selected_task,
                ),
                id="tasks_search",
                item_id_getter=lambda item: item["task_id"],
                items="task_buttons"
            ),
            id="scroll_tasks_search",
            width=1,
            height=10,
        ),
        Start(
            text=Const("➕ Новая задача"),
            id="create_task",
            state=CreateTaskDialogSG.input_task_window,
        ),
        SwitchTo(
            text=Const("Архив"),
            id="archive",
            state=TasksManagementDialogSG.archive_window
        ),
        SwitchTo(
            text=Const("🗑 Корзина"),
            id="trash",
            state=TasksManagementDialogSG.trash_window
        ),
        Cancel(
            text=Const("🔙 Назад"),
            id="back",
        ),
        getter=get_all_tasks,
        state=TasksManagementDialogSG.main_tasks_window,
    ),
    WindowWithInput(
        Const("Отменённые задачи:"),
        Const("<i>отменённых задач пока нет</i>", when=~F["task_buttons"]),
        ScrollingGroup(
            ListGroup(
                Button(
                    Format("{item[pos]}. {item[task_title]}"),
                    id="select_task",
                    on_click=go_selected_task,
                ),
                id="tasks_search",
                item_id_getter=lambda item: item["task_id"],
                items="task_buttons"
            ),
            id="scroll_tasks_search",
            width=1,
            height=10,
        ),
        SwitchTo(
            text=Const("🔙 Назад"),
            id="back",
            state=TasksManagementDialogSG.main_tasks_window,
        ),
        getter = get_tasks_in_trash,
        state = TasksManagementDialogSG.trash_window,
    ),
    WindowWithInput(
        Const("Выполненные задачи:"),
        Const("<i>выполненных задач пока нет</i>", when=~F["task_buttons"]),
        ScrollingGroup(
            ListGroup(
                Button(
                    Format("{item[pos]}. {item[task_title]}"),
                    id="select_task",
                    on_click=go_selected_task,
                ),
                id="tasks_search",
                item_id_getter=lambda item: item["task_id"],
                items="task_buttons"
            ),
            id="scroll_tasks_search",
            width=1,
            height=10,
        ),
        SwitchTo(
            text=Const("🔙 Назад"),
            id="back",
            state=TasksManagementDialogSG.main_tasks_window,
        ),
        getter = get_tasks_in_archive,
        state = TasksManagementDialogSG.archive_window,
    ),
    on_process_result=combine_result_with_dialog_data,
)