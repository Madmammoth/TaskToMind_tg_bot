from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Row, Button, Start
from aiogram_dialog.widgets.text import Const

from bot.dialogs.add_task.handlers import go_pass
from bot.dialogs.start.handlers import (
    add_task, input_task, go_settings, go_features, go_support,
)
from bot.dialogs.states import StartSG, ForTestsDialogSG

start_dialog = Dialog(
    Window(
        Const(
            "Отправь мне планируемую задачу, чтобы не забыть о ней!",
        ),
        Row(
            Button(
                text=Const("Добавить задачу"),
                id="add_task",
                on_click=input_task,
            ),
            Button(
                text=Const("Посмотреть задачи"),
                id="tasks",
                on_click=go_pass,
            ),
        ),
        Row(
            Button(
                text=Const("Настройки"),
                id="settings",
                on_click=go_settings,
            ),
            Button(
                text=Const("Возможности бота"),
                id="features",
                on_click=go_features,
            ),
        ),
        Button(
            text=Const("Поддержка"),
            id="support",
            on_click=go_support,
        ),
        Start(
            text=Const("Тестирование"),
            id="testing",
            state=ForTestsDialogSG.test_window,
        ),
        state=StartSG.start_window,
    ),
    Window(
        Const("✍️ Введи текст задачи"),
        TextInput(
            id="task_input",
            on_success=add_task,
        ),
        state=StartSG.input_task_window,
    ),
)
