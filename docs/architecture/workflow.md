# Workflow Architecture

This document describes the orchestration system that coordinates the Writer-Reviewer agents through an iterative refinement loop.

## Overview

The workflow system implements a **managed iteration pattern** where:

1. **Writer** generates a slogan
2. **Reviewer** evaluates and provides feedback
3. **Orchestrator** decides whether to continue or complete
4. Process repeats until approval or max turns reached

### Core Responsibilities

| Component | Responsibility |
|-----------|---------------|
| **Orchestrator** | Manages agent lifecycle, iteration loop, state tracking |
| **Session Manager** | Maintains iteration history and session state |
| **Approval Checker** | Detects "SHIP IT!" approval signal |
| **Completion Handler** | Finalizes session with appropriate reason |

---

## Workflow State Machine

### States

```
┌──────────────┐
│ INITIALIZED  │
│  (Start)     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  GENERATING  │ ◄─────────┐
│  (Writer)    │           │
└──────┬───────┘           │
       │                   │
       ▼                   │
┌──────────────┐           │
│  REVIEWING   │           │
│ (Reviewer)   │           │
└──────┬───────┘           │
       │                   │
       ▼                   │
┌──────────────┐           │
│   DECIDING   │           │
│ (Check OK?)  │           │
└──────┬───────┘           │
       │                   │
       ├─ Approved ─────►┌─┴────────────┐
       │                 │  COMPLETED   │
       │                 │  (Success)   │
       │                 └──────────────┘
       │
       ├─ Not Approved ──┘ (feedback to Writer)
       │    + Turn < Max
       │
       └─ Max Turns ───►┌──────────────┐
                        │  COMPLETED   │
                        │ (Max Turns)  │
                        └──────────────┘
```

### State Transitions

| From State | Event | To State | Action |
|-----------|-------|----------|--------|
| INITIALIZED | Start | GENERATING | Create agents |
| GENERATING | Writer complete | REVIEWING | Pass slogan to reviewer |
| REVIEWING | Reviewer complete | DECIDING | Check approval |
| DECIDING | Approved | COMPLETED | Finalize session |
| DECIDING | Not approved + turns left | GENERATING | Pass feedback to writer |
| DECIDING | Max turns reached | COMPLETED | Finalize with max turns reason |

---

## Main Workflow Function

### `run_slogan_generation`

The primary orchestration function that manages the entire workflow.

```python
async def run_slogan_generation(
    user_input: str,
    model_name: str | None = None,
    max_turns: int | None = None,
) -> IterationSession:
    """
    Run the slogan generation workflow with iterative refinement.
    
    This function orchestrates the Writer-Reviewer collaboration:
    1. Initializes session and agents
    2. Runs iteration loop until approval or max turns
    3. Returns complete session with all turns
    
    Args:
        user_input: Product/service description
        model_name: LLM model to use (default from config)
        max_turns: Max iterations (default from config)
        
    Returns:
        IterationSession with final slogan and turn history
        
    Raises:
        ConfigurationError: If Ollama config invalid
        ModelNotFoundError: If specified model not available
        AgentError: If agent creation or execution fails
    """
```

### Implementation

