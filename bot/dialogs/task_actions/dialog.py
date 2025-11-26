from aiogram import F
from aiogram_dialog import Dialog, StartMode
from aiogram_dialog.widgets.kbd import (
    Back,
    Button,
    Cancel,
    Next,
    Row,
    Start,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Format, Const, List

from bot.dialogs.common.getters import get_dialog_data
from bot.dialogs.common.handlers import get_start_data, on_process_result
from bot.dialogs.components import WindowWithInput, WindowWithoutInput
from bot.dialogs.states import TaskActionsDialogSG, StartSG
from bot.dialogs.task_actions.getters import get_task
from bot.dialogs.task_actions.handlers import (
    go_complete_yes,
    postpone,
    go_not_complete_yes,
    go_cancel_yes,
    go_not_cancel_yes,
    select_list,
)

task_actions_dialog = Dialog(
    WindowWithInput(
        Format("{task_title}"),
        Format("{description}", when="description"),
        Format("\nВ списке: {selected_list_title}"),
        Format("Приоритет: {priority_label}"),
        Format("Срочность: {urgency_label}"),
        Const("\nСтатус задачи:"),
        Format("<i>{status_label}</i>"),
        Const("\nИмеют доступ к задаче:", when="is_shared"),
        List(
            Format("@{item[1]}"),
            items="users",
            sep=", ",
            when="is_shared",
        ),
        Format("Время на задачу: {duration}", when="duration"),
        Const("\nСрок выполнения:", when="deadline"),
        Format("<i>{deadline}</i>", when="deadline"),
        Format(
            text="Задача завершена:\n<i>{completed_at}</i>",
            when="completed_at",
        ),
        Format(text="Задача отменена:\n<i>{canceled_at}</i>",
               when="canceled_at",
               ),
        Const(
            text="\nНапоминания: включены",
            when=F["remind"] & ~F["completed_at"] & ~F["canceled_at"],
        ),
        Const(
            text="\nНапоминания: выключены",
            when=~F["remind"] & ~F["completed_at"] & ~F["canceled_at"],
        ),
        Const(
            text="\nПовтор задачи: нет",
            when=~F["is_recurring"] & ~F["canceled_at"],
        ),
        Const(
            text="\nПовтор задачи: да",
            when=F["is_recurring"] & ~F["canceled_at"],
        ),
        Const(
            text="Период повтора:",
            when=F["is_recurring"] & ~F["canceled_at"],
        ),
        Format(
            text="{recurrence_rule_text}",
            when=F["is_recurring"] & ~F["canceled_at"],
        ),
        # SwitchTo(
        #     text=Const("Поделиться"),
        #     id="share_task",
        #     state=TaskActionsDialogSG.share_task_window,
        #     when=~F["is_shared"] & ~F["completed_at"] & ~F["canceled_at"],
        # ),
        SwitchTo(
            text=Const("Чек-лист"),
            id="checklist",
            state=TaskActionsDialogSG.checklist_window,
            when="has_checklist",
        ),
        SwitchTo(
            text=Const("Выполнить"),
            id="complete_task",
            state=TaskActionsDialogSG.complete_task_window,
            when=~F["completed_at"] & ~F["canceled_at"],
        ),
        SwitchTo(
            text=Const("Не выполнена"),
            id="not_complete_task",
            state=TaskActionsDialogSG.not_complete_task_window,
            when="completed_at",
        ),
        Row(
            Button(
                text=Const("+час"),
                id="deadline_hour_more",
                on_click=postpone,
            ),
            Button(
                text=Const("+день"),
                id="deadline_day_more",
                on_click=postpone,
            ),
            Button(
                text=Const("+неделя"),
                id="deadline_week_more",
                on_click=postpone,
            ),
            Button(
                text=Const("+..."),
                id="deadline_edit",
                on_click=postpone,
            ),
            when=F["deadline"] & ~F["completed_at"] & ~F["canceled_at"],
        ),
        SwitchTo(
            text=Const("Отменить"),
            id="cancel_task",
            state=TaskActionsDialogSG.cancel_task_window,
            when=~F["canceled_at"] & ~F["completed_at"],
        ),
        SwitchTo(
            text=Const("Восстановить"),
            id="not_cancel_task",
            state=TaskActionsDialogSG.not_cancel_task_window,
            when="canceled_at",
        ),
        SwitchTo(
            text=Const("Повторить"),
            id="repeat_task",
            state=TaskActionsDialogSG.repeat_task_window,
            when="completed_at",
        ),
        Next(
            text=Const("Редактировать"),
            id="task_edit",
            when=~F["canceled_at"] & ~F["completed_at"],
        ),
        Cancel(Const("🔙 Выйти из задачи")),
        Start(
            Const("🏠 Главное меню"),
            id="main_menu",
            state=StartSG.start_window,
            mode=StartMode.RESET_STACK,
        ),
        getter=get_task,
        state=TaskActionsDialogSG.main_task_window,
    ),
    WindowWithInput(
        Format("{task_title}"),
        Format("{description}", when="description"),
        Format("\nВ списке: {selected_list_title}"),
        Format("Приоритет: {priority_label}"),
        Format("Срочность: {urgency_label}"),
        Const("\nСтатус задачи:"),
        Format("<i>{status_label}</i>"),
        Const("\nИмеют доступ к задаче:", when="is_shared"),
        List(
            Format("@{item[1]}"),
            items="users",
            sep=", ",
            when="is_shared",
        ),
        Format("Время на задачу: {duration}", when="duration"),
        Const("\nСрок выполнения:", when="deadline"),
        Format("<i>{deadline}</i>", when="deadline"),
        Format(
            text="Задача завершена:\n<i>{completed_at}</i>",
            when="completed_at",
        ),
        Format(text="Задача отменена:\n<i>{canceled_at}</i>",
               when="canceled_at",
               ),
        Const(
            text="\nНапоминания: включены",
            when=F["remind"] & ~F["completed_at"] & ~F["canceled_at"],
        ),
        Const(
            text="\nНапоминания: выключены",
            when=~F["remind"] & ~F["completed_at"] & ~F["canceled_at"],
        ),
        Const(
            text="\nПовтор задачи: нет",
            when=~F["is_recurring"] & ~F["canceled_at"],
        ),
        Const(
            text="\nПовтор задачи: да",
            when=F["is_recurring"] & ~F["canceled_at"],
        ),
        Const(
            text="Период повтора:",
            when=F["is_recurring"] & ~F["canceled_at"],
        ),
        Format(
            text="{recurrence_rule_text}",
            when=F["is_recurring"] & ~F["canceled_at"],
        ),
        Button(
            text=Const("Список"),
            id="select_list",
            on_click=select_list,
        ),
        SwitchTo(
            text=Const("Приоритет"),
            id="priority",
            state=TaskActionsDialogSG.task_priority_window,
        ),
        SwitchTo(
            text=Const("Срочность"),
            id="urgency",
            state=TaskActionsDialogSG.task_urgency_window,
        ),
        SwitchTo(
            text=Const("Напомнить"),
            id="remind",
            state=TaskActionsDialogSG.task_remind_window,
        ),
        SwitchTo(
            text=Const("Время на задачу"),
            id="duration",
            state=TaskActionsDialogSG.task_duration_window,
        ),
        SwitchTo(
            text=Const("Срок выполнения"),
            id="deadline",
            state=TaskActionsDialogSG.task_deadline_window,
        ),
        SwitchTo(
            text=Const("Повторять"),
            id="recurrence",
            state=TaskActionsDialogSG.task_recurrence_window,
        ),
        Back(
            text=Const("Управлять"),
            id="manage",
        ),
        Cancel(Const("🔙 Выйти из задачи")),
        Start(
            Const("🏠 Главное меню"),
            id="main_menu",
            state=StartSG.start_window,
            mode=StartMode.RESET_STACK,
        ),
        getter=get_dialog_data,
        state=TaskActionsDialogSG.main_task_window_2,
    ),
    WindowWithoutInput(
        Const("Завершить задачу?\n"),
        Format("<b>{task_title}</b>"),
        Row(
            Button(
                text=Const("✅ Да"),
                id="yes",
                on_click=go_complete_yes,
            ),
            SwitchTo(
                text=Const("❌ Нет"),
                id="no",
                state=TaskActionsDialogSG.main_task_window
            ),
        ),
        getter=get_dialog_data,
        state=TaskActionsDialogSG.complete_task_window,
    ),
    WindowWithoutInput(
        Const("Вернуть задачу в работу?\n"),
        Format("<b>{task_title}</b>"),
        Row(
            Button(
                text=Const("✅ Да"),
                id="yes",
                on_click=go_not_complete_yes,
            ),
            SwitchTo(
                text=Const("❌ Нет"),
                id="no",
                state=TaskActionsDialogSG.main_task_window
            ),
        ),
        getter=get_dialog_data,
        state=TaskActionsDialogSG.not_complete_task_window,
    ),
    WindowWithoutInput(
        Const("Отменить задачу?\n"),
        Format("<b>{task_title}</b>"),
        Row(
            Button(
                text=Const("✅ Да"),
                id="yes",
                on_click=go_cancel_yes,
            ),
            SwitchTo(
                text=Const("❌ Нет"),
                id="no",
                state=TaskActionsDialogSG.main_task_window
            ),
        ),
        getter=get_dialog_data,
        state=TaskActionsDialogSG.cancel_task_window,
    ),
    WindowWithoutInput(
        Const("Восстановить задачу?\n"),
        Format("<b>{task_title}</b>"),
        Row(
            Button(
                text=Const("✅ Да"),
                id="yes",
                on_click=go_not_cancel_yes,
            ),
            SwitchTo(
                text=Const("❌ Нет"),
                id="no",
                state=TaskActionsDialogSG.main_task_window
            ),
        ),
        getter=get_dialog_data,
        state=TaskActionsDialogSG.not_cancel_task_window,
    ),
    on_start=get_start_data,
    on_process_result=on_process_result,
)
