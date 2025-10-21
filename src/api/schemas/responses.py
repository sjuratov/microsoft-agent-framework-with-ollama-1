"""Pydantic response models for API endpoints."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


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


class ModelInfo(BaseModel):
    """Information about an available model."""

    name: str = Field(..., description="Model name")
    display_name: str = Field(..., description="Human-readable model name")


class ModelsResponse(BaseModel):
    """Response schema for models endpoint."""

    models: list[ModelInfo] = Field(..., description="List of available models")
    default_model: str = Field(..., description="The default model name")
    count: int = Field(..., ge=0, description="Total number of available models")


class TurnDetail(BaseModel):
    """Details of a single iteration turn (for verbose mode)."""

    turn_number: int = Field(..., ge=1, description="Iteration number (1-indexed)")
    slogan: str = Field(..., description="Slogan proposed in this turn")
    feedback: str | None = Field(default=None, description="Reviewer feedback (null if approved)")
    approved: bool = Field(..., description="Whether slogan was approved")
    timestamp: datetime = Field(..., description="Turn timestamp")


class GenerateResponse(BaseModel):
    """Response schema for slogan generation endpoint."""

    slogan: str = Field(..., description="Final approved slogan")
    input: str = Field(..., description="Original user input")
    completion_reason: Literal["approved", "max_turns", "error"] = Field(
        ..., description="Reason for generation completion"
    )
    turn_count: int = Field(..., ge=1, description="Number of iterations performed")
    model_name: str = Field(..., description="Model used for generation")
    total_duration_seconds: float = Field(..., ge=0, description="Total generation time in seconds")
    average_duration_per_turn: float = Field(..., ge=0, description="Average time per iteration")
    turns: list[TurnDetail] | None = Field(
        default=None, description="Iteration history (only if verbose=true)"
    )
    created_at: datetime = Field(..., description="Request timestamp")
    request_id: UUID | None = Field(default=None, description="Request identifier (UUID v4)")


class QueuedResponse(BaseModel):
    """Response schema for queued requests (202 Accepted)."""

    request_id: UUID = Field(..., description="Request identifier for tracking")
    status: Literal["queued"] = Field(..., description="Request status")
    estimated_wait_seconds: int = Field(..., ge=0, description="Estimated wait time")
    message: str = Field(..., description="Human-readable status message")
