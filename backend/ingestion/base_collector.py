import asyncio
import json
import glob
import os
from abc import ABC, abstractmethod
from typing import Any
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models import Product, PriceHistory, PriceEvent
from backend.database import AsyncSessionLocal
import uuid
from datetime import datetime


class BaseCollector(ABC):
    

    source_name: str = ""
    data_folder: str = "sample_products"

    def get_files(self) -> list[str]:
        
        pattern = os.path.join(self.data_folder, f"{self.source_name}_*.json")
        files = glob.glob(pattern)
        return files

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    )
    async def load_file(self, filepath: str) -> dict[str, Any]:
        
        await asyncio.sleep(0)   
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    @abstractmethod
    def normalize(self, raw: dict[str, Any]) -> dict[str, Any]:
        pass

    async def collect(self) -> dict[str, int]:
        
        files = self.get_files()
        if not files:
            print(f"[{self.source_name}] No files found.")
            return {"source": self.source_name, "processed": 0, "new": 0, "updated": 0, "errors": 0}

        results = {"source": self.source_name, "processed": 0, "new": 0, "updated": 0, "errors": 0}

        async with AsyncSessionLocal() as session:
            for filepath in files:
                try:
                    raw = await self.load_file(filepath)
                    normalized = self.normalize(raw)
                    outcome = await self.upsert_product(session, normalized)
                    results["processed"] += 1
                    results[outcome] += 1
                except Exception as e:
                    print(f"[{self.source_name}] Error processing {filepath}: {e}")
                    results["errors"] += 1

        print(f"[{self.source_name}] Done: {results}")
        return results

    async def upsert_product(self, session: AsyncSession, data: dict[str, Any]) -> str:
        
        stmt = select(Product).where(
            Product.source == data["source"],
            Product.external_id == data["external_id"],
        )
        result = await session.execute(stmt)
        existing: Product | None = result.scalar_one_or_none()

        if existing is None:
            
            product = Product(
                id=str(uuid.uuid4()),
                **data,
            )
            session.add(product)
            await session.flush()

           
            history = PriceHistory(
                id=str(uuid.uuid4()),
                product_id=product.id,
                price=product.current_price,
                currency=product.currency,
                price_delta=0.0,
                recorded_at=datetime.utcnow(),
            )
            session.add(history)
            await session.commit()
            return "new"

        else:
            old_price = existing.current_price
            new_price = data.get("current_price")

            
            for key, value in data.items():
                setattr(existing, key, value)
            existing.updated_at = datetime.utcnow()

            
            if new_price is not None and old_price != new_price:
                delta = round(new_price - (old_price or 0), 2)

                history = PriceHistory(
                    id=str(uuid.uuid4()),
                    product_id=existing.id,
                    price=new_price,
                    currency=existing.currency,
                    price_delta=delta,
                    recorded_at=datetime.utcnow(),
                )
                session.add(history)

                event = PriceEvent(
                    id=str(uuid.uuid4()),
                    product_id=existing.id,
                    old_price=old_price,
                    new_price=new_price,
                    price_delta=delta,
                    source=existing.source,
                    is_delivered=False,
                    delivery_attempts=0,
                )
                session.add(event)

            await session.commit()
            return "updated"