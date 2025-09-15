from aiogram import Router

from .basic import router, menu_task


def get_routers() -> list[Router]:
    return [
        router,
        menu_task,
    ]
