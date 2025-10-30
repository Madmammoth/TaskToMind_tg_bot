from aiogram.fsm.state import StatesGroup, State


class StartSG(StatesGroup):
    start_window = State()
    input_task_window = State()


class GetTaskDialogSG(StatesGroup):
    tasks_window = State()
    add_task_window = State()
    add_task_window_2 = State()
    select_list_window = State()
    task_priority_window = State()
    task_urgency_window = State()
    save_task_window = State()
    cancel_window = State()


class TaskManagementDialogSG(StatesGroup):
    main_tasks_window = State()


class TaskListsDialogSG(StatesGroup):
    main_lists_window = State()
    input_list_title_window = State()
    add_list_window = State()
    in_list_window = State()
    save_list_window = State()
    cancel_window = State()
    change_view_window = State()


class ChangeSettingsDialogSG(StatesGroup):
    settings_window = State()


class ForTestsDialogSG(StatesGroup):
    test_window = State()
    main = State()
    result = State()
