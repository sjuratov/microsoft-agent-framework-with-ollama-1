"""Configuration management for the slogan generation system."""

import os
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class OllamaConfig(BaseSettings):
    """Ollama configuration from environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="OLLAMA_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    base_url: str = Field(
        default="http://localhost:11434/v1",
        description="Ollama API base URL",
    )
    model_name: str = Field(
        default="llama3.2:latest",
        description="Default model name",
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Sampling temperature",
    )
    max_tokens: int = Field(
        default=500,
        ge=1,
        le=4096,
        description="Maximum tokens per generation",
    )
    timeout: int = Field(
        default=30,
        ge=1,
        le=300,
        description="Request timeout in seconds",
    )
    max_turns: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Maximum iteration turns",
    )


@lru_cache
def get_ollama_config() -> OllamaConfig:
    """Get cached Ollama configuration instance."""
    return OllamaConfig()
