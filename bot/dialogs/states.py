from aiogram.fsm.state import StatesGroup, State


class GetTaskDialogSG(StatesGroup):
    menu_window = State()
