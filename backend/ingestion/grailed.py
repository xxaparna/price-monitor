from typing import Any
from backend.ingestion.base_collector import BaseCollector


class GrailedCollector(BaseCollector):
    source_name = "grailed"

    def normalize(self, raw: dict[str, Any]) -> dict[str, Any]:
        metadata = raw.get("metadata", {})
        images = raw.get("main_images", [])
        image_url = images[0]["url"] if images else raw.get("image_url")

        return {
            "external_id": raw.get("product_id", ""),
            "source": self.source_name,
            "brand": raw.get("brand", "").title(),
            "model": raw.get("model", ""),
            "category": metadata.get("style") or "Apparel",
            "current_price": float(raw["price"]) if raw.get("price") is not None else None,
            "currency": "USD",
            "condition": None,                          # Grailed doesn't provide condition
            "product_url": raw.get("product_url"),
            "image_url": image_url,
            "is_sold": bool(metadata.get("is_sold", False)),
            "seller_location": None,
            "description": metadata.get("full_product_description") or None,
        }