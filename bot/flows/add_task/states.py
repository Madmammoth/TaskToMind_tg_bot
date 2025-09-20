from aiogram.fsm.state import StatesGroup, State


class GetTaskDialogSG(StatesGroup):
    tasks_window = State()
    add_task_window = State()
    cancel_window = State()
