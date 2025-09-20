from aiogram import Router

from .basic import router
from ..flows.start.dialog import start_dialog
from ..flows.add_task.dialog import add_task_dialog


def get_routers() -> list[Router]:
    return [
        router,
        start_dialog,
        add_task_dialog,
    ]
