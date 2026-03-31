from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime


# ── Product schemas ──────────────────────────────────────────────

class PriceHistoryOut(BaseModel):
    id: str
    price: float
    currency: str
    price_delta: Optional[float]
    recorded_at: datetime

    model_config = {"from_attributes": True}


class ProductOut(BaseModel):
    id: str
    external_id: str
    source: str
    brand: Optional[str]
    model: Optional[str]
    category: Optional[str]
    current_price: Optional[float]
    currency: str
    condition: Optional[str]
    product_url: Optional[str]
    image_url: Optional[str]
    is_sold: bool
    seller_location: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProductDetailOut(ProductOut):
    description: Optional[str]
    price_history: list[PriceHistoryOut] = []


# ── Analytics schemas ────────────────────────────────────────────

class SourceStat(BaseModel):
    source: str
    total_products: int
    avg_price: Optional[float]
    min_price: Optional[float]
    max_price: Optional[float]


class CategoryStat(BaseModel):
    category: str
    total_products: int
    avg_price: Optional[float]


class AnalyticsOut(BaseModel):
    total_products: int
    total_sources: int
    by_source: list[SourceStat]
    by_category: list[CategoryStat]


# ── Refresh schemas ──────────────────────────────────────────────

class RefreshOut(BaseModel):
    status: str
    results: list[dict]
    total_processed: int
    total_new: int
    total_updated: int
    total_errors: int


# ── Notification schemas ─────────────────────────────────────────

class WebhookCreate(BaseModel):
    url: str
    owner: str
    secret: Optional[str] = None


class WebhookOut(BaseModel):
    id: str
    url: str
    owner: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class PriceEventOut(BaseModel):
    id: str
    product_id: str
    old_price: Optional[float]
    new_price: float
    price_delta: Optional[float]
    source: str
    is_delivered: bool
    delivery_attempts: int
    is_dead_letter: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ── API Key schemas ──────────────────────────────────────────────

class ApiKeyCreate(BaseModel):
    owner: str


class ApiKeyOut(BaseModel):
    id: str
    key: str
    owner: str
    usage_count: int
    created_at: datetime

    model_config = {"from_attributes": True}