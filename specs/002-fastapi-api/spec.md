# Feature Specification: FastAPI REST API for Slogan Generation

**Feature Branch**: `002-fastapi-api`  
**Created**: 2025-10-21  
**Status**: Draft  
**Dependencies**: Spec 001 (CLI implementation must be complete)  
**Input**: "Expose the existing slogan generation functionality via FastAPI REST API, enabling developers to integrate slogan generation into their applications programmatically."

## Clarifications

### Session 2025-10-21

- Q: When 10 concurrent generation requests are already in progress and an 11th request arrives, how should the API respond? → A: Accept and log the request, return 202 Accepted with estimated wait time
- Q: For the 202 Accepted response when requests are queued, how should the request tracking information be provided to clients? → A: Request ID in response headers (X-Request-ID) and JSON body
- Q: When the API returns 202 Accepted (request queued due to concurrency limit), what should be logged and at what level? → A: Log as warning with details

## 2. Design Principles

1. **Reuse Existing Logic**: The API layer wraps existing orchestration without modification
2. **Simplicity First**: Start with core functionality, avoid premature optimization
3. **API-First Design**: Follow REST principles, provide comprehensive OpenAPI documentation
4. **Async by Default**: Use async endpoints with thread pool executors for long-running operations

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Programmatic Slogan Generation (Priority: P1)

A developer wants to integrate slogan generation into their application by making HTTP POST requests to generate slogans programmatically, receiving structured JSON responses with the final slogan and metadata.

**Why this priority**: This is the core MVP for the API - the essential functionality that enables programmatic access. Without this, there is no API product.

**Independent Test**: Can be fully tested by making a POST request to `/api/v1/slogans/generate` with valid JSON input and verifying a successful JSON response with slogan and metadata.

**Acceptance Scenarios**:

1. **Given** the API is running and Ollama is available, **When** a developer sends `POST /api/v1/slogans/generate` with `{"input": "coffee shop"}`, **Then** the API returns 200 OK with JSON containing `{"slogan": "...", "completion_reason": "approved", "turn_count": 2, "duration": 21.5}`
2. **Given** the API receives a request, **When** the writer-reviewer collaboration completes successfully, **Then** the response includes the final slogan, all iteration turns, timing information, and completion status
3. **Given** the API receives a request with custom parameters, **When** the request includes `{"input": "...", "model": "mistral:latest", "max_turns": 3}`, **Then** the API uses those parameters for generation

**Error Scenarios**:

1. **Given** the API receives invalid input, **When** the request body is malformed or missing required fields, **Then** the API returns 422 Unprocessable Entity with validation error details
2. **Given** Ollama is not running, **When** a generation request is made, **Then** the API returns 503 Service Unavailable with error message indicating Ollama connection failure
3. **Given** the specified model doesn't exist, **When** the request includes an invalid model name, **Then** the API returns 400 Bad Request with available models listed

---

### User Story 2 - Model Discovery (Priority: P2)

A developer wants to discover which Ollama models are available before making generation requests, enabling them to present model options to their users or validate model selection.

**Why this priority**: Important for usability and validation, but the API can function with hardcoded defaults. This enhances developer experience but isn't critical for MVP.

**Independent Test**: Can be tested by making a GET request to `/api/v1/models` and verifying the response contains a list of available models with metadata.

**Acceptance Scenarios**:

1. **Given** the API is running with Ollama available, **When** a developer sends `GET /api/v1/models`, **Then** the API returns 200 OK with JSON containing `{"models": [{"name": "mistral:latest", "size": "7B"}, ...], "default": "mistral:latest"}`
2. **Given** Ollama has multiple models installed, **When** the models endpoint is called, **Then** all available models are listed with their names and basic metadata
3. **Given** a model is set as default in configuration, **When** the models endpoint is called, **Then** the default model is clearly indicated in the response

---

### User Story 3 - Health Monitoring (Priority: P2)

An operations engineer wants to monitor the API's health status, including connectivity to Ollama, to ensure the service is operational and integrate with monitoring tools.

**Why this priority**: Critical for production deployment and monitoring, but not required for initial development and testing. Essential for operational excellence.

**Independent Test**: Can be tested by making a GET request to `/api/v1/health` and verifying the response indicates service status and dependencies.

**Acceptance Scenarios**:

1. **Given** the API and Ollama are both running, **When** a monitoring tool sends `GET /api/v1/health`, **Then** the API returns 200 OK with `{"status": "healthy", "ollama": {"connected": true, "url": "http://localhost:11434"}}`
2. **Given** Ollama is not running, **When** the health endpoint is called, **Then** the API returns 503 Service Unavailable with `{"status": "degraded", "ollama": {"connected": false, "error": "Connection refused"}}`
3. **Given** the API is starting up, **When** dependencies are being initialized, **Then** the health endpoint returns appropriate status indicating readiness

