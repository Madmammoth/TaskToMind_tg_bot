__all__ = ["dialogs"]

from .add_task.dialog import add_task_dialog
from .start.dialog import start_dialog
from .testing.dialog import test_dialog

dialogs = [
    start_dialog,
    add_task_dialog,
    test_dialog,
]
