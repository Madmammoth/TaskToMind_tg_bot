from aiogram import F
from aiogram.enums import ContentType
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.kbd import (
    Button,
    Cancel,
    ListGroup,
    ScrollingGroup,
    SwitchTo, Row,
)
from aiogram_dialog.widgets.text import Const, Format

from app.bot.dialogs.common.getters import get_lists
from app.bot.dialogs.components import WindowWithoutInput
from app.bot.dialogs.create_list.getters import get_new_list
from app.bot.dialogs.create_list.handlers import (
    correct_title_list_input,
    empty_title_input,
    wrong_title_list_input,
    go_insert_in_list,
    go_save_new_list,
    clear_in_list,
    select_list,
    go_cancel_yes,
)
from app.bot.dialogs.create_task.handlers import empty_text_check
from app.bot.dialogs.common.handlers import get_start_data
from app.bot.dialogs.states import CreateListDialogSG

create_list_dialog = Dialog(
    Window(
        Const("✍️ Введи название списка:"),
        Cancel(text=Const("↩️ Отмена")),
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
        state=CreateListDialogSG.input_list_title_window,
    ),
    WindowWithoutInput(
        Const("Добавление списка задач:\n"),
        Format("{new_list_title}"),
        Format("\nВ списке: {in_list_title}", when="in_list_id"),
        Button(
            text=Const("✅ Сохранить"),
            id="save",
            on_click=go_save_new_list
        ),
        # Button(
        #     text=Const("Переименовать список"),
        #     id="rename_list",
        #     on_click=go_pass,
        # ),
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
            state=CreateListDialogSG.cancel_window,
        ),
        getter=get_new_list,
        state=CreateListDialogSG.add_list_window,
    ),
    WindowWithoutInput(
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
            state=CreateListDialogSG.add_list_window,
        ),
        getter=get_lists,
        state=CreateListDialogSG.in_list_window
    ),
    WindowWithoutInput(
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
                state=CreateListDialogSG.add_list_window
            ),
        ),
        state=CreateListDialogSG.cancel_window
    ),
    on_start=get_start_data,
)
