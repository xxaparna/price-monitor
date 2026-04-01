from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.database import init_db
from backend.config import get_settings
from backend.api.routes import products, analytics, refresh, notifications

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
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
    allow_origins=[
        "http://localhost:5173",
        "https://price-monitor-2qso.vercel.app",
        "https://price-monitor-nu.vercel.app",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(products.router)
app.include_router(analytics.router)
app.include_router(refresh.router)
app.include_router(notifications.router)


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
    }
