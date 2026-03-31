from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models import PriceEvent


async def get_recent_events(
    db: AsyncSession,
    limit: int = 50,
    undelivered_only: bool = False,
) -> list[PriceEvent]:
    stmt = select(PriceEvent).order_by(PriceEvent.created_at.desc()).limit(limit)
    if undelivered_only:
        stmt = stmt.where(PriceEvent.is_delivered == False)
    result = await db.execute(stmt)
    return result.scalars().all()