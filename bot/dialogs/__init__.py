__all__ = ["dialogs"]

from .create_list.dialog import create_list_dialog
from .create_task.dialog import create_task_dialog
from .lists_managment.dialog import lists_management_dialog
from .start.dialog import start_dialog, help_dialog, predict_dialog
from .task_actions.dialog import task_actions_dialog
from .tasks_management.dialog import tasks_management_dialog
from .testing.dialog import test_dialog

dialogs = [
    start_dialog,
    help_dialog,
    predict_dialog,
    create_task_dialog,
    create_list_dialog,
    test_dialog,
    lists_management_dialog,
    tasks_management_dialog,
    task_actions_dialog,
]
