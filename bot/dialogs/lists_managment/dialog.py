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
    Multiselect,
)
from aiogram_dialog.widgets.text import Const, Format, List

from bot.dialogs.lists_managment.getters import (
    get_main_lists,
    get_new_list,
    get_tasks,
    get_lists_for_delete,
    get_selected_lists_for_delete,
    get_lists_for_parent,
)
from bot.dialogs.lists_managment.handlers import (
    go_selected_list,
    go_cancel_yes,
    correct_title_list_input,
    wrong_title_list_input,
    empty_title_input,
    go_selected_task,
    go_delete_lists,
    go_delete_lists_yes,
    select_list,
    go_save_new_list, clear_in_list,
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
        SwitchTo(
            text=Const("🔀 Изменить порядок"),
            id="change_lists_view",
            state=TaskListsDialogSG.change_view_window,
        ),
        SwitchTo(
            text=Const("Удалить список"),
            id="delete_lists",
            state=TaskListsDialogSG.delete_lists_window,
        ),
        Cancel(
            text=Const("🔙 Назад"),
            id="back",
        ),
        getter=get_main_lists,
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
        SwitchTo(
            text=Const("Переименовать список"),
            id="rename_list",
            state=TaskListsDialogSG.rename_new_list_window,
        ),
        SwitchTo(
            text=Const("📥 Вложить в список"),
            id="in_list",
            state=TaskListsDialogSG.in_list_window,
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
        SwitchTo(
            text=Const("Изменить имя списка"),
            id="rename_list",
            state=TaskListsDialogSG.rename_list_window,
        ),
        SwitchTo(
            text=Const("Переместить список"),
            id="move_list",
            state=TaskListsDialogSG.move_list_window,
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
        Const("Доступные для удаления списки задач."),
        Const("Выбери те, что нужно удалить:"),
        ScrollingGroup(
            Multiselect(
                Format("❌ {item[list_title]} ❌"),
                Format("{item[list_title]}"),
                id="m_lists",
                item_id_getter=lambda item: item["list_id"],
                items="lists"
            ),
            id="scroll_lists_search",
            width=1,
            height=5,
        ),
        Button(
            text=Const("🗑️ Удалить выбранные"),
            id="delete_selected",
            on_click=go_delete_lists,
        ),
        SwitchTo(
            text=Const("↩️ Отмена"),
            id="back",
            state=TaskListsDialogSG.main_lists_window,
        ),
        getter=get_lists_for_delete,
        state=TaskListsDialogSG.delete_lists_window,
    ),
    Window(
        Const("Будут удалены следующие списки задач:"),
        List(
            Format("{item[0]}. {item[2]}"),
            items="selected_lists",
        ),
        Const("\nВсё верно?"),
        Row(
            Button(
                text=Const("✅ Да"),
                id="yes",
                on_click=go_delete_lists_yes,
            ),
            SwitchTo(
                text=Const("❌ Нет"),
                id="no",
                state=TaskListsDialogSG.delete_lists_window,
            ),
        ),
        SwitchTo(
            text=Const("↩️ Отмена"),
            id="cancel",
            state=TaskListsDialogSG.main_lists_window,
        ),
        getter=get_selected_lists_for_delete,
        state=TaskListsDialogSG.ack_delete_lists_window,
    ),
    Window(
        Const(
            "Выбери список, в который вложить новый список:",
            when="has_lists",
        ),
        Const(
            "Нет списков для вложения.",
            when=~F["has_lists"],
        ),
        ScrollingGroup(
            ListGroup(
                Button(
                    Format("{item[list_title]}"),
                    id="selected_list",
                    on_click=select_list,
                ),
                id="lists_search",
                item_id_getter=lambda item: item["list_id"],
                items="lists_for_parent",
                when="has_lists",
            ),
            id="scroll_lists_search",
            width=1,
            height=5,
        ),
        SwitchTo(
            text=Const("↩️ Отмена"),
            id="back",
            state=TaskListsDialogSG.main_lists_window,
        ),
        getter=get_lists_for_parent,
        state=TaskListsDialogSG.in_list_window
    ),
)