```python
# Phase 1: Initialize
config = get_ollama_config()
if model_name:
    config.model_name = model_name
if max_turns:
    config.max_turns = max_turns

session = IterationSession(
    user_input=user_input,
    model_name=config.model_name,
    max_turns=config.max_turns,
)

# Phase 2: Create Agents
writer = await create_writer_agent(config)
reviewer = await create_reviewer_agent(config)

# Phase 3: Iteration Loop
feedback: str | None = None

for turn_number in range(1, config.max_turns + 1):
    # Step 1: Writer generates slogan
    writer_message = await writer.send_message(
        _create_writer_prompt(user_input, feedback)
    )
    slogan = writer_message.content.strip()
    
    # Step 2: Reviewer evaluates
    reviewer_message = await reviewer.send_message(
        _create_reviewer_prompt(slogan)
    )
    reviewer_feedback = reviewer_message.content.strip()
    
    # Step 3: Check approval
    approved = is_approved(reviewer_feedback)
    
    # Step 4: Record turn
    turn = Turn(
        turn_number=turn_number,
        slogan=slogan,
        feedback=None if approved else reviewer_feedback,
        approved=approved,
        timestamp=datetime.now(timezone.utc),
    )
    session.turns.append(turn)
    
    # Step 5: Decision
    if approved:
        session.final_slogan = slogan
        session.completion_reason = CompletionReason.APPROVED
        session.turn_count = turn_number
        session.completed_at = datetime.now(timezone.utc)
        return session
    
    # Prepare for next iteration
    feedback = reviewer_feedback

# Phase 4: Max turns reached
session.final_slogan = session.turns[-1].slogan
session.completion_reason = CompletionReason.MAX_TURNS
session.turn_count = config.max_turns
session.completed_at = datetime.now(timezone.utc)
return session
```

---

## Helper Functions

### Approval Detection

```python
def is_approved(feedback: str) -> bool:
    """
    Detect approval signal in reviewer feedback.
    
    Looks for the exact phrase "SHIP IT!" (case-insensitive).
    Uses word boundaries to avoid false positives.
    
    Args:
        feedback: Reviewer's response
        
    Returns:
        True if contains "SHIP IT!", False otherwise
        
    Examples:
        >>> is_approved("This is perfect! SHIP IT!")
        True
        >>> is_approved("This needs work on shipping logistics")
        False
    """
    normalized = feedback.upper().strip()
    return bool(re.search(r'\bSHIP IT!?\b', normalized))
```

**Design Considerations**:

- **Explicit Signal**: Clear, unambiguous approval phrase
- **Case Insensitive**: Handles "SHIP IT", "Ship It!", "ship it"
- **Word Boundaries**: `\b` prevents false matches (e.g., "relationship")
- **Optional Punctuation**: Matches "SHIP IT" or "SHIP IT!"

### Continuation Logic

```python
def should_continue_iteration(
    turn_number: int,
    max_turns: int,
    approved: bool,
) -> bool:
    """
    Determine if workflow should continue to next iteration.
    
    Args:
        turn_number: Current iteration number (1-based)
        max_turns: Maximum allowed iterations
        approved: Whether current slogan was approved
        
    Returns:
        True if should continue, False if should stop
    """
    if approved:
        return False  # Stop on approval
    
    if turn_number >= max_turns:
        return False  # Stop at max turns
    
    return True  # Continue otherwise
```

### Prompt Construction

```python
def _create_writer_prompt(
    user_input: str,
    feedback: str | None,
) -> str:
    """
    Build prompt for Writer agent.
    
    Args:
        user_input: Product/service description
        feedback: Previous reviewer feedback (None for first turn)
        
    Returns:
        Formatted prompt string
    """
    if feedback is None:
        # First turn: Just the product description
        return f"Create a slogan for: {user_input}"
    else:
        # Subsequent turns: Include feedback
        return (
            f"Create a slogan for: {user_input}\n\n"
            f"Previous feedback:\n{feedback}\n\n"
            f"Please improve based on the feedback."
        )


def _create_reviewer_prompt(slogan: str) -> str:
    """
    Build prompt for Reviewer agent.
    
    Args:
        slogan: Slogan to evaluate
        
    Returns:
        Formatted prompt string
    """
    return f"Please review this slogan: {slogan}"
```

---

## Data Models

### IterationSession

Complete record of a workflow execution.

```python
class IterationSession(BaseModel):
    """
    Complete session record for one workflow execution.
    
    Tracks all iterations, final result, and completion metadata.
    """
    
    # Input
    user_input: str
    model_name: str
    max_turns: int
    
    # Execution
    turns: list[Turn] = Field(default_factory=list)
    turn_count: int = 0
    
    # Result
    final_slogan: str | None = None
    completion_reason: CompletionReason | None = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    
    @property
    def duration(self) -> timedelta | None:
        """Calculate session duration."""
        if self.completed_at:
            return self.completed_at - self.created_at
        return None
    
    @property
    def succeeded(self) -> bool:
        """Check if session completed successfully (approved)."""
        return self.completion_reason == CompletionReason.APPROVED
```

