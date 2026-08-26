"""Application configuration using Pydantic Settings."""

import json
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    DATABASE_URL: str
    APP_NAME: str = "Task Management API"
    DEBUG: bool = False
    CORS_ORIGINS: str = '["http://localhost:3000"]'
    API_PREFIX: str = "/api"

    @property
    def cors_origins_list(self) -> list[str]:
        val = self.CORS_ORIGINS.strip()
        if not val or val == "*":
            return ["*"]
        try:
            parsed = json.loads(val)
            if isinstance(parsed, list):
                return parsed
        except Exception:
            pass
        return [item.strip() for item in val.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
