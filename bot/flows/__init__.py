__all__ = ["dialogs"]

from bot.flows.add_task.dialog import add_task_dialog
from bot.flows.start.dialog import start_dialog

dialogs = [
    start_dialog,
    add_task_dialog,
]
