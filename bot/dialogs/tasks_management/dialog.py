from aiogram_dialog import Dialog
from aiogram_dialog.widgets.kbd import (
    Button,
    Cancel,
    ListGroup,
    ScrollingGroup,
    Start,
)
from aiogram_dialog.widgets.text import Const, Format

from bot.dialogs.common.handlers import on_process_result
from bot.dialogs.components import WindowWithInput
from bot.dialogs.states import TasksManagementDialogSG, CreateTaskDialogSG
from bot.dialogs.tasks_management.getters import get_all_tasks
from bot.dialogs.tasks_management.handlers import go_selected_task

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
        Cancel(
            text=Const("🔙 Назад"),
            id="back",
        ),
        getter=get_all_tasks,
        state=TasksManagementDialogSG.main_tasks_window,
    ),
    on_process_result=on_process_result,
)