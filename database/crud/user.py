import logging

from sqlalchemy.dialects.postgresql import insert as upsert
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User, UserTag
from database.models.stats import UserStats

logger = logging.getLogger(__name__)


async def upsert_user_row(
        session: AsyncSession,
        telegram_id: int,
        first_name: str,
        last_name: str | None = None,
        username: str | None = None,
):
    stmt = upsert(User).values(
        telegram_id=telegram_id,
        first_name=first_name,
        last_name=last_name,
        username=username,
    ).on_conflict_do_update(
        index_elements=["telegram_id"],
        set_={
            "first_name": first_name,
            "last_name": last_name,
            "username": username,
        }
    ).returning(User)
    result = await session.execute(stmt)
    return result.scalar_one()


def create_user_stats(
        session: AsyncSession,
        telegram_id: int
):
    session.add(UserStats(user_id=telegram_id))


def assign_default_tags(
        session: AsyncSession,
        telegram_id: int
):
    session.add_all([
        UserTag(user_id=telegram_id, tag_id=tag_id)
        for tag_id in range(1, 14)
    ])
