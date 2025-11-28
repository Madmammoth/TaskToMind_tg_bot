from aiogram_dialog import Dialog, ShowMode
from aiogram_dialog.widgets.kbd import Row, Start, Cancel, Button
from aiogram_dialog.widgets.text import Const

from app.bot.dialogs.common.handlers import get_start_data, on_process_result
from app.bot.dialogs.components import WindowWithInput, WindowWithoutInput
from app.bot.dialogs.start.handlers import (
    go_create_task,
    go_create_list,
    go_cancel,
    on_predict_dialog_process_result,
)
from app.bot.dialogs.states import (
    StartSG,
    HelpSG,
    PredictSG,
    # ForTestsDialogSG,
    ListsManagementDialogSG,
    TasksManagementDialogSG,
    CreateTaskDialogSG,
)

start_dialog = Dialog(
    WindowWithInput(
        Const(
            "Выбери нужный пункт меню:",
        ),
        Row(
            Start(
                text=Const("Добавить задачу"),
                id="create_task",
                state=CreateTaskDialogSG.input_task_window,
                show_mode=ShowMode.DELETE_AND_SEND
            ),
            Start(
                text=Const("Посмотреть задачи"),
                id="tasks",
                state=TasksManagementDialogSG.main_tasks_window,
            ),
        ),
        Start(
            text=Const("Управление списками"),
            id="task_lists_management",
            state=ListsManagementDialogSG.main_lists_window,
        ),
        # Row(
        #     Button(
        #         text=Const("Настройки"),
        #         id="settings",
        #         on_click=go_settings,
        #     ),
        #     Button(
        #         text=Const("Возможности бота"),
        #         id="features",
        #         on_click=go_features,
        #     ),
        # ),
        # Button(
        #     text=Const("Поддержка"),
        #     id="support",
        #     on_click=go_support,
        # ),
        # Start(
        #     text=Const("Тестирование"),
        #     id="testing",
        #     state=ForTestsDialogSG.test_window,
        # ),
        state=StartSG.start_window,
    ),
    on_process_result=on_process_result,
)

help_dialog = Dialog(
    WindowWithoutInput(
        Const(
            "Я — бот, который со временем "
            "станет твоим удобным и надёжным планировщиком дел, "
            "умным каталогизатором всех твоих пересланных сообщений, "
            "твоей второй памятью и даже — твоим вторым мозгом!\n\n"
            "Но пока я могу следующее:\n1. Сохранить твою задачу.\n\n"
            "Нажми кнопку «↩️ Назад», чтобы вернуться в предыдущее меню "
            "или нажми /start, чтобы перезапустить меня."
        ),
        Cancel(Const("↩️ Назад")),
        state=HelpSG.help_window,
    ),
)

predict_dialog = Dialog(
    WindowWithoutInput(
        Const("Это новая задача или новый список?"),
        Button(
            text=Const("Новая задача"),
            id="new_task",
            on_click=go_create_task,
        ),
        Button(
            text=Const("Новый список"),
            id="new_list",
            on_click=go_create_list,
        ),
        Button(
            text=Const("↩️ Отмена"),
            id="cancel",
            on_click=go_cancel,
        ),
        state=PredictSG.predict_window,
    ),
    on_start=get_start_data,
    on_process_result=on_predict_dialog_process_result,
)
