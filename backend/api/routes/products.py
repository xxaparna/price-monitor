from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from backend.database import get_db
from backend.models import Product, PriceHistory
from backend.api.middleware import require_api_key
from backend.api.schemas import ProductOut, ProductDetailOut
from typing import Optional

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=list[ProductOut])
async def list_products(
    source: Optional[str] = Query(None, description="Filter by source: grailed, fashionphile, 1stdibs"),
    category: Optional[str] = Query(None, description="Filter by category"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    min_price: Optional[float] = Query(None, description="Minimum price"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    is_sold: Optional[bool] = Query(None, description="Filter sold items"),
    sort_by: str = Query("updated_at", description="Sort by: price, updated_at, brand"),
    order: str = Query("desc", description="asc or desc"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_api_key),
):
    stmt = select(Product)

    if source:
        stmt = stmt.where(Product.source == source.lower())
    if category:
        stmt = stmt.where(Product.category.ilike(f"%{category}%"))
    if brand:
        stmt = stmt.where(Product.brand.ilike(f"%{brand}%"))
    if min_price is not None:
        stmt = stmt.where(Product.current_price >= min_price)
    if max_price is not None:
        stmt = stmt.where(Product.current_price <= max_price)
    if is_sold is not None:
        stmt = stmt.where(Product.is_sold == is_sold)

    # Sorting
    sort_col = getattr(Product, sort_by, Product.updated_at)
    if order == "asc":
        stmt = stmt.order_by(sort_col.asc())
    else:
        stmt = stmt.order_by(sort_col.desc())

    # Pagination
    offset = (page - 1) * page_size
    stmt = stmt.offset(offset).limit(page_size)

    result = await db.execute(stmt)
    products = result.scalars().all()
    return products


@router.get("/{product_id}", response_model=ProductDetailOut)
async def get_product(
    product_id: str,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_api_key),
):
    stmt = (
        select(Product)
        .where(Product.id == product_id)
        .options(selectinload(Product.price_history))
    )
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    # Sort history by recorded_at ascending for chart display
    product.price_history.sort(key=lambda h: h.recorded_at)
    return product