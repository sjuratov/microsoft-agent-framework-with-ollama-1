"""
FastAPI dependency injection functions.

This module provides dependency injection functions for FastAPI endpoints,
allowing routes to access shared resources like configuration objects.
"""

from src.config.settings import OllamaConfig, get_ollama_config


def get_config() -> OllamaConfig:
    """
    Get the application configuration instance.
    
    This dependency can be injected into FastAPI route handlers to access
    the Ollama configuration object, which provides settings like base_url,
    model_name, temperature, etc.
    
    Returns:
        OllamaConfig: The Ollama configuration instance
    
    Example:
        @app.get("/example")
        def example_route(config: OllamaConfig = Depends(get_config)):
            base_url = config.base_url
            return {"base_url": base_url}
    """
    return get_ollama_config()
