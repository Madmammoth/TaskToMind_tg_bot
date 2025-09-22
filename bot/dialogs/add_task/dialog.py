from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Row, Button, SwitchTo, Column, Next, Back
from aiogram_dialog.widgets.text import Format, Const

from bot.dialogs.states import GetTaskDialogSG
from bot.dialogs.add_task.getters import get_task
from bot.dialogs.add_task.handlers import go_pass, go_cancel_yes

add_task_dialog = Dialog(
    Window(
        Format("{task}"),
        Column(
            Button(
                text=Const("Сохранить"),
                id="save",
                on_click=go_pass
            ),
            Button(
                text=Const("Приоритет"),
                id="priority",
                on_click=go_pass
            ),
            Button(
                text=Const("Срок завершения"),
                id="deadline",
                on_click=go_pass
            ),
            Next(
                text=Const("Дополнительные настройки"),
                id="check_list",
            ),
            SwitchTo(
                text=Const("Отмена"),
                id="cancel",
                state=GetTaskDialogSG.cancel_window
            ),
        ),
        getter=get_task,
        state=GetTaskDialogSG.add_task_window
    ),
    Window(
        Format("{task}"),
        Column(
            Button(
                text=Const("Сохранить"),
                id="save",
                on_click=go_pass
            ),
            Button(
                text=Const("Продолжительность"),
                id="duration",
                on_click=go_pass
            ),
            Button(
                text=Const("Напомнить"),
                id="remind",
                on_click=go_pass
            ),
            Button(
                text=Const("В список"),
                id="to_list",
                on_click=go_pass
            ),
            Button(
                text=Const("Чек-лист"),
                id="check_list",
                on_click=go_pass
            ),
        Column(
            Button(
                text=Const("Отложить"),
                id="delay",
                on_click=go_pass
            ),
            Button(
                text=Const("Повтор"),
                id="delay",
                on_click=go_pass
            ),
            Button(
                text=Const("Изменить список"),
                id="change_list",
                on_click=go_pass
            ),
        ),
            ),
        Back(
            text=Const("Основные настройки"),
            id="back",
        ),
        SwitchTo(
            text=Const("Отмена"),
            id="cancel",
            state=GetTaskDialogSG.cancel_window
        ),
        getter=get_task,
        state=GetTaskDialogSG.add_task_window_2
    ),
    Window(
        Const("Вы уверены, что хотите отменить добавление задачи?"),
        Row(
            Button(
                text=Const("Да"),
                id="yes",
                on_click=go_cancel_yes,
            ),
            SwitchTo(
                text=Const("Нет"),
                id="no",
                state=GetTaskDialogSG.add_task_window
            ),
        ),
        state=GetTaskDialogSG.cancel_window
    ),
)
