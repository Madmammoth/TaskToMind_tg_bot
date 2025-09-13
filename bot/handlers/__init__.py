from aiogram import Router

from bot.handlers import basic


def get_routers() -> list[Router]:
    return [
        basic.router,
    ]
