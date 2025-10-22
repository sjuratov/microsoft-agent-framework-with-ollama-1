# Agent Architecture

This document describes the agent design patterns, communication protocols, and implementation details for the Writer-Reviewer multi-agent system.

## Overview

The system implements a **two-agent collaborative pattern** where specialized agents work together to generate high-quality slogans through iterative refinement.

### Agent Roles

| Agent | Role | Input | Output |
|-------|------|-------|--------|
| **Writer** | Creative generation | Product description + feedback | Slogan proposal |
| **Reviewer** | Quality evaluation | Slogan to review | Approval or feedback |

### Design Philosophy

- **Single Responsibility**: Each agent has one clear purpose
- **Specialized Prompts**: System prompts optimized for specific roles
- **Loose Coupling**: Agents don't directly communicate
- **Stateless**: Agents don't maintain state between calls
- **Extensible**: Easy to add new agent types

---

## Agent Communication Protocol

### Message Flow

```
User Input
    ↓
┌───────────────────────────────────────────┐
│         Orchestration Layer               │
│     (Mediates all communication)          │
└───┬──────────────────────────────────┬────┘
    │                                  │
    │ 1. Generate Request              │
    ▼                                  │
┌──────────┐                           │
│  Writer  │                           │
│  Agent   │                           │
└────┬─────┘                           │
     │ 2. Slogan                       │
     ▼                                 │
┌────────────────┐                     │
│ Orchestration  │                     │
│    (stores)    │                     │
└────┬───────────┘                     │
     │ 3. Review Request               │
     ▼                                 │
                              ┌────────▼─────┐
                              │   Reviewer   │
                              │    Agent     │
                              └────────┬─────┘
     ┌─────────────────────────────────┘
     │ 4. Feedback/Approval
     ▼
┌────────────────┐
│ Orchestration  │
│  (decision)    │
└────┬───────────┘
     │
     ├─ If "SHIP IT!" → Complete
     │
     └─ If feedback → Go to step 1 (with feedback)
```

### Communication Objects

#### WorkflowMessage

```python
@dataclass
class WorkflowMessage:
    """Message passed between orchestration and agents."""
    role: AgentRole  # WRITER or REVIEWER
    content: str     # Slogan or feedback
    metadata: dict   # Additional context
```

#### Turn

```python
class Turn(BaseModel):
    """Single Writer-Reviewer exchange."""
    turn_number: int
    slogan: str
    feedback: str | None
    approved: bool
    timestamp: datetime
```

---

## Writer Agent

### Purpose

Generate creative, memorable slogans based on product descriptions and iterative feedback.

### System Prompt

```python
WRITER_SYSTEM_PROMPT = """
You are a creative slogan writer. Your job is to create short, 
memorable slogans for products or services.

Guidelines:
- Keep slogans between 2-7 words
- Focus on emotional appeal and memorability
- Use active voice and strong verbs
- Avoid clichés and overused phrases
- Be specific to the product/service

If you receive feedback, use it to improve your next slogan.
Only provide the slogan text, no explanations.
"""
```

### Behavior

#### Initial Generation (Turn 1)

**Input**:
```python
{
    "user_input": "eco-friendly water bottles",
    "previous_feedback": None
}
```

**Processing**:
1. Analyze product description
2. Identify key attributes (eco-friendly, water bottles)
3. Generate memorable slogan
4. Focus on emotional appeal

**Output**:
```
"Hydrate Green, Live Clean"
```

#### Refinement (Turn 2+)

**Input**:
```python
{
    "user_input": "eco-friendly water bottles",
    "previous_feedback": "Good start but 'live clean' is vague. 
                         Be more specific about environmental impact."
}
```

**Processing**:
1. Analyze feedback points
2. Identify weaknesses (vagueness)
3. Maintain strengths (rhythm, brevity)
4. Generate improved version

**Output**:
```
"Hydrate Green, Save Our Seas"
```

### Implementation

```python
async def create_writer_agent(config: OllamaConfig) -> Agent:
    """
    Create Writer agent for slogan generation.
    
    Args:
        config: Ollama configuration
        
    Returns:
        Configured Writer agent
    """
    return Agent(
        name="writer",
        model=config.model_name,
        system_message=WRITER_SYSTEM_PROMPT,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
    )
```

### Prompt Engineering

**Key Techniques**:

1. **Clear Guidelines**: Explicit instructions (2-7 words, avoid clichés)
2. **Examples** (implicit): Training data includes good examples
3. **Constraints**: Word count, tone, style
4. **Feedback Integration**: Instruction to use reviewer feedback
5. **Format Specification**: "Only provide slogan text"

**Temperature Settings**:
- **Low (0.3-0.5)**: Conservative, focused (good for professional slogans)
- **Medium (0.7)**: Balanced creativity (default, recommended)
- **High (0.9-1.2)**: More creative, diverse (good for brainstorming)

---

## Reviewer Agent

### Purpose

Evaluate slogans against quality criteria and provide constructive feedback or approval.

### System Prompt

