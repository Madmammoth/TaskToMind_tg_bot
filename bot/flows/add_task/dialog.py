from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Row, Button
from aiogram_dialog.widgets.text import Format, Const

from bot.flows.add_task.states import GetTaskDialogSG
from bot.flows.add_task.getters import get_task
from bot.flows.add_task.handlers import go_tasks, go_back_to_add_task, go_cancel_yes, go_inbox, go_cancel

add_task_dialog = Dialog(
    Window(
        Format("{task}"),
        Row(
            Button(text=Const("Списки"),
                   id="lists",
                   on_click=go_tasks),
            Button(text=Const("Входящие"),
                   id="inbox",
                   on_click=go_inbox),
            Button(text=Const("Отмена"),
                   id="cancel",
                   on_click=go_cancel),
        ),
        getter=get_task,
        state=GetTaskDialogSG.add_task_window
    ),
    Window(
        Const("Вы уверены, что хотите отменить добавление задачи?"),
        Row(
            Button(text=Const("Да"),
                   id="yes",
                   on_click=go_cancel_yes),
            Button(text=Const("Нет"),
                   id="no",
                   on_click=go_back_to_add_task),
        ),
        state=GetTaskDialogSG.cancel_window
    ),
)
