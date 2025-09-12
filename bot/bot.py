import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config_data.config import Config

logger = logging.getLogger(__name__)


async def main(config: Config):
    logger.info("Starting bot...")
    bot = Bot(
        token=config.bot_settings.token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    logger.info("Including routers...")
    # dp.include_routers(*get_routers)
    logger.info("Including middlewares...")
    # dp.update.middleware(SomeMiddleware)
    try:
        await dp.start_polling(
            bot,
            owner_id=config.bot_settings.owner_id.get_secret_value()
        )
    except Exception as e:
        logger.exception(e)
