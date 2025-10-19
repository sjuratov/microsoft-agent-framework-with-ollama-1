"""Configuration package."""

from .settings import OllamaConfig, get_available_models, get_ollama_config

__all__ = [
    "OllamaConfig",
    "get_ollama_config",
    "get_available_models",
]
