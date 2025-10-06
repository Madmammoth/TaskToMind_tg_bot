import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram_dialog import setup_dialogs
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from bot.dialogs import dialogs
from bot.handlers import routers
from config_data.config import Config, load_config
from database.middlewares import DbSessionMiddleware

config: Config = load_config()

logging.basicConfig(
    level=logging.getLevelName(level=config.log_settings.level),
    format=config.log_settings.format,
)

logger = logging.getLogger(__name__)

if sys.platform.startswith("win") or os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def main():
    logger.info("Starting bot...")
    dsn = config.db_settings.get_dsn()
    engine = create_async_engine(
        url=dsn,
        echo=True,
    )

    bot = Bot(
        token=config.bot_settings.token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    logger.info("Including routers...")
    dp.include_routers(*routers)
    dp.include_routers(*dialogs)
    setup_dialogs(dp)
    logger.info("Including middlewares...")
    Sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    dp.update.middleware(DbSessionMiddleware(Sessionmaker))
    try:
        await dp.start_polling(
            bot,
            owner_id=config.bot_settings.owner_id.get_secret_value()
        )
    except Exception as e:
        logger.exception(e)


asyncio.run(main())
