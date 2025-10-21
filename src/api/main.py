"""FastAPI application initialization and configuration."""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.api.config import get_api_config
from src.api.exceptions import (
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from src.api.middleware import RequestLoggingMiddleware
from src.api.routes import generate, health, models
from src.api.schemas.responses import RootResponse

# Load configuration and setup logging
config = get_api_config()

app = FastAPI(
    title="Slogan Writer-Reviewer API",
    version="1.0.0",
    description="Multi-agent slogan generation via Writer-Reviewer collaboration",
)

# Configure CORS
# Note: When allow_credentials=True, we can't use allow_origins=["*"]
# Instead, use allow_origin_regex to match all origins
if config.cors_origins_list == ["*"]:
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex="https?://.*",  # Match any origin (http or https)
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Register exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(Exception, unhandled_exception_handler)

# Register routers
app.include_router(health.router)
app.include_router(models.router)
app.include_router(generate.router)


@app.get("/", response_model=RootResponse, tags=["info"])
def get_root() -> RootResponse:
    """Get API information and documentation links."""
    return RootResponse(
        name="Slogan Writer-Reviewer API",
        version="1.0.0",
        description="Multi-agent slogan generation via Writer-Reviewer collaboration",
        documentation={
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
        },
    )
