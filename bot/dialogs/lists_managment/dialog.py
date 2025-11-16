from aiogram import F
from aiogram.enums import ContentType
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import MessageInput, TextInput
from aiogram_dialog.widgets.kbd import (
    ListGroup,
    Button,
    SwitchTo,
    Cancel,
    Row,
    ScrollingGroup,
)
from aiogram_dialog.widgets.text import Const, Format, List

from bot.dialogs.common.getters import get_lists
from bot.dialogs.common.handlers import go_pass
from bot.dialogs.lists_managment.getters import (
    get_new_list,
    get_tasks,
    get_list_title_to_delete,
)
from bot.dialogs.lists_managment.handlers import (
    go_cancel_yes,
    correct_title_list_input,
    wrong_title_list_input,
    empty_title_input,
    go_selected_task,
    go_save_new_list,
    clear_in_list,
    go_insert_in_list,
    select_list,
    go_delete_list_yes,
    go_selected_list,
)
from bot.dialogs.start.handlers import empty_text_check
from bot.dialogs.states import TaskListsDialogSG

lists_management_dialog = Dialog(
    Window(
        Const("Тут все твои списки задач:"),
        ScrollingGroup(
            ListGroup(
                Button(
                    Format("{item[pos]} {item[list_title]}"),
                    id="selected_list",
                    on_click=go_selected_list,
                ),
                id="lists_search",
                item_id_getter=lambda item: item["list_id"],
                items="lists"
            ),
            id="scroll_lists_search",
            width=1,
            height=5,
        ),
        SwitchTo(
            text=Const("➕ Новый список"),
            id="new_list",
            state=TaskListsDialogSG.input_list_title_window,
        ),
        Button(
            text=Const("🔀 Изменить порядок"),
            id="change_lists_view",
            on_click=go_pass,
        ),
        Cancel(
            text=Const("🔙 Назад"),
            id="back",
        ),
        getter=get_lists,
        state=TaskListsDialogSG.main_lists_window,
    ),
    Window(
        Const("✍️ Введи название списка:"),
        SwitchTo(
            text=Const("↩️ Отмена"),
            id="cancel",
            state=TaskListsDialogSG.main_lists_window,
        ),
        TextInput(
            id="text_task_input",
            type_factory=empty_text_check,
            on_success=correct_title_list_input,
            on_error=empty_title_input,
        ),
        MessageInput(
            func=wrong_title_list_input,
            content_types=ContentType.ANY,
        ),
        state=TaskListsDialogSG.input_list_title_window,
    ),
    Window(

        Const("Добавление списка задач:\n"),
        Format("{new_list_title}"),
        Format("\nВ списке: {in_list_title}", when="in_list_id"),
        Button(
            text=Const("✅ Сохранить"),
            id="save",
            on_click=go_save_new_list
        ),
        Button(
            text=Const("Переименовать список"),
            id="rename_list",
            on_click=go_pass,
        ),
        Button(
            text=Const("📥 Вложить в список"),
            id="in_list",
            on_click=go_insert_in_list,
        ),
        Button(
            text=Const("Убрать из списка"),
            id="not_sub_list",
            on_click=clear_in_list,
            when="in_list_id",
        ),
        SwitchTo(
            text=Const("↩️ Отмена"),
            id="cancel",
            state=TaskListsDialogSG.cancel_window,
        ),
        getter=get_new_list,
        state=TaskListsDialogSG.add_list_window,
    ),
    Window(
        Const("Точно отменить создание нового списка?"),
        Row(
            Button(
                text=Const("✅ Да"),
                id="yes",
                on_click=go_cancel_yes,
            ),
            SwitchTo(
                text=Const("↩️ Нет"),
                id="no",
                state=TaskListsDialogSG.add_list_window
            ),
        ),
        state=TaskListsDialogSG.cancel_window
    ),
    Window(
        Const("Список задач:"),
        Format("<b>{list_title}</b>"),
        Const("\nПодсписки:", when="sub_lists"),
        List(
            Format("{item[0]}. {item[1]}"),
            items="sub_lists",
            when="sub_lists",
        ),
        Const("\nЗадачи:"),
        Const("<i>в этом списке пока нет задач</i>", when=~F["tasks"]),
        ScrollingGroup(
            ListGroup(
                Button(
                    Format("{item[task_title]}"),
                    id="selected_task",
                    on_click=go_selected_task,
                ),
                id="tasks_search",
                item_id_getter=lambda item: item["task_id"],
                items="tasks",
                when=~F["is_empty_list"]
            ),
            id="scroll_tasks_search",
            width=1,
            height=5,
        ),
        Button(
            text=Const("Изменить имя списка"),
            id="rename_list",
            on_click=go_pass,
        ),
        Button(
            text=Const("Переместить список"),
            id="move_list",
            on_click=go_pass,
        ),
        Button(
            text=Const("Поделиться списком"),
            id="list_share",
            on_click=go_pass,
        ),
        SwitchTo(
            text=Const("Удалить список"),
            id="delete_list",
            state=TaskListsDialogSG.delete_list_window,
            when="is_empty_list"
        ),
        SwitchTo(
            text=Const("🔙 Назад"),
            id="back",
            state=TaskListsDialogSG.main_lists_window,
        ),
        getter=get_tasks,
        state=TaskListsDialogSG.list_with_tasks
    ),
    Window(
        Const(
            "Выбери список, в который вложить новый список:",
            when="lists",
        ),
        Const(
            "Нет списков для вложения.",
            when=~F["lists"],
        ),
        ScrollingGroup(
            ListGroup(
                Button(
                    Format("{item[pos]} {item[list_title]}"),
                    id="selected_list",
                    on_click=select_list,
                ),
                id="lists_search",
                item_id_getter=lambda item: item["list_id"],
                items="lists",
                when="lists",
            ),
            id="scroll_lists_search",
            width=1,
            height=10,
        ),
        SwitchTo(
            text=Const("↩️ Отмена"),
            id="back",
            state=TaskListsDialogSG.add_list_window,
        ),
        getter=get_lists,
        state=TaskListsDialogSG.in_list_window
    ),
    Window(
        Const("Точно удалить этот список задач:"),
        Format("{list_title}"),
        Row(
            Button(
                text=Const("✅ Да"),
                id="yes",
                on_click=go_delete_list_yes,
            ),
            SwitchTo(
                text=Const("↩️ Нет"),
                id="no",
                state=TaskListsDialogSG.list_with_tasks
            ),
        ),
        getter=get_list_title_to_delete,
        state=TaskListsDialogSG.delete_list_window,
    ),
)
