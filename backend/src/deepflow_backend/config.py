"""
DeepFlow Backend Configuration

Manages environment variables with Pydantic Settings.
"""

from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Supabase (optional for local development without auth)
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""

    # Upstash Redis (connection URL for standard Redis)
    upstash_redis_url: str = "redis://localhost:6379"
    
    # Upstash Redis REST API (for SSE pub/sub)
    upstash_redis_rest_url: str = ""
    upstash_redis_rest_token: str = ""

    # JWT
    jwt_secret: str = "dev-secret-change-in-production"

    # App
    app_env: str = "development"
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def is_configured(self) -> bool:
        """Check if required services are configured."""
        return bool(self.supabase_url and self.supabase_anon_key)

    @property
    def is_redis_rest_configured(self) -> bool:
        """Check if Redis REST API is configured for SSE."""
        return bool(self.upstash_redis_rest_url and self.upstash_redis_rest_token)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

