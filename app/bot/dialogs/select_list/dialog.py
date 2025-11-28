from aiogram_dialog import Dialog
from aiogram_dialog.widgets.kbd import (
    Button,
    Cancel,
    ListGroup,
    ScrollingGroup,
    Start,
)
from aiogram_dialog.widgets.text import Const, Format

from app.bot.dialogs.common.getters import get_lists
from app.bot.dialogs.common.handlers import get_start_data
from app.bot.dialogs.components import WindowWithoutInput
from app.bot.dialogs.select_list.handlers import select_list
from app.bot.dialogs.states import SelectListDialogSG, CreateListDialogSG

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
                items="lists"
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
        getter=get_lists,
        state=SelectListDialogSG.select_list_window
    ),
    on_start=get_start_data,
)
