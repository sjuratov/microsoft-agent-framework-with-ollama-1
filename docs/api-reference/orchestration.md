# Orchestration API Reference

# Orchestration API Reference

This page documents the workflow orchestration and data models that coordinate the Writer-Reviewer collaboration.

## Overview

The orchestration layer manages the iterative collaboration between Writer and Reviewer agents. It handles:

- **Workflow Coordination**: Managing the turn-by-turn iteration loop
- **State Management**: Tracking session progress and turn history
- **Completion Logic**: Determining when to stop iterating
- **Data Models**: Structured representations of turns and sessions

## Workflow

::: src.orchestration.workflow.run_slogan_generation
    options:
      show_source: true
      heading_level: 3

### Workflow Process

The slogan generation workflow follows this pattern:

```
1. Initialize Session
   ↓
2. Turn Loop:
   ├─ Writer generates slogan
   ├─ Reviewer evaluates
   ├─ Check approval
   └─ Continue or stop
   ↓
3. Complete Session
```

**Loop Continuation Logic**:

- **Continue** if: Not approved AND turns < max_turns
- **Stop** if: Approved OR reached max_turns

### Usage Example

```python
from src.orchestration import run_slogan_generation

# Basic usage
session = await run_slogan_generation(
    user_input="eco-friendly water bottle"
)

print(f"Final Slogan: {session.final_slogan}")
print(f"Reason: {session.completion_reason}")
print(f"Turns: {len(session.turns)}")

# With custom configuration
session = await run_slogan_generation(
    user_input="AI coding assistant",
    model_name="llama3.2:latest",
    max_turns=7
)

# Access turn history
for turn in session.turns:
    print(f"Turn {turn.turn_number}: {turn.slogan}")
    print(f"Feedback: {turn.feedback}")
    print(f"Approved: {turn.approved}")
```

---

## Helper Functions

### is_approved

::: src.orchestration.workflow.is_approved
    options:
      show_source: true
      heading_level: 4

**Purpose**: Detect if reviewer has approved the slogan.

**Detection Strategy**:

1. Checks if response starts with "ship it" (most reliable)
2. Checks for "ship it!" on its own line
3. Uses regex to match variations with punctuation

**Examples**:

```python
from src.orchestration.workflow import is_approved

# Approved responses
is_approved("SHIP IT!")                    # True
is_approved("Ship it!")                    # True
is_approved("ship it")                     # True
is_approved("SHIP IT! Great work!")        # True

# Not approved (contains feedback)
is_approved("Good, but ship it later")     # False
is_approved("Try shipping this idea")      # False
is_approved("Needs work. Make it catchy")  # False
```

### should_continue_iteration

::: src.orchestration.workflow.should_continue_iteration
    options:
      show_source: true
      heading_level: 4

**Purpose**: Determine if the iteration loop should continue.

**Logic**:

- Returns `True` if: Not approved AND turns < max_turns
- Returns `False` if: Approved OR reached max_turns

**Usage**:

```python
from src.orchestration.workflow import should_continue_iteration
from src.orchestration.models import IterationSession
from src.config import get_ollama_config

session = IterationSession(user_input="test", model_name="mistral:latest")
config = get_ollama_config()

# First iteration
should_continue_iteration(session, config)  # True (no turns yet)

# Add approved turn
session.add_turn("Great Slogan!", "SHIP IT!", approved=True)
should_continue_iteration(session, config)  # False (approved)

# Reached max turns
for i in range(config.max_turns):
    session.add_turn(f"Slogan {i}", "Try again", approved=False)
should_continue_iteration(session, config)  # False (max turns)
```

---

## Data Models

### IterationSession

::: src.orchestration.models.IterationSession
    options:
      show_source: true
      heading_level: 4
      members:
        - add_turn
        - complete

**Purpose**: Represents a complete slogan generation session with all turns.

**Key Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `user_input` | str | Original product/service description |
| `model_name` | str | Ollama model used |
| `turns` | list[Turn] | All iteration turns |
| `final_slogan` | str \| None | Final approved or best slogan |
| `completed` | bool | Session completion status |
| `completion_reason` | CompletionReason \| None | Why session ended |
| `started_at` | datetime | Session start timestamp |
| `completed_at` | datetime \| None | Session end timestamp |

**Methods**:

- `add_turn(slogan, feedback, approved)`: Add new turn to session
- `complete(reason)`: Mark session as complete

**Usage Example**:

```python
from src.orchestration.models import IterationSession, CompletionReason

# Create session
session = IterationSession(
    user_input="coffee shop",
    model_name="mistral:latest"
)

# Add turns
session.add_turn(
    slogan="Coffee Perfection",
    feedback="Too generic, add emotion",
    approved=False
)

session.add_turn(
    slogan="☕ Brew Happiness Daily",
    feedback="SHIP IT!",
    approved=True
)

# Complete session
session.complete(CompletionReason.APPROVED)

# Access results
print(f"Final: {session.final_slogan}")          # "☕ Brew Happiness Daily"
print(f"Turns: {len(session.turns)}")            # 2
print(f"Duration: {session.completed_at - session.started_at}")
```

---

### Turn

::: src.orchestration.models.Turn
    options:
      show_source: true
      heading_level: 4

**Purpose**: Represents one iteration turn in the Writer-Reviewer cycle.

