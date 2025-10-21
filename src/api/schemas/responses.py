"""Pydantic response models for API endpoints."""

from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field
from uuid import UUID


class DependencyStatus(BaseModel):
    """Status of a single dependency."""

    connected: bool = Field(..., description="Connection status")
    url: str = Field(..., description="Dependency URL")
    response_time_ms: int | None = Field(
        default=None, ge=0, description="Response time (if connected)"
    )
    error: str | None = Field(default=None, description="Error message (if not connected)")


class HealthResponse(BaseModel):
    """Response schema for health check."""

    status: Literal["healthy", "degraded"] = Field(
        ..., description="Overall health status"
    )
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(..., description="Health check timestamp")
    dependencies: dict[str, DependencyStatus] = Field(
        ..., description="Dependency statuses"
    )


class RootResponse(BaseModel):
    """Response schema for root endpoint."""

    name: str = Field(..., description="API name")
    version: str = Field(..., description="API version (semver)")
    description: str = Field(..., description="API description")
    documentation: dict[str, str] = Field(..., description="Documentation links")
