"""Pydantic request models for API endpoints."""

from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    """Request schema for slogan generation endpoint."""

    input: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Product/topic description for slogan generation"
    )
    model: str | None = Field(
        default=None,
        description="Ollama model name (optional, uses default if not specified)"
    )
    max_turns: int | None = Field(
        default=None,
        ge=1,
        le=10,
        description="Maximum iteration turns (optional)"
    )
    verbose: bool = Field(
        default=False,
        description="Include all iteration turns in response (optional)"
    )