```python
REVIEWER_SYSTEM_PROMPT = """
You are a professional slogan reviewer. Evaluate slogans based on:

1. Memorability - Is it catchy and easy to remember?
2. Clarity - Is the message clear?
3. Conciseness - Is it brief (2-7 words)?
4. Emotional Appeal - Does it evoke the right feelings?
5. Uniqueness - Is it original and distinctive?

If the slogan meets all criteria excellently, respond with exactly:
"SHIP IT!"

Otherwise, provide specific, constructive feedback on what needs 
improvement. Be direct but helpful.
"""
```

### Behavior

#### Evaluation Process

**Input**:
```python
{
    "slogan": "Hydrate Green, Live Clean"
}
```

**Processing**:
1. **Memorability Check**: Is it catchy? ✅ Yes (rhyming, rhythm)
2. **Clarity Check**: Is message clear? ⚠️ "Live clean" is vague
3. **Conciseness Check**: Word count? ✅ 4 words
4. **Emotional Appeal**: Right feelings? ✅ Positive, eco-conscious
5. **Uniqueness Check**: Original? ✅ Not clichéd

**Decision**: Not all criteria met → Provide feedback

**Output**:
```
Good start! The rhythm and rhyme work well. However, 
"live clean" is vague. Be more specific about the 
environmental impact - what exactly are we protecting?
```

#### Approval

**Input**:
```python
{
    "slogan": "Hydrate Green, Save Our Seas"
}
```

**Processing**:
1. **Memorability**: ✅ Excellent (rhyming, clear rhythm)
2. **Clarity**: ✅ Clear environmental message
3. **Conciseness**: ✅ 5 words (optimal)
4. **Emotional Appeal**: ✅ Strong (ocean conservation)
5. **Uniqueness**: ✅ Original phrasing

**Decision**: All criteria met → Approve

**Output**:
```
SHIP IT!
```

### Implementation

```python
async def create_reviewer_agent(config: OllamaConfig) -> Agent:
    """
    Create Reviewer agent for slogan evaluation.
    
    Args:
        config: Ollama configuration
        
    Returns:
        Configured Reviewer agent
    """
    return Agent(
        name="reviewer",
        model=config.model_name,
        system_message=REVIEWER_SYSTEM_PROMPT,
        temperature=0.3,  # Lower temperature for consistency
        max_tokens=config.max_tokens,
    )
```

### Approval Detection

```python
def is_approved(feedback: str) -> bool:
    """
    Check if reviewer approved the slogan.
    
    Args:
        feedback: Reviewer's response
        
    Returns:
        True if approved (contains "SHIP IT!")
    """
    normalized = feedback.upper().strip()
    return bool(re.search(r'\bSHIP IT!?\b', normalized))
```

**Detection Strategy**:
- Case-insensitive matching
- Handles variations: "SHIP IT", "Ship it!", "ship it"
- Word boundary check (avoids false positives)

---

## Agent Coordination

### Orchestration Layer Responsibilities

1. **Agent Lifecycle**:
   - Create agents with proper configuration
   - Manage agent instances
   - Clean up resources

2. **Message Routing**:
   - Route user input to Writer
   - Pass slogan to Reviewer
   - Return feedback to Writer

3. **State Management**:
   - Track iteration count
   - Store turn history
   - Maintain session state

4. **Decision Logic**:
   - Check approval status
   - Determine if more iterations needed
   - Complete session

### Iteration Loop

```python
async def run_slogan_generation(
    user_input: str,
    model_name: str | None = None,
    max_turns: int | None = None
) -> IterationSession:
    """
    Main orchestration loop.
    
    Workflow:
    1. Initialize session
    2. Create agents
    3. Loop until approved or max turns:
       a. Writer generates slogan
       b. Reviewer evaluates
       c. Check approval
       d. If not approved, provide feedback to writer
    4. Complete session
    """
    # Initialize
    config = get_ollama_config()
    session = IterationSession(user_input=user_input, ...)
    writer = await create_writer_agent(config)
    reviewer = await create_reviewer_agent(config)
    
    feedback = None
    
    # Iteration loop
    for turn_num in range(1, max_turns + 1):
        # Writer generates
        slogan = await writer.generate(user_input, feedback)
        
        # Reviewer evaluates
        review = await reviewer.evaluate(slogan)
        
        # Check approval
        approved = is_approved(review)
        
        # Store turn
        session.add_turn(Turn(
            turn_number=turn_num,
            slogan=slogan,
            feedback=None if approved else review,
            approved=approved
        ))
        
        # Exit if approved
        if approved:
            session.complete(CompletionReason.APPROVED)
            return session
        
        # Prepare feedback for next iteration
        feedback = review
    
    # Max turns reached
    session.complete(CompletionReason.MAX_TURNS)
    return session
```

---

## Agent Best Practices

### System Prompt Design

#### ✅ Do:
- **Be specific**: Clear guidelines and constraints
- **Provide criteria**: Explicit evaluation metrics
- **Use examples**: Show desired format
- **Set expectations**: Define success conditions
- **Be concise**: Avoid unnecessary verbosity

