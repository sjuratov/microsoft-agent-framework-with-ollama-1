# Feature Specification: Iterative Slogan Writer-Reviewer Agent System

**Feature Branch**: `001-slogan-writer-reviewer`  
**Created**: 2025-10-19  
**Status**: Draft  
**Input**: User description: "I want to create an agentic solution that is taking user input, pass that to writer agent to a slogan. Once writer creates slogan, it passes that to reviewer agent that is providing critical feedback. If reviewer agent is happy with writer's agent result, it will tell writer agent to SHIP IT!. If it's not happy with writer's result, it will pass that feedback on to a writer, who will create new version based on the feedback. writer/reviewer agents will take max 5 turns before outputing result. Both agents will use Ollama local model. Model will be past as configuration parameter to the application. First iteration of this application will be used by end users using command line. Command line in shell terminal. However, in the future I would want to expose this agentic solution as FastAPI. Don't create any FastAPI code now, just keep this in mind as you create first command line iteration"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Basic Slogan Generation (Priority: P1)

A user provides a topic or product description via command line, and the system generates a slogan through iterative collaboration between writer and reviewer agents, outputting the final approved slogan.

**Why this priority**: This is the core MVP - the essential functionality that delivers immediate value. Without this, there is no product.

**Independent Test**: Can be fully tested by running the CLI with a simple input (e.g., "eco-friendly water bottle") and verifying that a slogan is generated and displayed after writer-reviewer collaboration.

**Acceptance Scenarios**:

1. **Given** the CLI is installed and configured with an Ollama model, **When** user runs the command with input "eco-friendly water bottle", **Then** the system outputs a final approved slogan within the 5-turn limit
2. **Given** the agents are collaborating, **When** the reviewer approves a slogan, **Then** the system displays "SHIP IT!" and outputs the final slogan
3. **Given** the agents are collaborating, **When** the reviewer provides feedback, **Then** the writer creates a new version incorporating that feedback

---

### User Story 2 - Iteration Visibility (Priority: P2)

A user wants to see the iterative process between writer and reviewer agents, including each version of the slogan and the feedback provided.

**Why this priority**: Transparency in the agent collaboration process builds trust and helps users understand how the final slogan was created. Also valuable for debugging and understanding agent behavior.

**Independent Test**: Can be tested by running the CLI with verbose output flag and verifying that all intermediate slogans, feedback, and turn counts are displayed.

**Acceptance Scenarios**:

1. **Given** the user runs the CLI, **When** agents are iterating, **Then** each turn displays: turn number, writer's slogan, and reviewer's feedback
2. **Given** the iteration reaches turn 5, **When** no approval has been given, **Then** the system outputs the best slogan from the iterations with a message indicating max turns reached
3. **Given** the reviewer approves before turn 5, **When** "SHIP IT!" is declared, **Then** the system shows total turns taken and final slogan

---

### User Story 3 - Configurable Model Selection (Priority: P3)

A user wants to specify which Ollama model to use for the agents, allowing flexibility to choose between different model sizes and capabilities based on their needs.

**Why this priority**: While important for flexibility and future-proofing, the system can function with a sensible default model. This is an enhancement that improves user experience but isn't critical for MVP.

**Independent Test**: Can be tested by running the CLI with different model parameters (e.g., `--model llama2`, `--model mistral`) and verifying that the specified model is used by both agents.

**Acceptance Scenarios**:

1. **Given** the user specifies a model via CLI parameter, **When** the command runs, **Then** both writer and reviewer agents use the specified model
2. **Given** no model is specified, **When** the command runs, **Then** the system uses a default model and completes successfully
3. **Given** an invalid model name is provided, **When** the command runs, **Then** the system displays a helpful error message listing available models

---

### Edge Cases

