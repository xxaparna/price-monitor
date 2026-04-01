import pytest
from backend.ingestion.grailed import GrailedCollector
from backend.ingestion.fashionphile import FashionphileCollector
from backend.ingestion.firstdibs import FirstDibsCollector


def test_grailed_normalize_basic():
    raw = {
        "product_id": "abc-123",
        "brand": "amiri",
        "model": "Amiri T-Shirt",
        "price": 425.0,
        "product_url": "https://grailed.com/listings/123",
        "image_url": "https://example.com/img.jpg",
        "main_images": [],
        "metadata": {
            "is_sold": False,
            "style": "Street",
            "full_product_description": "A nice shirt",
        },
    }
    result = GrailedCollector().normalize(raw)
    assert result["external_id"] == "abc-123"
    assert result["source"] == "grailed"
    assert result["brand"] == "Amiri"
    assert result["current_price"] == 425.0
    assert result["is_sold"] is False
    assert result["category"] == "Street"


def test_grailed_normalize_sold():
    raw = {
        "product_id": "sold-999",
        "brand": "amiri",
        "model": "Sold Shirt",
        "price": 100.0,
        "product_url": "https://grailed.com/listings/999",
        "image_url": "",
        "main_images": [],
        "metadata": {"is_sold": True, "style": None, "full_product_description": ""},
    }
    result = GrailedCollector().normalize(raw)
    assert result["is_sold"] is True
    assert result["category"] == "Apparel"


def test_grailed_normalize_uses_first_image():
    raw = {
        "product_id": "img-test",
        "brand": "amiri",
        "model": "Image Test",
        "price": 200.0,
        "product_url": "https://grailed.com/listings/img",
        "image_url": "fallback.jpg",
        "main_images": [
            {"url": "https://first-image.jpg", "format": "image/jpeg", "metadata": {}},
            {"url": "https://second-image.jpg", "format": "image/jpeg", "metadata": {}},
        ],
        "metadata": {"is_sold": False, "style": "Casual", "full_product_description": ""},
    }
    result = GrailedCollector().normalize(raw)
    assert result["image_url"] == "https://first-image.jpg"




def test_fashionphile_normalize_basic():
    raw = {
        "product_id": "fp-456",
        "brand": "Tiffany",
        "model": "Diamond Necklace",
        "price": 2435.0,
        "currency": "USD",
        "condition": "Excellent",
        "product_url": "https://fashionphile.com/products/123",
        "image_url": "https://example.com/fp.jpg",
        "main_images": [],
        "metadata": {
            "garment_type": "jewelry",
            "description": "Beautiful necklace",
            "sku": "1802360",
        },
    }
    result = FashionphileCollector().normalize(raw)
    assert result["external_id"] == "fp-456"
    assert result["source"] == "fashionphile"
    assert result["current_price"] == 2435.0
    assert result["condition"] == "Excellent"
    assert result["category"] == "jewelry"
    assert result["currency"] == "USD"


def test_fashionphile_normalize_missing_price():
    raw = {
        "product_id": "fp-no-price",
        "brand": "Tiffany",
        "model": "Unknown Item",
        "price": None,
        "currency": "USD",
        "condition": "Good",
        "product_url": "https://fashionphile.com/products/000",
        "image_url": "",
        "main_images": [],
        "metadata": {"garment_type": "jewelry", "description": None, "sku": "000"},
    }
    result = FashionphileCollector().normalize(raw)
    assert result["current_price"] is None




def test_firstdibs_normalize_basic():
    raw = {
        "product_id": "fd-789",
        "brand": "Chanel",
        "model": "Chanel Belt 1994",
        "price": 7550.0,
        "product_url": "https://1stdibs.com/fashion/belts/123",
        "category": "1990s Belts",
        "seller_location": "Paris, FR",
        "full_description": "Authentic Chanel belt",
        "main_images": [],
        "metadata": {
            "condition_display": "Excellent",
            "availability": "In Stock",
            "seller_location": "Paris, FR",
        },
    }
    result = FirstDibsCollector().normalize(raw)
    assert result["external_id"] == "fd-789"
    assert result["source"] == "1stdibs"
    assert result["current_price"] == 7550.0
    assert result["condition"] == "Excellent"
    assert result["is_sold"] is False
    assert result["seller_location"] == "Paris, FR"


def test_firstdibs_normalize_sold():
    raw = {
        "product_id": "fd-sold",
        "brand": "Chanel",
        "model": "Sold Belt",
        "price": 5000.0,
        "product_url": "https://1stdibs.com/fashion/belts/sold",
        "category": "Luxury",
        "seller_location": "NYC, US",
        "full_description": None,
        "main_images": [],
        "metadata": {
            "condition_display": "Good",
            "availability": "sold",
            "seller_location": "NYC, US",
        },
    }
    result = FirstDibsCollector().normalize(raw)
    assert result["is_sold"] is True


def test_firstdibs_normalize_uses_all_prices_fallback():
    raw = {
        "product_id": "fd-fallback",
        "brand": "Chanel",
        "model": "Price Fallback Test",
        "price": None,
        "product_url": "https://1stdibs.com/fashion/belts/fallback",
        "category": "Luxury",
        "seller_location": "London, GB",
        "full_description": None,
        "main_images": [],
        "metadata": {
            "condition_display": "Good",
            "availability": "In Stock",
            "all_prices": {"USD": 3000.0},
            "seller_location": "London, GB",
        },
    }
    result = FirstDibsCollector().normalize(raw)
    assert result["current_price"] == 3000.0