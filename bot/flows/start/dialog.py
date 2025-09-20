from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Row, Button
from aiogram_dialog.widgets.text import Const

from bot.flows.add_task.handlers import go_tasks
from bot.flows.start.states import StartSG
from bot.flows.start.handlers import add_task, input_task, go_settings, go_features, go_support

start_dialog = Dialog(
    Window(
        Const("Отправь мне планируемую задачу, "
              "чтобы не забыть о ней! 🔘 ⚪ ⬜ 🔳 🔲"),
        Row(
            Button(text=Const("Добавить задачу"),
                   id="add_task",
                   on_click=input_task),
            Button(text=Const("Посмотреть задачи"),
                   id="tasks",
                   on_click=go_tasks),
        ),
        Row(
            Button(text=Const("Настройки"),
                   id="settings",
                   on_click=go_settings),
            Button(text=Const("Возможности бота"),
                   id="features",
                   on_click=go_features),
        ),
        Button(text=Const("Поддержка"),
               id="support",
               on_click=go_support),
        state=StartSG.start_window
    ),
    Window(
        Const("✍️ Введите текст задачи"),
        TextInput(
            id="task_input",
            on_success=add_task
        ),
        state=StartSG.input_task_window
    ),
)
