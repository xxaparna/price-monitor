from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text
from backend.models import Base, ApiKey
from backend.config import get_settings
import uuid

settings = get_settings()

# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=False,          # set True temporarily if you want to see SQL queries
    future=True,
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Create all tables and seed the admin API key."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed default admin key so the API works immediately on first run
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("SELECT id FROM api_keys WHERE owner = 'admin' LIMIT 1")
        )
        existing = result.fetchone()
        if not existing:
            admin_key = ApiKey(
                id=str(uuid.uuid4()),
                key=settings.admin_api_key,
                owner="admin",
                is_active=True,
                usage_count=0,
            )
            session.add(admin_key)
            await session.commit()
            print(f"[DB] Admin API key seeded: {settings.admin_api_key}")
        else:
            print("[DB] Admin API key already exists")


async def get_db() -> AsyncSession:
    """FastAPI dependency — yields a DB session per request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()