- What happens when the user provides empty or very short input (e.g., single word, empty string)?
- How does the system handle Ollama connection failures or model unavailability?
- What happens if the reviewer never approves within 5 turns?
- How does the system behave if the writer or reviewer produces unexpected output format?
- What happens when the user interrupts the process mid-iteration (Ctrl+C)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept user input describing the topic/product for slogan generation via command line
- **FR-002**: System MUST implement a writer agent that generates slogans based on user input and reviewer feedback
- **FR-003**: System MUST implement a reviewer agent that evaluates slogans and provides critical feedback or approval
- **FR-004**: System MUST facilitate communication between writer and reviewer agents for up to 5 iteration turns
- **FR-005**: System MUST terminate iteration when reviewer approves (responds with "SHIP IT!") or when 5 turns are completed
- **FR-006**: System MUST output the final approved slogan to the command line
- **FR-007**: System MUST accept Ollama model name as a configuration parameter
- **FR-008**: System MUST use the specified Ollama model for both writer and reviewer agents
- **FR-009**: System MUST display the iterative process including turn numbers, slogans, and feedback
- **FR-010**: System MUST handle cases where 5 turns are reached without approval by outputting the latest slogan
- **FR-011**: System MUST provide clear error messages if Ollama is not available or model is invalid
- **FR-012**: System MUST be designed with future API extension in mind (architecture should support both CLI and API interfaces)

### Key Entities

- **Writer Agent**: An autonomous agent that generates creative slogans based on user input and iteratively improves them based on reviewer feedback. Communicates with Ollama local model.
- **Reviewer Agent**: An autonomous agent that evaluates slogans for quality, creativity, and effectiveness. Provides critical feedback to guide improvements or approves with "SHIP IT!". Communicates with Ollama local model.
- **Iteration Turn**: A single cycle of writer generating/revising a slogan and reviewer providing feedback. Maximum 5 turns per session.
- **Slogan**: The creative output - a short, memorable phrase created by the writer agent for the user's specified topic/product.
- **User Input**: The topic, product, or concept description provided by the end user via command line.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can generate a slogan by providing input via command line and receiving output within 5 minutes
- **SC-002**: System completes the writer-reviewer iteration cycle within 5 turns or less for 100% of sessions
- **SC-003**: Users can see each iteration step (slogan version and feedback) in the command line output
- **SC-004**: System successfully handles connection to local Ollama model and gracefully reports errors if unavailable
- **SC-005**: Users can specify different Ollama models via configuration and observe different agent behaviors
- **SC-006**: 90% of users successfully generate their first slogan without requiring support or documentation beyond basic usage instructions

## Assumptions *(optional)*

- Ollama is already installed and running on the user's local machine
- Users have at least one Ollama model downloaded and available
- Command line interface will be the only user interface for this iteration (no GUI, web interface, or API)
- Both agents (writer and reviewer) will use the same Ollama model instance
- The definition of "approval" is when the reviewer's response contains "SHIP IT!"
- If 5 turns are exhausted, the last generated slogan is considered the final output
- Users have basic familiarity with command line tools
- The architecture will be modular enough to support future FastAPI integration without major refactoring

## Constraints *(optional)*

- Maximum 5 iteration turns between writer and reviewer agents (hard limit)
- System must use local Ollama models only (no cloud API calls)
- Must run on end user's local machine via command line
- Output must be text-based to the terminal
- No persistent storage required for this iteration (stateless sessions)

## Dependencies *(optional)*

- Ollama must be installed and running on the user's system
- At least one Ollama language model must be available locally
- Python 3.8+ (assumed for Microsoft Agent Framework)
- Microsoft Agent Framework library compatibility with Ollama

## Out of Scope

- FastAPI web service implementation (future iteration)
- Web-based user interface
- Persistent storage of generated slogans or conversation history
- Multi-user support or concurrent sessions
- Model fine-tuning or training
- Support for non-Ollama models (e.g., OpenAI, Anthropic)
- Advanced slogan analytics or quality metrics
- User authentication or authorization
- Slogan versioning or history tracking beyond current session

## Future Considerations

- FastAPI service wrapper to expose functionality via REST API
- Web-based interface for broader accessibility
- Conversation history and slogan storage
- Multiple specialized reviewer agents (e.g., brand tone, legal compliance, audience targeting)
- Integration with other local LLM providers
- Slogan quality scoring and analytics
- Batch processing mode for multiple inputs
- Export functionality (JSON, CSV, etc.)

