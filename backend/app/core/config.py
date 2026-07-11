import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    PORT: int = 8000
    HOST: str = "0.0.0.0"
    LOG_LEVEL: str = "INFO"

    # Database URLs
    DATABASE_URL: str = "sqlite:///./sentinel.db"
    ASYNC_DATABASE_URL: str = "sqlite+aiosqlite:///./sentinel.db"

    # Redis URL
    REDIS_URL: Optional[str] = None

    # Simulation Speed
    SIMULATION_SPEED_MULTIPLIER: float = 1.0


# Initialize Settings
settings = Settings()