**Key Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `turn_number` | int | 1-10 | Turn sequence number |
| `slogan` | str | 1-500 chars | Generated slogan |
| `feedback` | str \| None | max 1000 chars | Reviewer feedback |
| `approved` | bool | | Approval status |
| `timestamp` | datetime | | Turn creation time |

**Validation**:

- `slogan`: Must be 1-500 characters (enforces conciseness)
- `feedback`: Maximum 1000 characters
- `turn_number`: Must be 1-10

**Usage Example**:

```python
from src.orchestration.models import Turn

turn = Turn(
    turn_number=1,
    slogan="Eco-Smart Hydration",
    feedback="Good start, but emphasize sustainability more",
    approved=False
)

print(f"Turn {turn.turn_number}: {turn.slogan}")
print(f"Status: {'Approved' if turn.approved else 'Needs revision'}")
```

---

### CompletionReason

::: src.orchestration.models.CompletionReason
    options:
      show_source: true
      heading_level: 4

**Purpose**: Enumeration of reasons why a session completed.

**Values**:

| Value | Description |
|-------|-------------|
| `APPROVED` | Reviewer approved with "SHIP IT!" |
| `MAX_TURNS` | Reached maximum turn limit |
| `ERROR` | Error occurred during workflow |

**Usage Example**:

```python
from src.orchestration.models import CompletionReason

# Check completion reason
if session.completion_reason == CompletionReason.APPROVED:
    print("✅ Slogan approved!")
elif session.completion_reason == CompletionReason.MAX_TURNS:
    print("⚠️ Max turns reached, using best slogan")
elif session.completion_reason == CompletionReason.ERROR:
    print("❌ Error occurred")
```

---

### AgentRole

::: src.orchestration.models.AgentRole
    options:
      show_source: true
      heading_level: 4

**Purpose**: Enumeration of agent roles in the system.

**Values**:

- `WRITER`: Writer agent (generates slogans)
- `REVIEWER`: Reviewer agent (provides feedback)

---

### WorkflowMessage

::: src.orchestration.models.WorkflowMessage
    options:
      show_source: true
      heading_level: 4

**Purpose**: Message exchanged between agents (for future extensions).

**Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `from_agent` | AgentRole | Sending agent |
| `to_agent` | AgentRole | Receiving agent |
| `content` | str | Message content |
| `turn_number` | int | Associated turn number |
| `metadata` | dict | Additional metadata |

---

## Workflow Patterns

### Basic Workflow

```python
# Simple generation
session = await run_slogan_generation("coffee shop")

if session.completion_reason == CompletionReason.APPROVED:
    print(f"✅ Approved: {session.final_slogan}")
else:
    print(f"⚠️ Max turns reached: {session.final_slogan}")
```

### Custom Configuration

```python
# Use larger model and more turns for higher quality
session = await run_slogan_generation(
    user_input="luxury fashion brand",
    model_name="llama3.2:latest",
    max_turns=10
)
```

### Error Handling

```python
try:
    session = await run_slogan_generation("test")
except ValueError as e:
    print(f"Invalid input: {e}")
except RuntimeError as e:
    print(f"Workflow error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Accessing Turn History

```python
session = await run_slogan_generation("AI assistant")

print("\n📊 Iteration History:")
for turn in session.turns:
    status = "✅" if turn.approved else "🔄"
    print(f"\n{status} Turn {turn.turn_number}:")
    print(f"  Slogan: {turn.slogan}")
    print(f"  Feedback: {turn.feedback[:100]}...")
    print(f"  Time: {turn.timestamp.strftime('%H:%M:%S')}")
```

### Session Metrics

```python
session = await run_slogan_generation("product")

# Calculate metrics
total_duration = (session.completed_at - session.started_at).total_seconds()
avg_duration_per_turn = total_duration / len(session.turns)
approval_rate = sum(1 for t in session.turns if t.approved) / len(session.turns)

print(f"Total Duration: {total_duration:.1f}s")
print(f"Avg Per Turn: {avg_duration_per_turn:.1f}s")
print(f"Turns: {len(session.turns)}/{session.max_turns}")
print(f"Approval Rate: {approval_rate:.1%}")
```

---

## Best Practices

### Input Validation

✅ **Do**:
```python
user_input = user_input.strip()
if not user_input:
    raise ValueError("Input cannot be empty")

session = await run_slogan_generation(user_input)
```

❌ **Don't**:
```python
# Don't pass unvalidated input
session = await run_slogan_generation(user_input)  # May raise ValueError
```

### Max Turns Configuration

✅ **Do**:
```python
# Quick brainstorming
session = await run_slogan_generation(input, max_turns=3)

# High quality
session = await run_slogan_generation(input, max_turns=7)
```

❌ **Don't**:
```python
# Don't use 1 turn (no feedback loop)
session = await run_slogan_generation(input, max_turns=1)

# Don't use too many turns (slow, diminishing returns)
session = await run_slogan_generation(input, max_turns=15)  # Invalid (max 10)
```

### Error Handling

✅ **Do**:
```python
try:
    session = await run_slogan_generation(input)
    if session.completion_reason == CompletionReason.ERROR:
        # Handle gracefully
        logger.error("Workflow failed")
except RuntimeError as e:
    # Catch and handle workflow errors
    logger.exception("Workflow exception")
```

---

## See Also

- [Agents API](agents.md) - Writer and Reviewer agent implementations
- [Config API](config.md) - Configuration management
- [CLI Usage Guide](../guides/cli-usage.md) - Using orchestration via CLI
- [Architecture: Workflow](../architecture/workflow.md) - Workflow design details
