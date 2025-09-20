__all__ = ["routers"]

from .commands import commands_router
from .others import others_router
from .task_messages import task_messages_router

routers = [
    commands_router,
    task_messages_router,
    others_router,
]
