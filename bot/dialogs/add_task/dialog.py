from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Row, Button, SwitchTo, Column, Next, Back
from aiogram_dialog.widgets.text import Format, Const

from bot.dialogs.states import GetTaskDialogSG
from bot.dialogs.add_task.getters import get_task
from bot.dialogs.add_task.handlers import go_pass, go_cancel_yes, go_save_yes

add_task_dialog = Dialog(
    Window(
        Format("{task}"),
        Format("\nСписок: {in_list}"),
        Format("Приоритет: {priority}"),
        Format("Срочность: {urgency}"),
        Column(
            SwitchTo(
                text=Const("Сохранить"),
                id="save",
                state=GetTaskDialogSG.save_window
            ),
            Button(
                text=Const("Список"),
                id="in_list",
                on_click=go_pass
            ),
            Button(
                text=Const("Приоритет"),
                id="priority",
                on_click=go_pass
            ),
            Button(
                text=Const("Срочность"),
                id="urgency",
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
        Format("\nСписок: {in_list}"),
        Format("Приоритет: {priority}"),
        Format("Срочность: {urgency}"),
        Column(
            SwitchTo(
                text=Const("Сохранить"),
                id="save",
                state=GetTaskDialogSG.save_window
            ),
            Button(
                text=Const("Срок завершения"),
                id="deadline",
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
        Const("Задача:\n"),
        Format("{task}\n"),
        Const("будет сохранена со следующими параметрами:"),
        Format("\nСписок: {in_list}"),
        Format("Приоритет: {priority}"),
        Format("Срочность: {urgency}"),
        Format("Срок завершения: {deadline}", when="deadline_show"),
        Format("Продолжительность: {duration}", when="duration_show"),
        Format("Напомнить: {remind}", when="remind_show"),
        Format("Повтор: {repeat}", when="repeat_show"),
        Format("Чек-лист: {checklist}", when="checklist_show"),
        Format("\nТег: {tag}", when="tag_show"),
        Const("\nВсё верно?"),
        Row(
            Button(
                text=Const("Да"),
                id="yes",
                on_click=go_save_yes,
            ),
            SwitchTo(
                text=Const("Нет"),
                id="no",
                state=GetTaskDialogSG.add_task_window
            ),
        ),
        getter=get_task,
        state=GetTaskDialogSG.save_window
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