### Turn

Single iteration in the workflow.

```python
class Turn(BaseModel):
    """
    Single Writer-Reviewer exchange.
    
    Represents one iteration in the refinement loop.
    """
    turn_number: int
    slogan: str
    feedback: str | None  # None if approved
    approved: bool
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

### CompletionReason

Why the workflow ended.

```python
class CompletionReason(str, Enum):
    """Reason for workflow completion."""
    
    APPROVED = "approved"        # Reviewer approved ("SHIP IT!")
    MAX_TURNS = "max_turns"      # Reached maximum iterations
    ERROR = "error"              # Encountered an error
    USER_CANCELLED = "cancelled" # User cancelled (future)
```

### AgentRole

Agent type identifier.

```python
class AgentRole(str, Enum):
    """Role of an agent in the workflow."""
    
    WRITER = "writer"
    REVIEWER = "reviewer"
```

---

## Workflow Patterns

### Happy Path (Approval)

```
Turn 1:
  User Input: "eco-friendly water bottles"
  Writer → "Hydrate Green, Live Clean"
  Reviewer → "Good rhythm but vague. Be specific about impact."
  Decision: Continue

Turn 2:
  User Input: "eco-friendly water bottles"
  Feedback: "Good rhythm but vague..."
  Writer → "Hydrate Green, Save Our Seas"
  Reviewer → "SHIP IT!"
  Decision: Complete (APPROVED)

Result: ✅ Success in 2 turns
```

### Max Turns Path

```
Turn 1-5:
  (Multiple iterations with feedback)
  
Turn 5:
  Writer → "Final slogan attempt"
  Reviewer → "Close but still needs work on X"
  Decision: Complete (MAX_TURNS)

Result: ⚠️ Reached limit without approval
```

### Error Path

```
Turn 1:
  Writer → ConnectionError (Ollama down)
  Decision: Complete (ERROR)

Result: ❌ Failed to complete
```

---

## Configuration

### Default Values

```python
# src/config/settings.py

DEFAULT_MODEL_NAME = "mistral:latest"
DEFAULT_MAX_TURNS = 5
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 100
DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_REQUEST_TIMEOUT = 30
```

### Environment Variables

```bash
# Workflow configuration
OLLAMA_MAX_TURNS=5           # Max iterations per session
OLLAMA_MODEL_NAME=mistral:latest  # Model to use
OLLAMA_TEMPERATURE=0.7       # Generation temperature

# Ollama connection
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_REQUEST_TIMEOUT=30
```

### Runtime Configuration

```python
# Override via function parameters
session = await run_slogan_generation(
    user_input="smart watches",
    model_name="llama3.2:latest",  # Override default
    max_turns=3,                   # Override default
)
```

---

## Error Handling

### Exception Hierarchy

```python
class WorkflowError(Exception):
    """Base exception for workflow errors."""
    pass

class AgentError(WorkflowError):
    """Error during agent creation or execution."""
    pass

class ApprovalTimeoutError(WorkflowError):
    """Max turns reached without approval."""
    pass

class ConfigurationError(WorkflowError):
    """Invalid configuration."""
    pass
```

### Error Recovery

```python
async def run_slogan_generation_with_retry(
    user_input: str,
    max_retries: int = 3,
) -> IterationSession:
    """
    Run workflow with automatic retry on failure.
    
    Retries on transient errors (network, timeout).
    Does not retry on validation or configuration errors.
    """
    for attempt in range(1, max_retries + 1):
        try:
            return await run_slogan_generation(user_input)
        except (ConnectionError, TimeoutError) as e:
            if attempt == max_retries:
                raise WorkflowError(f"Failed after {max_retries} attempts") from e
            
            wait_time = 2 ** attempt  # Exponential backoff
            await asyncio.sleep(wait_time)
            continue
        except (ConfigurationError, ValidationError):
            # Don't retry validation errors
            raise
