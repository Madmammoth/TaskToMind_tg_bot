from aiogram.fsm.state import StatesGroup, State


class StartSG(StatesGroup):
    start_window = State()


class HelpSG(StatesGroup):
    help_window = State()


class PredictSG(StatesGroup):
    predict_window = State()


class CreateTaskDialogSG(StatesGroup):
    input_task_window = State()
    tasks_window = State()
    add_task_window = State()
    add_task_window_2 = State()
    select_list_window = State()
    task_priority_window = State()
    task_urgency_window = State()
    save_task_window = State()
    cancel_window = State()


class TaskActionsDialogSG(StatesGroup):
    main_task_window = State()
    main_task_window_2 = State()
    share_task_window = State()
    checklist_window = State()
    complete_task_window = State()
    not_complete_task_window = State()
    cancel_task_window = State()
    not_cancel_task_window = State()
    select_list_window = State()
    task_priority_window = State()
    task_urgency_window = State()
    repeat_task_window = State()
    task_remind_window = State()
    task_duration_window = State()
    task_deadline_window = State()
    task_recurrence_window = State()


class TasksManagementDialogSG(StatesGroup):
    main_tasks_window = State()
    trash_window = State()
    archive_window = State()


class CreateListDialogSG(StatesGroup):
    input_list_title_window = State()
    add_list_window = State()
    in_list_window = State()
    cancel_window = State()


class ListsManagementDialogSG(StatesGroup):
    main_lists_window = State()
    rename_new_list_window = State()
    save_list_window = State()
    list_with_tasks = State()
    rename_list_window = State()
    move_list_window = State()
    delete_list_window = State()
    change_view_window = State()


class ChangeSettingsDialogSG(StatesGroup):
    settings_window = State()


class ForTestsDialogSG(StatesGroup):
    test_window = State()
    main = State()
    result = State()
