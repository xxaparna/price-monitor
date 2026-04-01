from fastapi import Header, HTTPException, Depends
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from backend.models import ApiKey
from backend.database import get_db
from datetime import datetime

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def require_api_key(
    api_key: str = Depends(api_key_header),
    db: AsyncSession = Depends(get_db),
) -> ApiKey:
   
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing API key. Pass it as X-API-Key header.",
        )

    result = await db.execute(
        select(ApiKey).where(
            ApiKey.key == api_key,
            ApiKey.is_active == True,
        )
    )
    key_obj: ApiKey | None = result.scalar_one_or_none()

    if not key_obj:
        raise HTTPException(
            status_code=401,
            detail="Invalid or inactive API key.",
        )

    
    await db.execute(
        update(ApiKey)
        .where(ApiKey.id == key_obj.id)
        .values(
            usage_count=ApiKey.usage_count + 1,
            last_used_at=datetime.utcnow(),
        )
    )
    await db.commit()

    return key_obj