---

### User Story 4 - API Documentation (Priority: P2)

A developer wants to explore the API endpoints, request/response schemas, and example usage through interactive documentation to quickly understand how to integrate the API.

**Why this priority**: Essential for developer adoption but automatically provided by FastAPI. This is a configuration task rather than a feature implementation.

**Independent Test**: Can be tested by navigating to `/docs` (Swagger UI) or `/redoc` (ReDoc) and verifying all endpoints are documented with schemas and examples.

**Acceptance Scenarios**:

1. **Given** the API is running, **When** a developer navigates to `/docs`, **Then** they see interactive Swagger UI with all endpoints, request/response schemas, and can test requests
2. **Given** a developer is viewing the documentation, **When** they select an endpoint, **Then** they see detailed schema definitions, example requests/responses, and can try it out
3. **Given** the API schemas are defined, **When** OpenAPI spec is generated, **Then** it includes all validation rules, optional parameters, and error responses

---

## API Design

### Base URL

```
http://localhost:8000/api/v1
```

**Versioning Strategy**: URL-based versioning (`/api/v1`, `/api/v2`) to maintain backward compatibility.

### Endpoints

#### 1. Generate Slogan

**Endpoint**: `POST /api/v1/slogans/generate` (async)

**Description**: Generate a creative slogan through Writer-Reviewer agent collaboration. Uses async endpoint with thread pool executor to handle long-running Ollama operations (up to 10 minutes) without blocking concurrent requests.

**Implementation Pattern**:
```python
# Async endpoint wrapping sync orchestration
@router.post("/api/v1/slogans/generate")
async def generate_slogan(request: SloganRequest):
    loop = asyncio.get_event_loop()
    result = await asyncio.wait_for(
        loop.run_in_executor(None, orchestration.run_slogan_generation, 
                            request.input, request.model),
        timeout=600.0  # 10 minute timeout to accommodate all models/max_turns
    )
    return result
```

**Request Body**:
```json
{
  "input": "string (required, 1-500 chars)",
  "model": "string (optional, default: mistral:latest)",
  "max_turns": "integer (optional, 1-10, default: 5)",
  "verbose": "boolean (optional, default: false)"
}
```

**Response** (200 OK):
```json
{
  "slogan": "string - final approved slogan",
  "input": "string - original user input",
  "completion_reason": "approved | max_turns | error",
  "turn_count": "integer - number of iterations",
  "model_name": "string - model used",
  "total_duration_seconds": "float - total generation time",
  "average_duration_per_turn": "float - average per iteration",
  "turns": [
    {
      "turn_number": "integer",
      "slogan": "string",
      "feedback": "string or null",
      "approved": "boolean",
      "timestamp": "ISO 8601 datetime"
    }
  ],
  "created_at": "ISO 8601 datetime - request timestamp"
}
```

**Error Responses**:
- `202 Accepted`: Request queued (when 10 concurrent requests already in progress)
  ```json
  {
    "request_id": "uuid-v4",
    "status": "queued",
    "estimated_wait_seconds": 300,
    "message": "Request queued. Maximum concurrent requests reached."
  }
  ```
  Response includes `X-Request-ID` header with same UUID for tracking.
- `400 Bad Request`: Invalid model name or parameters
- `422 Unprocessable Entity`: Validation errors (missing fields, invalid types)
- `503 Service Unavailable`: Ollama connection failure
- `500 Internal Server Error`: Unexpected errors during generation

**Example Request**:
```bash
curl -X POST "http://localhost:8000/api/v1/slogans/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "eco-friendly water bottle",
    "model": "mistral:latest",
    "max_turns": 5
  }'
```

---

#### 2. List Models

**Endpoint**: `GET /api/v1/models` (async)

**Description**: Retrieve list of available Ollama models for slogan generation. Uses async to avoid blocking during Ollama API calls.

**Query Parameters**: None

**Response** (200 OK):
```json
{
  "models": [
    {
      "name": "string - model identifier",
      "display_name": "string - human-readable name",
      "is_default": "boolean"
    }
  ],
  "default_model": "string - default model name",
  "total_count": "integer"
}
```

**Error Responses**:
- `503 Service Unavailable`: Cannot connect to Ollama

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/models"
```

---

#### 3. Health Check

**Endpoint**: `GET /api/v1/health` (async)

**Description**: Check API and dependency health status. Uses async to perform non-blocking health checks against Ollama.

**Query Parameters**: None

**Response** (200 OK - Healthy):
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "ISO 8601 datetime",
  "dependencies": {
    "ollama": {
      "connected": true,
      "url": "http://localhost:11434",
      "response_time_ms": 15
    }
  }
}
```

