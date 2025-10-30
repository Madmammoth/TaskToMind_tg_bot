from aiogram.enums import ContentType
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import MessageInput, TextInput
from aiogram_dialog.widgets.kbd import ListGroup, Button, SwitchTo, Cancel, Row
from aiogram_dialog.widgets.text import Const, Format

from bot.dialogs.lists_managment.getters import get_main_lists, get_new_list
from bot.dialogs.lists_managment.handlers import (
    go_selected_list, go_cancel_yes, go_save_yes,
    correct_title_list_input, wrong_title_list_input, empty_title_input,
)
from bot.dialogs.start.handlers import empty_text_check
from bot.dialogs.states import TaskListsDialogSG

lists_management_dialog = Dialog(
    Window(
        Const("Твои списки:"),
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
        SwitchTo(
            text=Const("Новый список"),
            id="new_list",
            state=TaskListsDialogSG.input_list_title_window,
        ),
        SwitchTo(
            text=Const("Изменить порядок"),
            id="change_lists_view",
            state=TaskListsDialogSG.change_view_window,
        ),
        Cancel(
            text=Const("Назад"),
            id="back",
        ),
        getter=get_main_lists,
        state=TaskListsDialogSG.main_lists_window,
    ),
    Window(
        Const("✍️ Введи название списка:"),
        SwitchTo(
            text=Const("Отмена"),
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
        SwitchTo(
            text=Const("Сохранить"),
            id="save",
            state=TaskListsDialogSG.save_list_window
        ),
        SwitchTo(
            text=Const("Добавить в список"),
            id="in_list",
            state=TaskListsDialogSG.in_list_window,
        ),
        SwitchTo(
            text=Const("Отмена"),
            id="cancel",
            state=TaskListsDialogSG.cancel_window,
        ),
        getter=get_new_list,
        state=TaskListsDialogSG.add_list_window,
    ),
    Window(
        Const("Сохранение списка задач:\n"),
        Format("{new_list_title}"),
        Format("\nВ списке: {in_list_id}", when="in_list_id"),
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
                state=TaskListsDialogSG.add_list_window
            ),
        ),
        getter=get_new_list,
        state=TaskListsDialogSG.save_list_window
    ),
    Window(
        Const("Точно отменить создание нового списка?"),
        Row(
            Button(
                text=Const("Да"),
                id="yes",
                on_click=go_cancel_yes,
            ),
            SwitchTo(
                text=Const("Нет"),
                id="no",
                state=TaskListsDialogSG.add_list_window
            ),
        ),
        state=TaskListsDialogSG.cancel_window
    ),
)
