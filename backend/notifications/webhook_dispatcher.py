import aiohttp
import asyncio
from sqlalchemy import select, update
from backend.database import AsyncSessionLocal
from backend.models import PriceEvent, WebhookSubscription
from backend.config import get_settings
from datetime import datetime

settings = get_settings()


async def dispatch_pending_events() -> None:
    
    async with AsyncSessionLocal() as session:
       
        events_result = await session.execute(
            select(PriceEvent).where(
                PriceEvent.is_delivered == False,
                PriceEvent.is_dead_letter == False,
                PriceEvent.delivery_attempts < settings.webhook_max_retries,
            )
        )
        events = events_result.scalars().all()

        if not events:
            return

        
        webhooks_result = await session.execute(
            select(WebhookSubscription).where(WebhookSubscription.is_active == True)
        )
        webhooks = webhooks_result.scalars().all()

        if not webhooks:
            print("[Dispatcher] No active webhooks registered.")
            return

        async with aiohttp.ClientSession() as http:
            for event in events:
                payload = {
                    "event_id": event.id,
                    "product_id": event.product_id,
                    "source": event.source,
                    "old_price": event.old_price,
                    "new_price": event.new_price,
                    "price_delta": event.price_delta,
                    "timestamp": event.created_at.isoformat(),
                }

                delivered = False
                for attempt in range(1, settings.webhook_max_retries + 1):
                    try:
                        async with http.post(
                            webhooks[0].url,
                            json=payload,
                            timeout=aiohttp.ClientTimeout(total=5),
                        ) as resp:
                            if resp.status < 400:
                                delivered = True
                                break
                    except Exception as e:
                        print(f"[Dispatcher] Attempt {attempt} failed: {e}")
                        await asyncio.sleep(settings.webhook_retry_delay ** attempt)

                
                await session.execute(
                    update(PriceEvent)
                    .where(PriceEvent.id == event.id)
                    .values(
                        is_delivered=delivered,
                        delivery_attempts=PriceEvent.delivery_attempts + 1,
                        is_dead_letter=not delivered,
                        delivered_at=datetime.utcnow() if delivered else None,
                    )
                )

        await session.commit()
        print(f"[Dispatcher] Processed {len(events)} events.")