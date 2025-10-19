# Data Model - Slogan Writer-Reviewer Agent System

**Feature**: 001-slogan-writer-reviewer  
**Date**: 2025-10-19  
**Status**: Complete

## Overview

This document defines the data structures for the iterative slogan generation system. All models use Pydantic for validation and type safety, aligning with the Code Quality principle.

## Core Entities

### 1. Turn

Represents a single iteration in the Writer-Reviewer collaboration.

**Purpose**: Track each cycle of slogan generation and feedback.

**Fields**:

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| turn_number | int | Sequence number (1-5) | >= 1, <= 5 |
| slogan | str | Writer's generated slogan | min_length=1, max_length=500 |
| feedback | str \| None | Reviewer's feedback or approval | Optional, max_length=1000 |
| approved | bool | Whether reviewer approved | Default: False |
| timestamp | datetime | When turn was created | Auto-generated |

**Relationships**:

- Belongs to one IterationSession
- Precedes/follows other Turns in sequence

**State Transitions**:

```text
Created → Slogan Generated → Feedback Received → [Approved/Not Approved]
```

**Pydantic Model**:

```python
from datetime import datetime
from pydantic import BaseModel, Field

class Turn(BaseModel):
    """Represents one iteration turn in the Writer-Reviewer cycle."""
    
    turn_number: int = Field(..., ge=1, le=5, description="Turn sequence number")
    slogan: str = Field(..., min_length=1, max_length=500, description="Generated slogan")
    feedback: str | None = Field(None, max_length=1000, description="Reviewer feedback")
    approved: bool = Field(default=False, description="Approval status")
    timestamp: datetime = Field(default_factory=datetime.now, description="Turn creation time")
    
    class Config:
        json_schema_extra = {
            "example": {
                "turn_number": 1,
                "slogan": "Eco-Smart: Where Green Meets Hydration",
                "feedback": "Good start, but focus more on the 'fun' aspect mentioned in the brief.",
                "approved": False,
                "timestamp": "2025-10-19T14:30:00"
            }
        }
```

### 2. IterationSession

Represents the complete multi-turn collaboration session.

**Purpose**: Aggregate all turns and track overall session state.

**Fields**:

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| user_input | str | Original user request | min_length=1, max_length=1000 |
| model_name | str | Ollama model used | non-empty |
| turns | list[Turn] | All iteration turns | max_length=5 |
| final_slogan | str \| None | Approved or last slogan | Optional |
| completed | bool | Session completion status | Default: False |
| completion_reason | CompletionReason \| None | Why session ended | Optional |
| started_at | datetime | Session start time | Auto-generated |
| completed_at | datetime \| None | Session end time | Optional |

**Validation Rules**:

- Must have at least 1 turn when completed
- If completed=True, must have final_slogan and completion_reason
- turns list must be ordered by turn_number
- Max 5 turns enforced

**Pydantic Model**:

```python
from enum import Enum
from pydantic import BaseModel, Field, field_validator

class CompletionReason(str, Enum):
    """Reasons for session completion."""
    APPROVED = "approved"  # Reviewer approved with "SHIP IT!"
    MAX_TURNS = "max_turns"  # Reached 5-turn limit
    ERROR = "error"  # Error occurred
    
class IterationSession(BaseModel):
    """Complete iteration session with all turns."""
    
    user_input: str = Field(..., min_length=1, max_length=1000)
    model_name: str = Field(..., min_length=1)
    turns: list[Turn] = Field(default_factory=list, max_length=5)
    final_slogan: str | None = None
    completed: bool = False
    completion_reason: CompletionReason | None = None
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: datetime | None = None
    
    @field_validator('turns')
    @classmethod
    def validate_turn_order(cls, turns: list[Turn]) -> list[Turn]:
        """Ensure turns are in sequential order."""
        for i, turn in enumerate(turns, start=1):
            if turn.turn_number != i:
                raise ValueError(f"Turn {i} has incorrect turn_number: {turn.turn_number}")
        return turns
    
    @field_validator('completed')
    @classmethod
    def validate_completion(cls, completed: bool, info) -> bool:
        """Ensure completed sessions have required fields."""
        if completed:
            if not info.data.get('final_slogan'):
                raise ValueError("Completed session must have final_slogan")
            if not info.data.get('completion_reason'):
                raise ValueError("Completed session must have completion_reason")
        return completed
    
    def add_turn(self, slogan: str, feedback: str | None = None, approved: bool = False) -> Turn:
        """Add a new turn to the session."""
        turn = Turn(
            turn_number=len(self.turns) + 1,
            slogan=slogan,
            feedback=feedback,
            approved=approved
        )
        self.turns.append(turn)
        return turn
    
    def complete(self, reason: CompletionReason) -> None:
        """Mark session as complete."""
        self.completed = True
        self.completion_reason = reason
        self.completed_at = datetime.now()
        self.final_slogan = self.turns[-1].slogan if self.turns else None
```

