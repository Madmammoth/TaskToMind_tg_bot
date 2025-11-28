from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import ScrollingGroup
from aiogram_dialog.widgets.text import Const

from app.bot.dialogs.states import ForTestsDialogSG
from app.bot.dialogs.testing.handlers import test_buttons

test_dialog = Dialog(
    Window(
        Const("Click find products to show a list of available products:"),
        ScrollingGroup(
            *test_buttons,
            id="numbers",
            width=6,
            height=6,
        ),
        state=ForTestsDialogSG.test_window,
    ),
)
