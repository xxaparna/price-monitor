from typing import Any
from backend.ingestion.base_collector import BaseCollector


class FashionphileCollector(BaseCollector):
    source_name = "fashionphile"

    def normalize(self, raw: dict[str, Any]) -> dict[str, Any]:
        metadata = raw.get("metadata", {})
        images = raw.get("main_images", [])
        image_url = images[0]["url"] if images else raw.get("image_url")

        
        size_dim = metadata.get("size_dimensions", {}) or {}
        description = metadata.get("description") or None

        return {
            "external_id": raw.get("product_id", ""),
            "source": self.source_name,
            "brand": raw.get("brand", "").title(),
            "model": raw.get("model", ""),
            "category": metadata.get("garment_type") or "Jewelry",
            "current_price": float(raw["price"]) if raw.get("price") is not None else None,
            "currency": raw.get("currency", "USD"),
            "condition": raw.get("condition"),
            "product_url": raw.get("product_url"),
            "image_url": image_url,
            "is_sold": False,
            "seller_location": metadata.get("pickup_location"),
            "description": description,
        }