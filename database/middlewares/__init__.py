__all__ = ["middlewares"]

from database.middlewares.db_session import DbSessionMiddleware

middlewares = [
    DbSessionMiddleware,
]
