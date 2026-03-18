from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
    )

    google_api_key: str = ""
    reddit_user_agent: str = "ecommerce_product_spotter/1.0 (Public API Fetcher)"
    gemini_model: str = "gemini-2.0-flash"
    gemini_model_pro: str = "gemini-2.5-flash"
    database_url: str = "sqlite+aiosqlite:///./data/analyses.db"
    cors_origins: list[str] = ["http://localhost:3000"]
    max_concurrent_analyses: int = 3
    environment: Literal["development", "staging", "production"] = "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()
