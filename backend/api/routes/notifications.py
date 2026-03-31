from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.database import get_db
from backend.models import PriceEvent, WebhookSubscription
from backend.api.middleware import require_api_key
from backend.api.schemas import (
    PriceEventOut, WebhookCreate, WebhookOut, ApiKeyCreate, ApiKeyOut
)
from backend.notifications.event_publisher import get_recent_events
import uuid
from datetime import datetime

router = APIRouter(tags=["Notifications & Keys"])


@router.get("/events", response_model=list[PriceEventOut])
async def list_events(
    limit: int = Query(50, ge=1, le=200),
    undelivered_only: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_api_key),
):
    """Returns the price change event log."""
    events = await get_recent_events(db, limit=limit, undelivered_only=undelivered_only)
    return events


@router.post("/webhooks", response_model=WebhookOut)
async def register_webhook(
    payload: WebhookCreate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_api_key),
):
    """Register a webhook URL to receive price change notifications."""
    webhook = WebhookSubscription(
        id=str(uuid.uuid4()),
        url=payload.url,
        owner=payload.owner,
        secret=payload.secret,
        is_active=True,
        created_at=datetime.utcnow(),
    )
    db.add(webhook)
    await db.commit()
    return webhook


@router.get("/webhooks", response_model=list[WebhookOut])
async def list_webhooks(
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_api_key),
):
    result = await db.execute(
        select(WebhookSubscription).where(WebhookSubscription.is_active == True)
    )
    return result.scalars().all()


@router.post("/api-keys", response_model=ApiKeyOut)
async def create_api_key(
    payload: ApiKeyCreate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_api_key),
):
    """Create a new API key for a consumer."""
    from backend.models import ApiKey
    new_key = ApiKey(
        id=str(uuid.uuid4()),
        key=str(uuid.uuid4()),
        owner=payload.owner,
        is_active=True,
        usage_count=0,
        created_at=datetime.utcnow(),
    )
    db.add(new_key)
    await db.commit()
    return new_key