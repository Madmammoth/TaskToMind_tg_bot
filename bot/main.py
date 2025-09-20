import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram_dialog import setup_dialogs

from bot.dialogs import dialogs
from bot.handlers import routers
from config_data.config import Config, load_config

config: Config = load_config()

logging.basicConfig(
    level=logging.getLevelName(level=config.log_settings.level),
    format=config.log_settings.format,
)

logger = logging.getLogger(__name__)


async def main():
    logger.info("Starting bot...")
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
    # dp.update.middleware(SomeMiddleware)
    try:
        await dp.start_polling(
            bot,
            owner_id=config.bot_settings.owner_id.get_secret_value()
        )
    except Exception as e:
        logger.exception(e)


asyncio.run(main())
