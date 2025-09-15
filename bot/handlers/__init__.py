from aiogram import Router

from .basic import router, menu_task_dialog


def get_routers() -> list[Router]:
    return [
        router,
        menu_task_dialog
    ]
