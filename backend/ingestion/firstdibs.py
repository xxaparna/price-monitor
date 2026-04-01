from typing import Any
from backend.ingestion.base_collector import BaseCollector


class FirstDibsCollector(BaseCollector):
    source_name = "1stdibs"

    def normalize(self, raw: dict[str, Any]) -> dict[str, Any]:
        metadata = raw.get("metadata", {})
        images = raw.get("main_images", [])
        image_url = images[0]["url"] if images else raw.get("image_url")

        
        price = raw.get("price")
        if price is None:
            all_prices = metadata.get("all_prices", {}) or {}
            price = all_prices.get("USD") or all_prices.get("usd")

        availability = metadata.get("availability", "")
        is_sold = availability.lower() not in ("in stock", "") if availability else False

        return {
            "external_id": raw.get("product_id", ""),
            "source": self.source_name,
            "brand": raw.get("brand", "").title(),
            "model": raw.get("model", ""),
            "category": raw.get("category") or metadata.get("category") or "Luxury",
            "current_price": float(price) if price is not None else None,
            "currency": "USD",
            "condition": metadata.get("condition_display") or metadata.get("condition"),
            "product_url": raw.get("product_url"),
            "image_url": image_url,
            "is_sold": is_sold,
            "seller_location": raw.get("seller_location") or metadata.get("seller_location"),
            "description": raw.get("full_description"),
        }