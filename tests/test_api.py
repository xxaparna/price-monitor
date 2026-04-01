import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from backend.main import app
from backend.database import init_db


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    await init_db()


@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_products_requires_auth():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/products")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_products_with_auth():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/products", headers={"X-API-Key": "admin-key-123"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_analytics_with_auth():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/analytics", headers={"X-API-Key": "admin-key-123"})
    assert response.status_code == 200
    data = response.json()
    assert "total_products" in data
    assert "by_source" in data
    assert "by_category" in data


@pytest.mark.asyncio
async def test_analytics_invalid_key():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/analytics", headers={"X-API-Key": "wrong-key"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_product_not_found():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            "/products/nonexistent-id-000",
            headers={"X-API-Key": "admin-key-123"}
        )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_products_filter_by_source():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            "/products?source=grailed",
            headers={"X-API-Key": "admin-key-123"}
        )
    assert response.status_code == 200
    data = response.json()
    for product in data:
        assert product["source"] == "grailed"


@pytest.mark.asyncio
async def test_products_filter_by_price_range():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            "/products?min_price=100&max_price=1000",
            headers={"X-API-Key": "admin-key-123"}
        )
    assert response.status_code == 200
    data = response.json()
    for product in data:
        assert product["current_price"] is None or (
            100 <= product["current_price"] <= 1000
        )


@pytest.mark.asyncio
async def test_events_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/events", headers={"X-API-Key": "admin-key-123"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)