#### ❌ Don't:
- **Be vague**: "Write a good slogan" (too broad)
- **Conflict**: Contradictory instructions
- **Overload**: Too many guidelines (cognitive load)
- **Assume**: Context the model might not have

### Temperature Selection

| Task | Temperature | Rationale |
|------|-------------|-----------|
| **Writer (Initial)** | 0.7-0.9 | Creative diversity needed |
| **Writer (Refinement)** | 0.5-0.7 | Focus on feedback integration |
| **Reviewer** | 0.3-0.5 | Consistent evaluation standards |

### Error Handling

```python
try:
    slogan = await writer.generate(input, feedback)
except TimeoutError:
    # Retry with shorter timeout
    slogan = await writer.generate(input, feedback, timeout=15)
except ModelError as e:
    # Log error and use fallback
    logger.error(f"Writer failed: {e}")
    raise GenerationError("Writer agent unavailable")
```

---

## Extending the Agent System

### Adding a New Agent

#### Example: Editor Agent

```python
# src/agents/editor.py

EDITOR_SYSTEM_PROMPT = """
You are a professional copy editor. Review slogans for:
1. Grammar and spelling
2. Punctuation
3. Style consistency
4. Word choice

Provide corrections or respond with "APPROVED" if perfect.
"""

async def create_editor_agent(config: OllamaConfig) -> Agent:
    """Create Editor agent for grammar/style review."""
    return Agent(
        name="editor",
        model=config.model_name,
        system_message=EDITOR_SYSTEM_PROMPT,
        temperature=0.2,  # Very consistent editing
        max_tokens=config.max_tokens,
    )
```

#### Integration

```python
# src/orchestration/workflow.py

async def run_slogan_generation_with_editor(
    user_input: str,
    model_name: str | None = None,
    max_turns: int | None = None
) -> IterationSession:
    """Enhanced workflow with Editor agent."""
    
    writer = await create_writer_agent(config)
    reviewer = await create_reviewer_agent(config)
    editor = await create_editor_agent(config)  # New agent
    
    for turn_num in range(1, max_turns + 1):
        # Writer generates
        slogan = await writer.generate(user_input, feedback)
        
        # Editor reviews grammar (NEW STEP)
        edited_slogan = await editor.review(slogan)
        
        # Reviewer evaluates
        review = await reviewer.evaluate(edited_slogan)
        
        # ... rest of logic
```

### Multi-Agent Patterns

#### Sequential Pattern (Current)
```
Writer → Reviewer → (loop)
```

#### Parallel Pattern
```
       ┌→ Reviewer A → Aggregate
Writer ┤
       └→ Reviewer B → Aggregate
```

#### Hierarchical Pattern
```
Writer → Editor → Reviewer → Manager
```

---

## Performance Considerations

### Agent Call Optimization

**Current**: 2 LLM calls per iteration (Writer + Reviewer)

**Optimization Options**:

1. **Batch Processing**: Generate multiple slogans, review all
2. **Caching**: Cache agent responses for similar inputs
3. **Streaming**: Stream responses for faster perceived speed
4. **Parallel Reviewers**: Multiple reviewers vote on quality

### Model Selection

| Use Case | Recommended Model | Rationale |
|----------|------------------|-----------|
| **Development** | `gemma2:2b` | Fast iteration, lower quality OK |
| **Testing** | `phi3:mini` | Good balance for tests |
| **Production** | `mistral:latest` | Best quality-to-speed ratio |
| **High Quality** | `llama3.2:latest` | Best results, slower |

---

## Testing Agents

### Unit Testing

```python
# tests/unit/test_agents.py

async def test_writer_generates_slogan():
    """Test writer agent produces valid slogan."""
    config = OllamaConfig(model_name="gemma2:2b")
    writer = await create_writer_agent(config)
    
    slogan = await writer.generate("eco-friendly water bottles")
    
    assert slogan
    assert len(slogan.split()) <= 10  # Reasonable length
    assert slogan.strip() == slogan  # No extra whitespace

async def test_reviewer_detects_approval():
    """Test reviewer can approve slogans."""
    config = OllamaConfig(model_name="gemma2:2b")
    reviewer = await create_reviewer_agent(config)
    
    # Excellent slogan
    feedback = await reviewer.evaluate("Hydrate Green, Save Our Seas")
    
    assert is_approved(feedback)
```

### Integration Testing

```python
# tests/integration/test_agents_integration.py

async def test_writer_reviewer_collaboration():
    """Test full Writer-Reviewer workflow."""
    session = await run_slogan_generation(
        "smart home devices",
        max_turns=3
    )
    
    assert session.final_slogan
    assert session.turn_count >= 1
    assert session.completion_reason in [
        CompletionReason.APPROVED,
        CompletionReason.MAX_TURNS
    ]
```

---

## See Also

- [Architecture Overview](overview.md) - High-level system design
- [Workflow Architecture](workflow.md) - Orchestration details
- [Agents API Reference](../api-reference/agents.md) - API documentation
- [Development Guide](../guides/development.md) - Developer setup
