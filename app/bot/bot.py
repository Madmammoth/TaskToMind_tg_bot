import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage
from aiogram_dialog import setup_dialogs
from dishka import make_async_container
from dishka.integrations.aiogram import setup_dishka
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.bot.dialogs import dialogs
from app.bot.dialogs.id_uniqueness_validator import validate_dialogs
from app.bot.handlers import routers
from app.bot.handlers.others import others_router
from app.bot.middlewares.last_active import LastActiveMiddleware
from app.config_data.config import Config, load_config
from app.database.middlewares.db_session import DbSessionMiddleware
from app.di.providers import DbProvider

logger = logging.getLogger(__name__)

if sys.platform.startswith("win") or os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def main():
    logger.info("Starting bot...")

    config: Config = load_config()

    dsn = config.pg_settings.get_dsn()
    engine = create_async_engine(url=dsn, echo=True)

    bot = Bot(
        token=config.bot_settings.token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    redis_client = Redis(
        host=config.redis_settings.host,
        port=config.redis_settings.port,
        db=config.redis_settings.db,
        password=config.redis_settings.password.get_secret_value(),
        username=config.redis_settings.username,
    )
    key_builder = DefaultKeyBuilder(with_destiny=True)
    storage = RedisStorage(redis=redis_client, key_builder=key_builder)

    dp = Dispatcher(storage=storage)

    logger.info("Including routers...")
    dp.include_routers(*routers)
    validate_dialogs(dialogs)
    dp.include_routers(*dialogs)
    setup_dialogs(dp)
    dp.include_router(others_router)

    logger.info("Including middlewares...")
    session_maker = async_sessionmaker(engine, expire_on_commit=False)
    dp.update.middleware(DbSessionMiddleware(session_maker))
    dp.update.middleware(LastActiveMiddleware(session_maker, redis_client))

    container = make_async_container(
        DbProvider(),
    )
    setup_dishka(container, dp)

    try:
        await dp.start_polling(
            bot,
            owner_id=config.bot_settings.owner_id.get_secret_value()
        )
    except Exception as e:
        logger.exception(e)
    finally:
        await bot.session.close()
