from aiogram import F
from aiogram_dialog import Dialog
from aiogram_dialog.widgets.kbd import (
    ListGroup,
    Button,
    SwitchTo,
    Cancel,
    Row,
    ScrollingGroup,
    Start,
)
from aiogram_dialog.widgets.text import Const, Format, List

from app.bot.dialogs.common.getters import get_lists
from app.bot.dialogs.common.handlers import update_dialog_data_from_result
from app.bot.dialogs.components import WindowWithInput, WindowWithoutInput
from app.bot.dialogs.lists_managment.getters import (
    get_tasks,
    get_list_title_to_delete,
)
from app.bot.dialogs.lists_managment.handlers import (
    go_selected_task,
    go_delete_list_yes,
    go_selected_list,
)
from app.bot.dialogs.states import (
    ListsManagementDialogSG,
    CreateListDialogSG,
    CreateTaskDialogSG
)

lists_management_dialog = Dialog(
    WindowWithInput(
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
            height=10,
        ),
        Start(
            text=Const("➕ Новый список"),
            id="new_list",
            state=CreateListDialogSG.input_list_title_window,
        ),
        # Button(
        #     text=Const("🔀 Изменить порядок"),
        #     id="change_lists_view",
        #     on_click=go_pass,
        # ),
        Cancel(
            text=Const("🔙 Назад"),
            id="back",
        ),
        getter=get_lists,
        state=ListsManagementDialogSG.main_lists_window,
    ),
    WindowWithInput(
        Const("Список задач:"),
        Format("<b>{list_title}</b>"),
        Const("\nПодсписки:", when="sub_lists"),
        List(
            Format("{item[0]}. {item[1]}"),
            items="sub_lists",
            when="sub_lists",
        ),
        Const("\nЗадачи:"),
        Const("<i>в этом списке пока нет задач</i>", when=~F["task_buttons"]),
        ScrollingGroup(
            ListGroup(
                Button(
                    Format("{item[pos]}. {item[task_title]}"),
                    id="select_task",
                    on_click=go_selected_task,
                ),
                id="tasks_search",
                item_id_getter=lambda item: item["task_id"],
                items="task_buttons",
                when=~F["is_empty_list"]
            ),
            id="scroll_tasks_search",
            width=1,
            height=10,
        ),
        # Button(
        #     text=Const("Изменить имя списка"),
        #     id="rename_list",
        #     on_click=go_pass,
        # ),
        # Button(
        #     text=Const("Переместить список"),
        #     id="move_list",
        #     on_click=go_pass,
        # ),
        # Button(
        #     text=Const("Поделиться списком"),
        #     id="list_share",
        #     on_click=go_pass,
        # ),
        SwitchTo(
            text=Const("Удалить список"),
            id="delete_list",
            state=ListsManagementDialogSG.delete_list_window,
            when="is_empty_list"
        ),
        Start(
            text=Const("➕ Новая задача"),
            id="create_task",
            state=CreateTaskDialogSG.input_task_window,
        ),
        SwitchTo(
            text=Const("🔙 Назад"),
            id="back",
            state=ListsManagementDialogSG.main_lists_window,
        ),
        getter=get_tasks,
        state=ListsManagementDialogSG.list_with_tasks
    ),
    WindowWithoutInput(
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
                state=ListsManagementDialogSG.list_with_tasks
            ),
        ),
        getter=get_list_title_to_delete,
        state=ListsManagementDialogSG.delete_list_window,
    ),
    on_process_result=update_dialog_data_from_result,
)
