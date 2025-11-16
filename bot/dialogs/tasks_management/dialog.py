from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import ScrollingGroup, ListGroup, Button, \
    Cancel, Start
from aiogram_dialog.widgets.text import Const, Format

from bot.dialogs.states import TaskManagementDialogSG, GetTaskDialogSG
from bot.dialogs.tasks_management.getters import get_all_tasks
from bot.dialogs.tasks_management.handlers import go_selected_task

tasks_management_dialog = Dialog(
    Window(
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
            state=GetTaskDialogSG.add_task_window,
        ),
        Cancel(
            text=Const("🔙 Назад"),
            id="back",
        ),
        getter=get_all_tasks,
        state=TaskManagementDialogSG.main_tasks_window,
    ),
)