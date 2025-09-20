from aiogram import Router

from .basic import router, create_task_dialog, start_dialog


def get_routers() -> list[Router]:
    return [
        router,
        start_dialog,
        create_task_dialog,
    ]
