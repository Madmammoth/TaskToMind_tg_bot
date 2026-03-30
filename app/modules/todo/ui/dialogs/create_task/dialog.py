from aiogram.enums import ContentType
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.kbd import (
    Back,
    Button,
    Cancel,
    Column,
    Next,
    Row,
    Start,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Format, Const

from app.modules.todo.ui.dialogs.common.handlers import update_dialog_data_from_start
from app.modules.todo.ui.dialogs.components import WindowWithoutInput
from app.modules.todo.ui.dialogs.create_task.getters import get_task
from app.modules.todo.ui.dialogs.create_task.handlers import (
    go_priority,
    go_urgency,
    go_cancel_yes,
    go_save_yes,
    empty_text_check,
    empty_text_input,
    correct_text_task_input,
    wrong_text_task_input,
    update_dialog_data_from_result,
)
from app.modules.todo.ui.dialogs.enums import ListSelectionMode
from app.modules.todo.ui.dialogs.states import CreateTaskDialogSG, SelectListDialogSG

create_task_dialog = Dialog(
    Window(
        Const("✍️ Введи текст задачи"),
        Cancel(text=Const("Отмена")),
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
        state=CreateTaskDialogSG.input_task_window,
    ),
    WindowWithoutInput(
        Format("{task_title}"),
        Format("{task_description}", when="task_description"),
        Format("\nСписок: {selected_list_title}"),
        Format("Приоритет: {priority_label}"),
        Format("Срочность: {urgency_label}"),
        Column(
            SwitchTo(
                text=Const("Сохранить"),
                id="save",
                state=CreateTaskDialogSG.save_task_window
            ),
            Start(
                text=Const("Список"),
                id="select_list",
                state=SelectListDialogSG.select_list_window,
                data={"mode": ListSelectionMode.CREATE_TASK},
            ),
            SwitchTo(
                text=Const("Приоритет"),
                id="priority",
                state=CreateTaskDialogSG.task_priority_window
            ),
            SwitchTo(
                text=Const("Срочность"),
                id="urgency",
                state=CreateTaskDialogSG.task_urgency_window
            ),
            Next(
                text=Const("Дополнительные настройки"),
                id="extra_settings",
            ),
            SwitchTo(
                text=Const("Отмена"),
                id="cancel",
                state=CreateTaskDialogSG.cancel_window
            ),
        ),
        getter=get_task,
        state=CreateTaskDialogSG.add_task_window
    ),
    WindowWithoutInput(
        Format("{task_title}"),
        Format("{task_description}", when="task_description"),
        Format("\nСписок: {selected_list_title}"),
        Format("Приоритет: {priority_label}"),
        Format("Срочность: {urgency_label}"),
        Column(
            SwitchTo(
                text=Const("Сохранить"),
                id="save",
                state=CreateTaskDialogSG.save_task_window
            ),
            # Button(
            #     text=Const("Срок завершения"),
            #     id="deadline",
            #     on_click=go_pass
            # ),
            # Button(
            #     text=Const("Продолжительность"),
            #     id="duration",
            #     on_click=go_pass
            # ),
            # Button(
            #     text=Const("Напомнить"),
            #     id="remind",
            #     on_click=go_pass
            # ),
            # Button(
            #     text=Const("Чек-лист"),
            #     id="check_list",
            #     on_click=go_pass
            # ),
            # Column(
            #     Button(
            #         text=Const("Отложить"),
            #         id="delay",
            #         on_click=go_pass
            #     ),
            #     Button(
            #         text=Const("Повтор"),
            #         id="repeat",
            #         on_click=go_pass
            #     ),
            # ),
        ),
        Back(
            text=Const("Основные настройки"),
            id="back",
        ),
        SwitchTo(
            text=Const("Отмена"),
            id="cancel",
            state=CreateTaskDialogSG.cancel_window
        ),
        getter=get_task,
        state=CreateTaskDialogSG.add_task_window_2
    ),
    WindowWithoutInput(
        Const("Текущий приоритет задачи:\n"),
        Format("<b>{priority_label}</b>"),
        Const("\nЗадайте приоритетность задачи.\n"),
        Const("<i>Описание:</i>"),
        Const(
            "<i><b>Высокий</b> — влияет на достижение главных целей </i>"
            "<i>и долгосрочный успех.</i>"),
        Const(
            "<i><b>Средний</b> — полезно, но не критично </i>"
            "<i>для ключевых результатов.</i>"),
        Const(
            "<i><b>Низкий</b> — несущественно, не влияет </i>"
            "<i>на важные задачи и цели.</i>"),
        Row(
            Button(
                text=Const("Высокий"),
                id="high",
                on_click=go_priority,
            ),
            Button(
                text=Const("Средний"),
                id="medium",
                on_click=go_priority
            ),
            Button(
                text=Const("Низкий"),
                id="low",
                on_click=go_priority
            ),
        ),
        SwitchTo(
            text=Const("🔙 Назад"),
            id="back",
            state=CreateTaskDialogSG.add_task_window
        ),
        getter=get_task,
        state=CreateTaskDialogSG.task_priority_window
    ),
    WindowWithoutInput(
        Const("Текущая срочность задачи:\n"),
        Format("<b>{urgency_label}</b>"),
        Const("\nЗадайте срочность задачи.\n"),
        Const("<i>Описание:</i>"),
        Const(
            "<i><b>Высокая</b> — требует внимания прямо сейчас, </i>"
            "<i>иначе будут негативные последствия.</i>"),
        Const(
            "<i><b>Средняя</b> — желательно сделать в ближайшее время, </i>"
            "<i>но можно немного отложить.</i>"),
        Const(
            "<i><b>Низкая</b> — не горит, </i>"
            "<i>задача может подождать без проблем.</i>"),
        Row(
            Button(
                text=Const("Высокая"),
                id="high",
                on_click=go_urgency,
            ),
            Button(
                text=Const("Средняя"),
                id="medium",
                on_click=go_urgency
            ),
            Button(
                text=Const("Низкая"),
                id="low",
                on_click=go_urgency
            ),
        ),
        SwitchTo(
            text=Const("🔙 Назад"),
            id="back",
            state=CreateTaskDialogSG.add_task_window
        ),
        getter=get_task,
        state=CreateTaskDialogSG.task_urgency_window
    ),
    WindowWithoutInput(
        Const("Задача:\n"),
        Format("{task_title}"),
        Format("{task_description}", when="task_description"),
        Const("\nбудет сохранена со следующими параметрами:"),
        Format("\nСписок: {selected_list_title}"),
        Format("Приоритет: {priority_label}"),
        Format("Срочность: {urgency_label}"),
        Format("Срок завершения: {deadline}", when="deadline_show"),
        Format("Продолжительность: {duration}", when="duration_show"),
        Format("Напомнить: {remind}", when="remind_show"),
        Format("Повтор: {repeat}", when="repeat_show"),
        Format("Чек-лист: {checklist}", when="checklist_show"),
        Format("\nТег: {tag}", when="tag_show"),
        Const("\nВсё верно?"),
        Row(
            Button(
                text=Const("✅ Да"),
                id="yes",
                on_click=go_save_yes,
            ),
            SwitchTo(
                text=Const("❌ Нет"),
                id="no",
                state=CreateTaskDialogSG.add_task_window
            ),
        ),
        getter=get_task,
        state=CreateTaskDialogSG.save_task_window
    ),
    WindowWithoutInput(
        Const("Точно отменить добавление задачи?"),
        Row(
            Button(
                text=Const("✅ Да"),
                id="yes",
                on_click=go_cancel_yes,
            ),
            SwitchTo(
                text=Const("↩️ Нет"),
                id="no",
                state=CreateTaskDialogSG.add_task_window
            ),
        ),
        state=CreateTaskDialogSG.cancel_window
    ),
    on_start=update_dialog_data_from_start,
    on_process_result=update_dialog_data_from_result,
)
