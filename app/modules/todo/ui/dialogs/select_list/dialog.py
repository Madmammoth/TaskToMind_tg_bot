from aiogram_dialog import Dialog
from aiogram_dialog.widgets.kbd import (
    Button,
    Cancel,
    ListGroup,
    ScrollingGroup,
    Start,
)
from aiogram_dialog.widgets.text import Const, Format

from app.modules.todo.ui.dialogs.common.handlers import update_dialog_data_from_start
from app.modules.todo.ui.dialogs.components import WindowWithoutInput
from app.modules.todo.ui.dialogs.select_list.getters import lists_getter
from app.modules.todo.ui.dialogs.select_list.handlers import select_list
from app.modules.todo.ui.dialogs.states import SelectListDialogSG, CreateListDialogSG

select_list_dialog = Dialog(
    WindowWithoutInput(
        Const("Выбери нужный список:\n"),
        ScrollingGroup(
            ListGroup(
                Button(
                    Format("{item[pos]} {item[list_title]}"),
                    id="selected_list",
                    on_click=select_list,
                ),
                id="lists_search",
                item_id_getter=lambda item: item["list_id"],
                items="buttons"
            ),
            id="scroll_lists_search",
            width=1,
            height=10,
        ),
        Start(
            text=Const("➕ Новый список"),
            id="new_list",
            state=CreateListDialogSG.input_list_title_window,
        ),
        Cancel(Const("🔙 Назад")),
        getter=lists_getter,
        state=SelectListDialogSG.select_list_window
    ),
    on_start=update_dialog_data_from_start,
)
