from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config.settings import config

dsn = config.pg_settings.get_dsn()
engine = create_async_engine(url=dsn, echo=True)

session_maker = async_sessionmaker(engine, expire_on_commit=False)
