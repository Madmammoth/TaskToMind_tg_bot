from typing import AsyncIterable

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config_data.config import Config, load_config
from app.database.orchestration.protocols import ApplyListSelection
from app.database.orchestration.task import apply_list_selection


class DbProvider(Provider):

    @provide(scope=Scope.APP)
    def engine(self) -> AsyncEngine:
        config: Config = load_config()
        dsn = config.pg_settings.get_dsn()
        return create_async_engine(
            dsn,
            echo=True,
        )

    @provide(scope=Scope.APP)
    def session_maker(
            self,
            engine: AsyncEngine,
    ) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(engine, expire_on_commit=False)

    @provide(scope=Scope.REQUEST)
    async def session(
            self,
            session_maker: async_sessionmaker[AsyncSession],
    ) -> AsyncIterable[AsyncSession]:
        async with session_maker() as session:
            yield session


class OrchestrationProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def apply_list_selection(self) -> ApplyListSelection:
        return apply_list_selection  # noqa
