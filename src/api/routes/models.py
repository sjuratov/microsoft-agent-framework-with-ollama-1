"""Models endpoint for listing available Ollama models."""

from fastapi import APIRouter, Depends, HTTPException

from src.api.dependencies import get_config
from src.api.schemas.responses import ModelInfo, ModelsResponse
from src.config.settings import OllamaConfig, get_available_models

router = APIRouter(prefix="/api/v1", tags=["models"])


@router.get("/models", response_model=ModelsResponse)
async def get_models(config: OllamaConfig = Depends(get_config)) -> ModelsResponse:
    """
    Get list of available Ollama models.
    
    Returns information about all models available on the Ollama instance,
    including the default model configured for the application.
    
    Args:
        config: Injected Ollama configuration
    
    Returns:
        ModelsResponse with list of models, default model, and count
    
    Raises:
        HTTPException: 503 if Ollama is unavailable
        HTTPException: 500 for other errors
    """
    try:
        # Get available models from Ollama API
        model_names = get_available_models(base_url=config.base_url, timeout=10)
        
        # Convert to ModelInfo objects with display names
        models = [
            ModelInfo(
                name=name,
                display_name=name.replace(":", " ").title()
            )
            for name in model_names
        ]
        
        return ModelsResponse(
            models=models,
            default_model=config.model_name,
            count=len(models)
        )
    
    except ConnectionError as e:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "service_unavailable",
                "message": str(e),
                "suggestion": "Ensure Ollama is running with 'ollama serve'"
            }
        ) from e
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": f"Failed to retrieve models: {str(e)}"
            }
        ) from e
