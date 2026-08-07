"""Application settings using Pydantic Settings."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application configuration.

    Values are loaded from environment variables and optional .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="Astra-Invest", description="Application name")
    app_env: Literal["development", "staging", "production"] = Field(
        default="development", description="Runtime environment"
    )
    app_debug: bool = Field(default=False, description="Enable debug mode")
    app_version: str = Field(default="0.1.0", description="Application version")
    secret_key: str = Field(
        default="change-me-in-production-please-use-a-long-random-string",
        description="Secret key for signing tokens and sessions",
    )

    # Server
    host: str = Field(default="0.0.0.0", description="Bind host")
    port: int = Field(default=8000, description="Bind port")
    workers: int = Field(default=1, description="Number of worker processes")
    reload: bool = Field(default=False, description="Enable auto-reload (dev only)")

    # Database
    postgres_host: str = Field(default="localhost", description="PostgreSQL host")
    postgres_port: int = Field(default=5432, description="PostgreSQL port")
    postgres_user: str = Field(default="astra", description="PostgreSQL user")
    postgres_password: str = Field(default="astra_dev_password", description="PostgreSQL password")
    postgres_db: str = Field(default="astra_invest", description="PostgreSQL database name")
    database_url: PostgresDsn | None = Field(
        default=None, description="Full database URL (overrides individual settings)"
    )

    # Redis
    redis_host: str = Field(default="localhost", description="Redis host")
    redis_port: int = Field(default=6379, description="Redis port")
    redis_db: int = Field(default=0, description="Redis database index")
    redis_url: RedisDsn | None = Field(
        default=None, description="Full Redis URL (overrides individual settings)"
    )

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", description="Logging level"
    )
    log_format: Literal["json", "console"] = Field(
        default="json", description="Log output format"
    )

    # CORS
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://127.0.0.1:3000"],
        description="Allowed CORS origins",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            import json

            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return [str(item) for item in parsed]
            except json.JSONDecodeError:
                return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v  # type: ignore[return-value]

    @property
    def is_development(self) -> bool:
        """Return True when running in development mode."""
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        """Return True when running in production mode."""
        return self.app_env == "production"

    def get_database_url(self) -> str:
        """Return the effective database URL."""
        if self.database_url:
            return str(self.database_url)
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    def get_redis_url(self) -> str:
        """Return the effective Redis URL."""
        if self.redis_url:
            return str(self.redis_url)
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance.

    Using lru_cache ensures we only parse environment variables once.
    """
    return Settings()
