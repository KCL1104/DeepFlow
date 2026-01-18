"""
DeepFlow Agent Configuration

Supports OpenAI-compatible API endpoints.
"""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Agent settings loaded from environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Allow extra env vars without error
    )

    # LLM - OpenAI Compatible
    openai_api_key: str = ""
    openai_api_base: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4-turbo"
    llm_temperature: float = 0.0

    # Opik
    opik_api_key: str = ""
    opik_project_name: str = "DeepFlow"
    opik_workspace: str = "default"

    # Upstash Redis (REST API)
    upstash_redis_rest_url: str = ""
    upstash_redis_rest_token: str = ""

    # Slack Integration
    slack_bot_token: str = ""
    slack_signing_secret: str = ""

    # Priority Weights
    priority_weight_urgency: float = 0.4
    priority_weight_deadline: float = 0.3
    priority_weight_wait_time: float = 0.2
    priority_weight_context: float = 0.1

    # State Thresholds
    flow_state_threshold: int = 9
    shallow_state_threshold: int = 6

    @property
    def is_opik_configured(self) -> bool:
        return bool(self.opik_api_key)

    @property
    def is_llm_configured(self) -> bool:
        return bool(self.openai_api_key)

    @property
    def is_redis_configured(self) -> bool:
        return bool(self.upstash_redis_rest_url and self.upstash_redis_rest_token)

    @property
    def is_slack_configured(self) -> bool:
        return bool(self.slack_bot_token)


@lru_cache
def get_settings() -> Settings:
    return Settings()

