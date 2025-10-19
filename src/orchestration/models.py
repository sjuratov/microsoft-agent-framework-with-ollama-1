"""Data models for the slogan generation system."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class CompletionReason(str, Enum):
    """Reasons for session completion."""

    APPROVED = "approved"  # Reviewer approved with "SHIP IT!"
    MAX_TURNS = "max_turns"  # Reached maximum turn limit
    ERROR = "error"  # Error occurred


class AgentRole(str, Enum):
    """Agent roles in the system."""

    WRITER = "writer"
    REVIEWER = "reviewer"


class Turn(BaseModel):
    """Represents one iteration turn in the Writer-Reviewer cycle."""

    turn_number: int = Field(..., ge=1, le=10, description="Turn sequence number")
    slogan: str = Field(..., min_length=1, max_length=500, description="Generated slogan")
    feedback: str | None = Field(None, max_length=1000, description="Reviewer feedback")
    approved: bool = Field(default=False, description="Approval status")
    timestamp: datetime = Field(default_factory=datetime.now, description="Turn creation time")

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "turn_number": 1,
                "slogan": "Eco-Smart: Where Green Meets Hydration",
                "feedback": "Good start, but focus more on the 'fun' aspect mentioned in the brief.",
                "approved": False,
                "timestamp": "2025-10-19T14:30:00",
            }
        }


class IterationSession(BaseModel):
    """Complete iteration session with all turns."""

    user_input: str = Field(..., min_length=1, max_length=1000)
    model_name: str = Field(..., min_length=1)
    turns: list[Turn] = Field(default_factory=list, max_length=10)
    final_slogan: str | None = None
    completed: bool = False
    completion_reason: CompletionReason | None = None
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: datetime | None = None

    @field_validator("turns")
    @classmethod
    def validate_turn_order(cls, turns: list[Turn]) -> list[Turn]:
        """Ensure turns are in sequential order."""
        for i, turn in enumerate(turns, start=1):
            if turn.turn_number != i:
                raise ValueError(f"Turn {i} has incorrect turn_number: {turn.turn_number}")
        return turns

    @field_validator("completed")
    @classmethod
    def validate_completion(cls, completed: bool, info: Any) -> bool:
        """Ensure completed sessions have required fields."""
        if completed:
            if not info.data.get("final_slogan"):
                raise ValueError("Completed session must have final_slogan")
            if not info.data.get("completion_reason"):
                raise ValueError("Completed session must have completion_reason")
        return completed

    def add_turn(self, slogan: str, feedback: str | None = None, approved: bool = False) -> Turn:
        """Add a new turn to the session."""
        turn = Turn(
            turn_number=len(self.turns) + 1,
            slogan=slogan,
            feedback=feedback,
            approved=approved,
        )
        self.turns.append(turn)
        return turn

    def complete(self, reason: CompletionReason) -> None:
        """Mark session as complete."""
        self.completed = True
        self.completion_reason = reason
        self.completed_at = datetime.now()
        self.final_slogan = self.turns[-1].slogan if self.turns else None


class WorkflowMessage(BaseModel):
    """Message exchanged between agents."""

    from_agent: AgentRole
    to_agent: AgentRole
    content: str = Field(..., min_length=1)
    turn_number: int = Field(..., ge=1, le=10)
    metadata: dict[str, Any] = Field(default_factory=dict)
