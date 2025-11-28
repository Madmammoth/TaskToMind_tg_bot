from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const


def test_buttons_creator(btn_quantity):
    buttons = []
    for i in btn_quantity:
        i = str(i)
        buttons.append(Button(Const(i), id=i))
    return buttons


test_buttons = test_buttons_creator(range(0, 30))
