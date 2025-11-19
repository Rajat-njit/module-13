# app/core/config.py dfg

from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    """
    Application settings read from environment variables.
    Works locally AND inside Docker containers.

    Priority:
    1. Environment variables (Docker / CI-CD)
    2. .env file (local development)
    3. Default values below
    """

    # ---------- Database ----------
    # If running in docker-compose, DATABASE_URL will be something like:
    # postgresql://postgres:postgres@db:5432/fastapi_db
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/fastapi_db"
    )

    # ---------- JWT Settings ----------
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-super-secret-key-change-this-in-production")
    JWT_REFRESH_SECRET_KEY: str = os.getenv("JWT_REFRESH_SECRET_KEY", "your-refresh-secret-key-change-this-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

    # ---------- Security ----------
    BCRYPT_ROUNDS: int = int(os.getenv("BCRYPT_ROUNDS", 12))

    # ---------- CORS ----------
    CORS_ORIGINS: List[str] = ["*"]

    # ---------- Redis (Optional) ----------
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
_settings = Settings()


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance."""
    return _settings


# For modules that import `settings` directly
settings: Settings = _settings
