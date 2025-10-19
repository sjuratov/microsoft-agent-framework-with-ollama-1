"""Configuration management for the slogan generation system."""

import os
from functools import lru_cache

import httpx
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
        default="mistral:latest",
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


def get_available_models(base_url: str | None = None, timeout: int = 10) -> list[str]:
    """Query Ollama API for available models.
    
    Args:
        base_url: Ollama base URL (defaults to config)
        timeout: Request timeout in seconds
        
    Returns:
        List of available model names
        
    Raises:
        ConnectionError: If unable to connect to Ollama
        RuntimeError: If API request fails
    """
    if base_url is None:
        config = get_ollama_config()
        base_url = config.base_url
    
    # Convert OpenAI-compatible URL to Ollama API URL
    # e.g., http://localhost:11434/v1 -> http://localhost:11434
    ollama_base = base_url.rstrip("/").removesuffix("/v1")
    tags_url = f"{ollama_base}/api/tags"
    
    try:
        response = httpx.get(tags_url, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        
        # Extract model names from response
        models = data.get("models", [])
        return [model.get("name", "") for model in models if model.get("name")]
        
    except httpx.ConnectError as e:
        raise ConnectionError(
            f"Unable to connect to Ollama at {ollama_base}. "
            "Is Ollama running? Try: ollama serve"
        ) from e
    except httpx.TimeoutException as e:
        raise RuntimeError(f"Request to Ollama timed out after {timeout}s") from e
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"Ollama API error: {e.response.status_code}") from e
    except Exception as e:
        raise RuntimeError(f"Failed to fetch models: {e}") from e
