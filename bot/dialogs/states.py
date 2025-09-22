from aiogram.fsm.state import StatesGroup, State


class StartSG(StatesGroup):
    start_window = State()
    input_task_window = State()


class GetTaskDialogSG(StatesGroup):
    tasks_window = State()
    add_task_window = State()
    add_task_window_2 = State()
    cancel_window = State()


class ChangeSettingsDialogSG(StatesGroup):
    settings_window = State()