### 3. OllamaConfig

Configuration for Ollama connection and model settings.

**Purpose**: Type-safe configuration management.

**Fields**:

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| base_url | str | Ollama API endpoint | `http://localhost:11434/v1` |
| model_name | str | Model to use | llama2 |
| max_iterations | int | Maximum turns | 5 |
| temperature | float | Model creativity | 0.7 |
| timeout | int | Request timeout (seconds) | 120 |

**Pydantic Model**:

```python
from pydantic_settings import BaseSettings

class OllamaConfig(BaseSettings):
    """Configuration for Ollama integration."""
    
    base_url: str = Field(
        default="http://localhost:11434/v1",
        description="Ollama API endpoint"
    )
    model_name: str = Field(
        default="llama2",
        description="Ollama model name"
    )
    max_iterations: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Maximum iteration turns"
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Model creativity level"
    )
    timeout: int = Field(
        default=120,
        ge=10,
        description="Request timeout in seconds"
    )
    
    class Config:
        env_prefix = "SLOGAN_"  # Enables SLOGAN_MODEL_NAME env var
        case_sensitive = False
```

### 4. AgentRole

Enum for agent identification.

**Purpose**: Type-safe agent role references.

```python
from enum import Enum

class AgentRole(str, Enum):
    """Agent roles in the system."""
    WRITER = "writer"
    REVIEWER = "reviewer"
```

### 5. WorkflowMessage

Message passed between agents in workflow.

**Purpose**: Standardize inter-agent communication.

**Fields**:

| Field | Type | Description |
|-------|------|-------------|
| from_agent | AgentRole | Sender agent |
| to_agent | AgentRole | Recipient agent |
| content | str | Message content |
| turn_number | int | Current turn |
| metadata | dict[str, Any] | Additional context |

**Pydantic Model**:

```python
from typing import Any
from pydantic import BaseModel, Field

class WorkflowMessage(BaseModel):
    """Message exchanged between agents."""
    
    from_agent: AgentRole
    to_agent: AgentRole
    content: str = Field(..., min_length=1)
    turn_number: int = Field(..., ge=1, le=5)
    metadata: dict[str, Any] = Field(default_factory=dict)
```

## Data Flow Diagram

```text
User Input
    ↓
IterationSession (created)
    ↓
┌─────────────────────────────────┐
│  Iteration Loop (max 5)         │
│                                  │
│  Writer Agent                    │
│    ↓                            │
│  Turn (slogan generated)         │
│    ↓                            │
│  Reviewer Agent                  │
│    ↓                            │
│  Turn (feedback added)           │
│    ↓                            │
│  [Approved?] → Yes: Exit loop    │
│              → No: Continue     │
└─────────────────────────────────┘
    ↓
IterationSession (completed)
    ↓
Final Output (CLI/API)
```

## Validation Examples

### Valid Session

```python
session = IterationSession(
    user_input="Create a slogan for eco-friendly water bottle",
    model_name="llama2"
)

# Add first turn
session.add_turn(
    slogan="Hydrate Green, Live Clean",
    feedback="Good, but emphasize the 'fun' aspect more",
    approved=False
)

# Add second turn with approval
session.add_turn(
    slogan="Sip Smart, Play Green!",
    feedback="SHIP IT! Perfect blend of eco and fun",
    approved=True
)

# Complete session
session.complete(CompletionReason.APPROVED)
```

### Invalid Session (catches error)

```python
# This will raise ValidationError
session = IterationSession(
    user_input="",  # ❌ Empty input not allowed
    model_name="llama2"
)

# This will raise ValidationError
session.completed = True  # ❌ Can't complete without final_slogan
```

## Entity Relationships

```text
IterationSession (1) ──< (1..5) Turn
IterationSession (1) ──< (1) OllamaConfig
Turn (n) ──> (n) WorkflowMessage
```

## Persistence (Future Consideration)

For MVP (P1): No persistence required (stateless sessions).

For future iterations:

- SQLite for local storage
- JSON export for portability
- Session history and analytics

Keeping models as Pydantic classes enables easy serialization when persistence is added.

## Summary

All data models follow:

- **Code Quality**: Type hints, validation, clear documentation
- **Simplicity**: Minimal fields, clear relationships, no over-abstraction
- **Testability**: Pydantic models are easy to instantiate and validate in tests

Models are ready for implementation in Phase 2 (Tasks).
