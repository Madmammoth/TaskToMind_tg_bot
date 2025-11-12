from aiogram.enums import ContentType
from aiogram_dialog import Dialog, Window, ShowMode
from aiogram_dialog.widgets.input import MessageInput, TextInput
from aiogram_dialog.widgets.kbd import Row, Button, Start, SwitchTo
from aiogram_dialog.widgets.text import Const

from bot.dialogs.common.handlers import go_pass
from bot.dialogs.start.handlers import (
    go_settings,
    go_features,
    go_support,
    correct_text_task_input,
    wrong_text_task_input,
    empty_text_check,
    empty_text_input,
)
from bot.dialogs.states import StartSG, ForTestsDialogSG, TaskListsDialogSG

start_dialog = Dialog(
    Window(
        Const(
            "Выбери нужный пункт меню:",
        ),
        Row(
            SwitchTo(
                text=Const("Добавить задачу"),
                id="add_task",
                state=StartSG.input_task_window,
                show_mode=ShowMode.DELETE_AND_SEND
            ),
            Button(
                text=Const("Посмотреть задачи"),
                id="tasks",
                on_click=go_pass,
            ),
        ),
        Start(
            text=Const("Управление списками"),
            id="task_lists_management",
            state=TaskListsDialogSG.main_lists_window,
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
        SwitchTo(
            text=Const("Отмена"),
            id="cancel",
            state=StartSG.start_window,
        ),
        TextInput(
            id="text_task_input",
            type_factory=empty_text_check,
            on_success=correct_text_task_input,
            on_error=empty_text_input,
        ),
        MessageInput(
            func=wrong_text_task_input,
            content_types=ContentType.ANY,
        ),
        state=StartSG.input_task_window,
    ),
)