**Response** (503 Service Unavailable - Unhealthy):
```json
{
  "status": "degraded",
  "version": "1.0.0",
  "timestamp": "ISO 8601 datetime",
  "dependencies": {
    "ollama": {
      "connected": false,
      "url": "http://localhost:11434",
      "error": "Connection refused"
    }
  }
}
```

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/health"
```

---

#### 4. Root Endpoint

**Endpoint**: `GET /` (sync - simple metadata, no I/O)

**Description**: API information and documentation links. Synchronous endpoint as it returns static metadata without external calls.

**Response** (200 OK):
```json
{
  "name": "Slogan Writer-Reviewer API",
  "version": "1.0.0",
  "description": "Multi-agent slogan generation via Writer-Reviewer collaboration",
  "documentation": {
    "swagger": "/docs",
    "redoc": "/redoc",
    "openapi": "/openapi.json"
  }
}
```

---

## Technical Architecture

### Layer Structure (Reusing Existing Code)

```
src/
├── agents/          # ✅ Reuse existing (no changes)
├── orchestration/   # ✅ Reuse existing (no changes)
├── config/          # ✅ Reuse existing (no changes)
├── cli/             # ✅ Keep separate (no changes)
└── api/             # 🆕 New FastAPI layer
    ├── __init__.py
    ├── main.py          # FastAPI app initialization
    ├── routes/
    │   ├── __init__.py
    │   ├── slogans.py   # Slogan generation endpoints
    │   ├── models.py    # Model listing endpoints
    │   └── health.py    # Health check endpoints
    ├── schemas/
    │   ├── __init__.py
    │   ├── requests.py  # Pydantic request models
    │   └── responses.py # Pydantic response models
    ├── dependencies.py  # FastAPI dependencies (config, etc.)
    └── middleware.py    # CORS, error handling, logging
```

### Key Components

1. **FastAPI Application** (`api/main.py`):
   - Initialize FastAPI app with metadata
   - Configure CORS for development
   - Include routers for each endpoint group
   - Add global exception handlers
   - Configure OpenAPI documentation

2. **Request/Response Schemas** (`api/schemas/`):
   - Pydantic models for request validation
   - Response models matching API contracts
   - Reuse `orchestration.models.IterationSession` for internal logic
   - Transform to API-specific response format

3. **Route Handlers** (`api/routes/`):
   - Async endpoint implementations
   - Call existing `orchestration.run_slogan_generation()`
   - Transform domain models to API responses
   - Handle errors and return appropriate HTTP status codes

4. **Dependencies** (`api/dependencies.py`):
   - Inject Ollama configuration
   - Shared dependency for config loading
   - Model validation dependency

5. **Middleware** (`api/middleware.py`):
   - CORS configuration (allow specific origins)
   - Request/response logging
   - Error handling middleware
   - Request ID generation (UUID v4) - added to response headers (`X-Request-ID`) and JSON body for all requests
   - Concurrency overflow logging: WARNING level when 202 Accepted returned, includes request_id, queue depth, estimated wait time

### Data Flow

```
HTTP Request
    ↓
FastAPI Router
    ↓
Request Schema Validation (Pydantic)
    ↓
Route Handler (async)
    ↓
orchestration.run_slogan_generation()  ← Existing code, no changes
    ↓
IterationSession (domain model)
    ↓
Transform to API Response Schema
    ↓
JSON Response
```

---

## Non-Functional Requirements

### Performance

- **Response Time**: Up to 10 minutes for generation (depends on model, max_turns, and complexity)
- **Concurrent Requests**: Support at least 10 concurrent slogan generation requests without blocking
- **Concurrency Overflow**: When 10 concurrent requests are in progress, additional requests return 202 Accepted with estimated wait time and request tracking information
- **Timeout**: 600 second (10 minute) timeout per generation request (configurable), 630 second overall request timeout
- **Async Pattern**: Thread pool executor for long-running operations ensures non-blocking I/O

### Security
- **CORS**: Configurable allowed origins (default: localhost for development)
- **Input Validation**: Strict Pydantic validation on all inputs
- **Rate Limiting**: Not implemented in v1 (future consideration)
- **Authentication**: Not implemented in v1 (future consideration)

### Reliability
- **Error Handling**: All errors return structured JSON with error details
- **Health Checks**: Dedicated endpoint for monitoring
- **Graceful Degradation**: Clear error messages when Ollama unavailable

### Documentation
- **OpenAPI**: Auto-generated from FastAPI route definitions
- **Swagger UI**: Interactive documentation at `/docs`
- **ReDoc**: Alternative documentation at `/redoc`
- **Examples**: All endpoints include example requests/responses

---

## Configuration

### Environment Variables (Extend Existing)

```bash
# Existing (reused from CLI config)
OLLAMA_BASE_URL="http://localhost:11434/v1"
OLLAMA_MODEL_NAME="mistral:latest"
OLLAMA_MAX_TURNS=5
OLLAMA_TEMPERATURE=0.7
OLLAMA_MAX_TOKENS=500
OLLAMA_TIMEOUT=30

