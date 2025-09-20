from aiogram.fsm.state import StatesGroup, State


class StartSG(StatesGroup):
    start_window = State()


class GetTaskDialogSG(StatesGroup):
    tasks_window = State()
    create_task_window = State()
    cancel_window = State()


class ChangeSettingsDialogSG(StatesGroup):
    settings_window = State()