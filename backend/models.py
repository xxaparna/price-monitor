import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Float, Boolean, Integer,
    DateTime, ForeignKey, Text, UniqueConstraint, Index
)
from sqlalchemy.orm import DeclarativeBase, relationship


def generate_uuid() -> str:
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, default=generate_uuid)
    external_id = Column(String, nullable=False)
    source = Column(String, nullable=False)        # grailed | fashionphile | 1stdibs
    brand = Column(String, nullable=True)
    model = Column(String, nullable=True)
    category = Column(String, nullable=True)
    current_price = Column(Float, nullable=True)
    currency = Column(String, default="USD")
    condition = Column(String, nullable=True)
    product_url = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    is_sold = Column(Boolean, default=False)
    seller_location = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    price_history = relationship("PriceHistory", back_populates="product", cascade="all, delete-orphan")
    price_events = relationship("PriceEvent", back_populates="product", cascade="all, delete-orphan")

    # Same product can exist on multiple sources — unique per source+external_id
    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_source_external_id"),
    )

    def __repr__(self):
        return f"<Product {self.brand} {self.model} [{self.source}] ${self.current_price}>"


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(String, primary_key=True, default=generate_uuid)
    product_id = Column(String, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    price_delta = Column(Float, nullable=True)     # difference from previous price
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    product = relationship("Product", back_populates="price_history")

    # Critical for scale — millions of rows need this index to stay fast
    __table_args__ = (
        Index("ix_price_history_product_recorded", "product_id", "recorded_at"),
    )

    def __repr__(self):
        return f"<PriceHistory product={self.product_id} price={self.price} at={self.recorded_at}>"


class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(String, primary_key=True, default=generate_uuid)
    key = Column(String, unique=True, nullable=False)
    owner = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<ApiKey owner={self.owner} usage={self.usage_count}>"


class PriceEvent(Base):
    __tablename__ = "price_events"

    id = Column(String, primary_key=True, default=generate_uuid)
    product_id = Column(String, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    old_price = Column(Float, nullable=True)
    new_price = Column(Float, nullable=False)
    price_delta = Column(Float, nullable=True)
    source = Column(String, nullable=False)
    is_delivered = Column(Boolean, default=False)
    delivery_attempts = Column(Integer, default=0)
    is_dead_letter = Column(Boolean, default=False)   # gave up after max retries
    created_at = Column(DateTime, default=datetime.utcnow)
    delivered_at = Column(DateTime, nullable=True)

    product = relationship("Product", back_populates="price_events")

    def __repr__(self):
        return f"<PriceEvent product={self.product_id} {self.old_price}->{self.new_price}>"


class WebhookSubscription(Base):
    __tablename__ = "webhook_subscriptions"

    id = Column(String, primary_key=True, default=generate_uuid)
    url = Column(String, nullable=False)
    owner = Column(String, nullable=False)
    secret = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<WebhookSubscription url={self.url} owner={self.owner}>"