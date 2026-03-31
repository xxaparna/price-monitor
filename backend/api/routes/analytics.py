from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from backend.database import get_db
from backend.models import Product
from backend.api.middleware import require_api_key
from backend.api.schemas import AnalyticsOut, SourceStat, CategoryStat

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("", response_model=AnalyticsOut)
async def get_analytics(
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_api_key),
):
    # Total products
    total_result = await db.execute(select(func.count(Product.id)))
    total_products = total_result.scalar() or 0

    # Stats by source
    source_result = await db.execute(
        select(
            Product.source,
            func.count(Product.id).label("total_products"),
            func.avg(Product.current_price).label("avg_price"),
            func.min(Product.current_price).label("min_price"),
            func.max(Product.current_price).label("max_price"),
        ).group_by(Product.source)
    )
    by_source = [
        SourceStat(
            source=row.source,
            total_products=row.total_products,
            avg_price=round(row.avg_price, 2) if row.avg_price else None,
            min_price=row.min_price,
            max_price=row.max_price,
        )
        for row in source_result.all()
    ]

    # Stats by category
    category_result = await db.execute(
        select(
            Product.category,
            func.count(Product.id).label("total_products"),
            func.avg(Product.current_price).label("avg_price"),
        )
        .where(Product.category.isnot(None))
        .group_by(Product.category)
        .order_by(func.count(Product.id).desc())
    )
    by_category = [
        CategoryStat(
            category=row.category,
            total_products=row.total_products,
            avg_price=round(row.avg_price, 2) if row.avg_price else None,
        )
        for row in category_result.all()
    ]

    return AnalyticsOut(
        total_products=total_products,
        total_sources=len(by_source),
        by_source=by_source,
        by_category=by_category,
    )