from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./price_monitor.db"
    api_secret_key: str = "super-secret-key-change-in-production"
    admin_api_key: str = "admin-key-123"
    app_name: str = "Price Monitor"
    app_version: str = "1.0.0"
    webhook_max_retries: int = 3
    webhook_retry_delay: float = 2.0

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()