```

---

## Performance Optimization

### Current Performance

| Metric | Value | Notes |
|--------|-------|-------|
| **Avg Turns** | 2-3 | Usually approved within 3 turns |
| **Avg Duration** | 10-15s | Per turn (model dependent) |
| **Success Rate** | ~85% | Percentage approved within max_turns |

### Optimization Strategies

#### 1. Early Stopping

```python
def should_stop_early(session: IterationSession) -> bool:
    """
    Detect convergence and stop early.
    
    If last 2 slogans are very similar, likely converged.
    """
    if len(session.turns) < 3:
        return False
    
    last_two = [t.slogan for t in session.turns[-2:]]
    similarity = calculate_similarity(last_two[0], last_two[1])
    
    return similarity > 0.95  # 95% similar
```

#### 2. Parallel Agent Calls (Future)

```python
# Current: Sequential
slogan = await writer.generate(...)
review = await reviewer.evaluate(slogan)

# Future: Parallel generation of multiple candidates
slogans = await asyncio.gather(
    writer.generate(input, feedback),
    writer.generate(input, feedback),  # Different seed
    writer.generate(input, feedback),
)
reviews = await asyncio.gather(*[
    reviewer.evaluate(s) for s in slogans
])
```

#### 3. Model Caching

```python
# Cache frequently used models
_model_cache: dict[str, Agent] = {}

async def get_cached_agent(
    role: AgentRole,
    config: OllamaConfig,
) -> Agent:
    """Get or create cached agent."""
    cache_key = f"{role}:{config.model_name}"
    
    if cache_key not in _model_cache:
        if role == AgentRole.WRITER:
            _model_cache[cache_key] = await create_writer_agent(config)
        else:
            _model_cache[cache_key] = await create_reviewer_agent(config)
    
    return _model_cache[cache_key]
```

---

## Monitoring and Observability

### Logging

```python
import logging

logger = logging.getLogger(__name__)

async def run_slogan_generation(
    user_input: str,
    model_name: str | None = None,
    max_turns: int | None = None,
) -> IterationSession:
    """Main workflow with comprehensive logging."""
    
    logger.info(
        "Starting workflow",
        extra={
            "user_input": user_input,
            "model_name": model_name or config.model_name,
            "max_turns": max_turns or config.max_turns,
        }
    )
    
    # ... workflow logic ...
    
    for turn_number in range(1, config.max_turns + 1):
        logger.debug(f"Starting turn {turn_number}")
        
        # Writer
        start_time = time.time()
        slogan = await writer.generate(...)
        writer_duration = time.time() - start_time
        logger.debug(
            f"Writer generated slogan",
            extra={"duration": writer_duration, "slogan": slogan}
        )
        
        # Reviewer
        start_time = time.time()
        review = await reviewer.evaluate(slogan)
        reviewer_duration = time.time() - start_time
        logger.debug(
            f"Reviewer provided feedback",
            extra={"duration": reviewer_duration, "approved": is_approved(review)}
        )
    
    logger.info(
        "Workflow completed",
        extra={
            "completion_reason": session.completion_reason,
            "turn_count": session.turn_count,
            "duration": session.duration.total_seconds(),
        }
    )
    
    return session
```

### Metrics (Future)

```python
# Prometheus metrics example
from prometheus_client import Counter, Histogram

workflow_runs = Counter(
    "workflow_runs_total",
    "Total workflow runs",
    ["completion_reason"]
)

workflow_duration = Histogram(
    "workflow_duration_seconds",
    "Workflow execution time"
)

turn_count = Histogram(
    "workflow_turns",
    "Number of turns per workflow"
)
```

---

## Testing Workflow

### Unit Tests

```python
# tests/unit/test_workflow.py

