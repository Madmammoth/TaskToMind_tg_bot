import asyncio
import logging

from aiogram import BaseMiddleware
from sqlalchemy import update, func

from database.models import User

logger = logging.getLogger(__name__)


class LastActiveMiddleware(BaseMiddleware):
    def __init__(self, session_pool, redis_client,
                 interval_sec: int = 3600):
        self.session_pool = session_pool
        self.redis = redis_client
        self.interval = interval_sec

    async def __call__(self, handler, event, data):
        user = data.get("event_from_user")
        if not user:
            return await handler(event, data)

        user_id = user.id
        redis_key = f"user:{user_id}:last_active"
        last_update = await self.redis.get(redis_key)

        if not last_update:
            asyncio.create_task(self._update_last_active(user_id))
            await self.redis.set(
                redis_key, "1", ex=self.interval)
            logger.debug(
                "last_active обновлён для пользователя id=%d", user_id
            )

        return await handler(event, data)

    async def _update_last_active(self, user_id: int):
        async with self.session_pool() as session:
            try:
                await session.execute(
                    update(User)
                    .where(User.telegram_id == user_id)
                    .values(last_active=func.now())
                )
                await session.commit()
            except Exception as e:
                logger.exception(
                    "Ошибка обновления last_active "
                    "для пользователя id=%d: %s",
                    user_id, e,
                )
