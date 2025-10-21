"""Health check endpoint."""

from datetime import UTC, datetime

import httpx
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from src.api.schemas.responses import DependencyStatus, HealthResponse

router = APIRouter(prefix="/api/v1", tags=["monitoring"])


@router.get("/health")
async def get_health() -> JSONResponse:
    """Check API and dependency health status."""
    # Check Ollama connectivity
    ollama_url = "http://localhost:11434"
    ollama_status = await check_ollama_health(ollama_url)

    health_data = HealthResponse(
        status="healthy" if ollama_status.connected else "degraded",
        version="1.0.0",
        timestamp=datetime.now(UTC),
        dependencies={"ollama": ollama_status},
    )

    status_code = (
        status.HTTP_200_OK
        if health_data.status == "healthy"
        else status.HTTP_503_SERVICE_UNAVAILABLE
    )

    return JSONResponse(
        status_code=status_code,
        content=health_data.model_dump(mode="json"),
    )


async def check_ollama_health(base_url: str) -> DependencyStatus:
    """Check if Ollama is responsive."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            start = datetime.now()
            response = await client.get(f"{base_url}/api/tags")
            elapsed_ms = int((datetime.now() - start).total_seconds() * 1000)

            if response.status_code == 200:
                return DependencyStatus(
                    connected=True,
                    url=base_url,
                    response_time_ms=elapsed_ms,
                )
            else:
                return DependencyStatus(
                    connected=False,
                    url=base_url,
                    error=f"HTTP {response.status_code}",
                )
    except Exception as e:
        return DependencyStatus(
            connected=False,
            url=base_url,
            error=str(e),
        )
