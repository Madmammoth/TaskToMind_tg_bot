from aiogram import Router

from .basic import router, add_task_dialog, start_dialog


def get_routers() -> list[Router]:
    return [
        router,
        start_dialog,
        add_task_dialog,
    ]
