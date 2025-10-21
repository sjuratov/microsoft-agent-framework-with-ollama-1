"""FastAPI application initialization and configuration."""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.schemas.responses import RootResponse
from src.api.routes import health, models, generate

app = FastAPI(
    title="Slogan Writer-Reviewer API",
    version="1.0.0",
    description="Multi-agent slogan generation via Writer-Reviewer collaboration",
)

# Configure CORS
cors_origins = os.getenv(
    "API_CORS_ORIGINS", 
    "http://localhost:3000,http://localhost:8080"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