async def test_is_approved():
    """Test approval detection."""
    assert is_approved("SHIP IT!")
    assert is_approved("Perfect! SHIP IT! Great work.")
    assert not is_approved("This needs work on shipping")

async def test_should_continue():
    """Test continuation logic."""
    assert should_continue_iteration(1, 5, False)  # Turn 1, not approved
    assert not should_continue_iteration(1, 5, True)  # Approved
    assert not should_continue_iteration(5, 5, False)  # Max turns
```

### Integration Tests

```python
# tests/integration/test_workflow_integration.py

@pytest.mark.integration
async def test_full_workflow():
    """Test complete workflow with real agents."""
    session = await run_slogan_generation(
        "smart home devices",
        model_name="gemma2:2b",  # Fast model for testing
        max_turns=3,
    )
    
    assert session.final_slogan
    assert session.turn_count >= 1
    assert session.completion_reason in [
        CompletionReason.APPROVED,
        CompletionReason.MAX_TURNS,
    ]
    assert session.duration
    assert len(session.turns) == session.turn_count
```

---

## Workflow Diagram

### Complete Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     START WORKFLOW                          │
│  Input: user_input, model_name?, max_turns?                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  INITIALIZE SESSION                         │
│  - Load configuration                                       │
│  - Create IterationSession object                           │
│  - Apply overrides (model_name, max_turns)                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   CREATE AGENTS                             │
│  - Writer agent (creative generation)                       │
│  - Reviewer agent (quality evaluation)                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────┐
        │     ITERATION LOOP (Turn 1-N)      │
        │                                    │
        │  ┌──────────────────────────────┐ │
        │  │  1. WRITER GENERATES         │ │
        │  │  - First turn: user_input    │ │
        │  │  - Later turns: + feedback   │ │
        │  │  Output: slogan              │ │
        │  └─────────────┬────────────────┘ │
        │                │                  │
        │                ▼                  │
        │  ┌──────────────────────────────┐ │
        │  │  2. REVIEWER EVALUATES       │ │
        │  │  - Check quality criteria    │ │
        │  │  - Approve or give feedback  │ │
        │  │  Output: review              │ │
        │  └─────────────┬────────────────┘ │
        │                │                  │
        │                ▼                  │
        │  ┌──────────────────────────────┐ │
        │  │  3. CHECK APPROVAL           │ │
        │  │  - Look for "SHIP IT!"       │ │
        │  │  - Set approved flag         │ │
        │  └─────────────┬────────────────┘ │
        │                │                  │
        │                ▼                  │
        │  ┌──────────────────────────────┐ │
        │  │  4. RECORD TURN              │ │
        │  │  - Create Turn object        │ │
        │  │  - Add to session.turns      │ │
        │  └─────────────┬────────────────┘ │
        │                │                  │
        │                ▼                  │
        │  ┌──────────────────────────────┐ │
        │  │  5. DECIDE NEXT ACTION       │ │
        │  │  - If approved → Complete    │ │
        │  │  - If max turns → Complete   │ │
        │  │  - Else → Continue (feedback)│ │
        │  └──────────────────────────────┘ │
        │                                    │
        └────────┬───────────────────┬───────┘
                 │                   │
        Approved │                   │ Max Turns / Not Approved
                 ▼                   │
┌────────────────────────────┐      │
│  COMPLETE (APPROVED)       │      │
│  - Set final_slogan        │      │
│  - Set completion_reason   │      │
│  - Set timestamp           │      │
│  - Return session          │      │
└────────────────────────────┘      │
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │  COMPLETE (MAX_TURNS)         │
                    │  - Use last slogan            │
                    │  - Set completion_reason      │
                    │  - Set timestamp              │
                    │  - Return session             │
                    └───────────────────────────────┘
```

---

## See Also

- [Architecture Overview](overview.md) - System architecture
- [Agent Architecture](agents.md) - Agent design patterns
- [Orchestration API Reference](../api-reference/orchestration.md) - API docs
- [Development Guide](../guides/development.md) - Developer setup
