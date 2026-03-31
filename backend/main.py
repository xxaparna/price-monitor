from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.database import init_db
from backend.config import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs on startup — creates tables and seeds admin key."""
    print("[Startup] Initializing database...")
    await init_db()
    print("[Startup] Database ready.")
    yield
    print("[Shutdown] Goodbye.")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Tracks product prices across Grailed, Fashionphile, and 1stdibs",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
    }