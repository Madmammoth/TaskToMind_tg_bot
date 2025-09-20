__all__ = ["routers"]

from .commands import commands_router

routers = [
    commands_router,
]
