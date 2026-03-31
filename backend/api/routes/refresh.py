from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_db
from backend.api.middleware import require_api_key
from backend.api.schemas import RefreshOut
from backend.ingestion import ALL_COLLECTORS
from backend.notifications.webhook_dispatcher import dispatch_pending_events

router = APIRouter(prefix="/refresh", tags=["Refresh"])


@router.post("", response_model=RefreshOut)
async def trigger_refresh(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_api_key),
):
    """
    Triggers data collection from all sources.
    After collecting, dispatches any pending price-change notifications
    as a background task so it doesn't block the response.
    """
    results = []
    for collector_class in ALL_COLLECTORS:
        collector = collector_class()
        result = await collector.collect()
        results.append(result)

    # Dispatch notifications without blocking the API response
    background_tasks.add_task(dispatch_pending_events)

    total_processed = sum(r["processed"] for r in results)
    total_new = sum(r["new"] for r in results)
    total_updated = sum(r["updated"] for r in results)
    total_errors = sum(r["errors"] for r in results)

    return RefreshOut(
        status="completed",
        results=results,
        total_processed=total_processed,
        total_new=total_new,
        total_updated=total_updated,
        total_errors=total_errors,
    )