# New API-specific
API_HOST="0.0.0.0"
API_PORT=8000
API_CORS_ORIGINS="http://localhost:3000,http://localhost:8080"
API_REQUEST_TIMEOUT=630
API_GENERATION_TIMEOUT=600
API_WORKERS=4
```

### Running the API

**Development**:
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**Production**:
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Docker** (future):
```bash
docker run -p 8000:8000 slogan-gen-api
```

---

## Testing Strategy

### API Integration Tests

Create new test suite in `tests/api/`:

1. **Test Request/Response Contracts**:
   - Valid requests return 200 with correct schema
   - Invalid requests return 422 with validation errors
   - Missing fields return appropriate errors

2. **Test Error Handling**:
   - Ollama unavailable returns 503
   - Invalid model returns 400
   - Timeouts handled gracefully

3. **Test Business Logic Integration**:
   - Generation endpoint calls orchestration correctly
   - Results match expected format
   - Verbose mode includes all turns

4. **Test Health Endpoint**:
   - Healthy status when dependencies available
   - Degraded status when Ollama unavailable

### Test Tools

- **pytest** + **pytest-asyncio**: Existing test framework
- **httpx**: Async HTTP client for testing
- **FastAPI TestClient**: For testing without server

**Example Test Structure**:

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_generate_slogan_success(client: AsyncClient):
    """Test async slogan generation endpoint"""
    response = await client.post(
        "/api/v1/slogans/generate",
        json={"input": "coffee shop", "max_turns": 2}
    )
    assert response.status_code == 200
    data = response.json()
    assert "slogan" in data
    assert data["completion_reason"] in ["approved", "max_turns"]

@pytest.mark.asyncio
async def test_generate_slogan_timeout():
    """Test timeout handling for long-running generations"""
    # Test that 600s (10 minute) timeout is enforced
    # This test would use a mock to simulate timeout without waiting
    pass
```

---

## Dependencies (New)

Add to `pyproject.toml`:

```toml
[project]
dependencies = [
    # ... existing dependencies ...
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
]

[project.optional-dependencies]
dev = [
    # ... existing dev dependencies ...
    "httpx>=0.25.0",  # For API testing
]
```

---

## Out of Scope (Future Considerations)

The following are **NOT** included in this specification but may be considered for future versions:

1. **Authentication/Authorization**: API keys, OAuth2, JWT tokens
2. **Rate Limiting**: Per-client request throttling
3. **WebSocket/Streaming**: Real-time turn-by-turn updates
4. **Batch Processing**: Multiple slogans in one request
5. **Result Caching**: Cache results for identical inputs
6. **Database Persistence**: Store generation history
7. **Async Background Jobs**: Queue-based processing
8. **Multi-model Support**: Different models for writer/reviewer
9. **Custom Agent Prompts**: User-provided system prompts
10. **Metrics/Analytics**: Usage statistics, performance metrics

---

## Success Criteria

This specification is considered successfully implemented when:

1. ✅ All API endpoints return correct responses according to contracts
2. ✅ Request/response validation works correctly (422 for invalid input)
3. ✅ Error handling is comprehensive (503 for Ollama failures, etc.)
4. ✅ API reuses existing orchestration without duplication
5. ✅ OpenAPI documentation is complete and accurate
6. ✅ All API integration tests pass
7. ✅ No modifications to existing CLI or orchestration code
8. ✅ Constitution compliance maintained (code quality, testing, docs)
9. ✅ Developer can successfully integrate API into their application
10. ✅ Health check endpoint works for monitoring

---

## Constitution Compliance

### Code Quality
- All new code follows existing standards (ruff, mypy)
- Comprehensive docstrings on all public functions
- Type hints throughout
- Peer review required before merge

### Simplicity
- Reuse existing code, don't duplicate
- Start with simple REST (no WebSockets in v1)
- Clear separation: API layer only handles HTTP, orchestration handles business logic
- No premature optimization (YAGNI principle)

### Testing
- API integration tests for all endpoints
- Error scenario testing
- Contract validation tests
- Maintain 100% test pass rate

---

## Approval Checklist

Before implementation begins:

- [ ] User scenarios reviewed and approved
- [ ] API contracts reviewed and approved
- [ ] Architecture design reviewed (reuse strategy confirmed)
- [ ] Testing strategy approved
- [ ] Dependencies approved
- [ ] Success criteria clear and measurable
- [ ] Constitution compliance verified

---

**Version**: 1.0.0  
**Last Updated**: 2025-10-21  
**Status**: Draft (Pending Approval)
