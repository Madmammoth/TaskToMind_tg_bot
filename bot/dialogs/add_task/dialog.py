from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import (
    Row, Button, SwitchTo, Column, Next, Back, ListGroup
)
from aiogram_dialog.widgets.text import Format, Const

from bot.dialogs.add_task.getters import get_task, get_lists
from bot.dialogs.add_task.handlers import (
    go_pass, go_cancel_yes, go_save_yes, go_priority, go_urgency,
    add_task_dialog_start, go_selected_list
)
from bot.dialogs.states import GetTaskDialogSG

add_task_dialog = Dialog(
    Window(
        Format("{task_title}"),
        Format("{task_description}", when="task_description"),
        Format("\nСписок: {list_title}"),
        Format("Приоритет: {priority_label}"),
        Format("Срочность: {urgency_label}"),
        Column(
            SwitchTo(
                text=Const("Сохранить"),
                id="save",
                state=GetTaskDialogSG.save_task_window
            ),
            SwitchTo(
                text=Const("Список"),
                id="list_title",
                state=GetTaskDialogSG.select_list_window
            ),
            SwitchTo(
                text=Const("Приоритет"),
                id="priority",
                state=GetTaskDialogSG.task_priority_window
            ),
            SwitchTo(
                text=Const("Срочность"),
                id="urgency",
                state=GetTaskDialogSG.task_urgency_window
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
        Format("{task_title}"),
        Format("{task_description}", when="task_description"),
        Format("\nСписок: {list_title}"),
        Format("Приоритет: {priority_label}"),
        Format("Срочность: {urgency_label}"),
        Column(
            SwitchTo(
                text=Const("Сохранить"),
                id="save",
                state=GetTaskDialogSG.save_task_window
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
                    id="repeat",
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
        Const("Выбери нужный список:\n"),
        ListGroup(
            Button(
                Format("{item[list_title]}"),
                id="selected_list",
                on_click=go_selected_list,
            ),
            id="lists_search",
            item_id_getter=lambda item: item["list_id"],
            items="lists"
        ),
        Row(
            Button(
                text=Const("Новый список"),
                id="new_list",
                on_click=go_pass,
            ),
            SwitchTo(
                text=Const("🔙 Назад"),
                id="back",
                state=GetTaskDialogSG.add_task_window,
            ),
        ),
        getter=get_lists,
        state=GetTaskDialogSG.select_list_window
    ),
    Window(
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
            state=GetTaskDialogSG.add_task_window
        ),
        getter=get_task,
        state=GetTaskDialogSG.task_priority_window
    ),
    Window(
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
            state=GetTaskDialogSG.add_task_window
        ),
        getter=get_task,
        state=GetTaskDialogSG.task_urgency_window
    ),
    Window(
        Const("Задача:\n"),
        Format("{task_title}"),
        Format("{task_description}", when="task_description"),
        Const("\nбудет сохранена со следующими параметрами:"),
        Format("\nСписок: {list_title}"),
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
                state=GetTaskDialogSG.add_task_window
            ),
        ),
        getter=get_task,
        state=GetTaskDialogSG.save_task_window
    ),
    Window(
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
                state=GetTaskDialogSG.add_task_window
            ),
        ),
        state=GetTaskDialogSG.cancel_window
    ),
    on_start=add_task_dialog_start,
)
