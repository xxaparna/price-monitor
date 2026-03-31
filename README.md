# Price Monitor

A product price monitoring system that tracks pricing across **Grailed**, **Fashionphile**, and **1stdibs**. Detects price changes in real time, stores history, exposes a REST API, and notifies consumers via webhooks.

**Stack:** FastAPI · SQLAlchemy (async) · SQLite · React + Vite · pytest

---

## Setup & Run

**Requirements:** Python 3.9+, Node.js 18+
```bash
# 1. Clone
git clone https://github.com/xxaparna/price-monitor.git
cd price-monitor

# 2. Backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 3. Load sample data
python run_collectors.py

# 4. Start backend
uvicorn backend.main:app --reload
# → http://127.0.0.1:8000
# → http://127.0.0.1:8000/docs  (Swagger UI)

# 5. Start frontend (new terminal)
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

---

## Authentication

All endpoints except `/health` require:
```
X-API-Key: admin-key-123
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | System status |
| GET | `/products` | List products with filters |
| GET | `/products/{id}` | Product detail + price history |
| GET | `/analytics` | Aggregates by source and category |
| POST | `/refresh` | Trigger data collection from all sources |
| GET | `/events` | Price change event log |
| POST | `/webhooks` | Register a webhook URL |
| GET | `/webhooks` | List active webhooks |
| POST | `/api-keys` | Create a new API key |

### Filtering products
```
GET /products?source=grailed&min_price=100&max_price=500&sort_by=price&order=asc&page=1
```

### Example response — GET /analytics
```json
{
  "total_products": 90,
  "total_sources": 3,
  "by_source": [
    {"source": "1stdibs", "total_products": 30, "avg_price": 4032.85}
  ],
  "by_category": [
    {"category": "jewelry", "total_products": 30, "avg_price": 1950.33}
  ]
}
```

---

## Design Decisions

**Price history at scale**
New rows are only written when the price actually changes — not on every refresh. The `price_history` table has a compound index on `(product_id, recorded_at)` so per-product queries stay fast regardless of total row count. For PostgreSQL at millions of rows, I would add range partitioning by month and a retention policy for old records.

**Notifications**
I chose an event log + async background dispatcher over synchronous webhooks. Writing a `PriceEvent` row during ingestion is instant and non-blocking. After refresh completes, a `BackgroundTask` dispatches to registered webhook URLs with 3 retries and exponential backoff. Events that exhaust retries are flagged `is_dead_letter` — nothing is silently lost. Consumers can also poll `GET /events` if they prefer pull over push.

**Adding new data sources**
Every collector extends `BaseCollector` and implements one method — `normalize()`. Adding a source means creating one file, implementing normalize, and adding it to `ALL_COLLECTORS`. The API, database, and notification system require zero changes.

---

## Testing
```bash
pytest tests/ -v
# 22 passed — collectors, API auth, filters, edge cases, notification logic
```

---

## Known Limitations

- Collectors read local JSON files instead of live HTTP calls. The `aiohttp` + `tenacity` retry wiring is in place for real fetches.
- SQLite is used for simplicity. Switching to PostgreSQL requires only changing `DATABASE_URL` in `.env`.
- Refresh is triggered manually. Production would add APScheduler for periodic collection.
- Webhook dispatcher fans out to one URL currently. Production would use `asyncio.gather()` for all active subscribers.


