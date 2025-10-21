# Implementation Plan: FastAPI REST API for Slogan Generation

**Branch**: `002-fastapi-api` | **Date**: 2025-10-21 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/002-fastapi-api/spec.md`  
**Dependencies**: Spec 001 (CLI implementation) must be complete and merged to master

## Summary

Build a FastAPI REST API that exposes the existing slogan generation functionality through HTTP endpoints. The API wraps the existing orchestration layer without modification, providing async endpoints for slogan generation, model discovery, health monitoring, and interactive documentation. Implementation uses thread pool executors to handle long-running Ollama operations (up to 10 minutes) without blocking concurrent requests. Architecture maintains strict separation: API layer handles HTTP concerns only, while business logic remains in the existing orchestration layer.

## Technical Context

**Language/Version**: Python 3.11+ (existing project standard)

**Primary Dependencies**:

- FastAPI (`fastapi>=0.104.0`) - Modern async web framework
- Uvicorn (`uvicorn[standard]>=0.24.0`) - ASGI server with production features
- httpx (`httpx>=0.25.0`) - Async HTTP client for testing (dev dependency)
- Existing dependencies: Microsoft Agent Framework, Ollama, Click, Pydantic

**Storage**: N/A (stateless API, reuses existing stateless orchestration)

**Testing**: pytest + pytest-asyncio (existing framework) + httpx for API integration tests

**Target Platform**: Server deployment (development: localhost, production: containerized or VM)

**Project Type**: Single project with dual interfaces (CLI + API), shared orchestration layer

**Performance Goals**:

- Support 10 concurrent slogan generation requests without blocking
- Response time: up to 10 minutes per generation (model/complexity dependent)
- Health check: < 100ms response time
- Model listing: < 1 second response time

**Constraints**:

- **No modifications to existing code**: CLI, orchestration, agents layers remain unchanged
- **Async-first design**: All I/O operations must be non-blocking
- **Timeout enforcement**: 600 second (10 minute) timeout per generation request
- **Development simplicity**: No authentication, rate limiting, or WebSockets in v1
- **Reuse over duplication**: Must call existing `orchestration.run_slogan_generation()`

**Scale/Scope**:

- Multi-user concurrent access (API endpoint)
- Four REST endpoints: Generate, Models, Health, Root
- New codebase: ~300-500 LOC estimated (API layer only)
- MVP feature set (4 user stories: 1 P1, 3 P2)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Code Quality Principle ✅ PASS

- **Documentation**: All API endpoints documented via FastAPI/OpenAPI (automatic)
- **Type Hints**: Pydantic schemas provide complete type safety for request/response
- **Linting**: Existing ruff configuration applies to new API code
- **Code Review**: Small, focused implementation per endpoint enables effective review
- **Testing**: API integration tests for all endpoints and error scenarios

**Justification**: FastAPI provides built-in OpenAPI documentation. Pydantic schemas enforce type safety. Clean layer separation enables straightforward testing.

### Simplicity Principle ✅ PASS

- **YAGNI Applied**: No auth, rate limiting, WebSockets, caching, or persistence in v1
- **Minimal New Dependencies**: Only FastAPI + Uvicorn (2 production dependencies)
- **No Duplication**: Reuses existing orchestration layer via function calls
- **Clear Architecture**: New API layer alongside existing CLI layer, both call orchestration
- **No Over-Engineering**: Simple REST endpoints with Pydantic validation, no complex state management

**Justification**: API layer is a thin HTTP wrapper around existing business logic. Thread pool executor pattern is standard for wrapping sync code in async endpoints. No premature optimization.

### Development Workflow ✅ PASS

- **Incremental Development**: Can implement endpoints independently (health → models → generate)
- **Small PRs**: Each endpoint can be developed, tested, and reviewed separately
- **Testability**: API endpoints testable with FastAPI TestClient, no external dependencies needed
- **Reuse**: Zero changes to existing tested code (orchestration, agents, CLI)

**Verdict**: ✅ **ALL GATES PASSED** - Proceed to Phase 0 Research

## Project Structure

### Documentation (this feature)

```text
specs/002-fastapi-api/
├── spec.md              # Feature specification (already created)
├── plan.md              # This file
├── contracts/           # Phase 1 output
│   └── api-interface.md # OpenAPI schemas and endpoint contracts
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
src/
├── agents/              # ✅ REUSE - No changes
├── orchestration/       # ✅ REUSE - No changes
├── config/              # ✅ REUSE - No changes
├── cli/                 # ✅ REUSE - No changes
└── api/                 # 🆕 NEW - FastAPI layer
    ├── __init__.py
    ├── main.py          # FastAPI app initialization, CORS, exception handlers
    ├── routes/
    │   ├── __init__.py
    │   ├── slogans.py   # POST /api/v1/slogans/generate endpoint
    │   ├── models.py    # GET /api/v1/models endpoint
    │   └── health.py    # GET /api/v1/health endpoint
    ├── schemas/
    │   ├── __init__.py
    │   ├── requests.py  # Pydantic request models (SloganRequest)
    │   └── responses.py # Pydantic response models (SloganResponse, etc.)
    ├── dependencies.py  # FastAPI dependencies (config injection)
    └── middleware.py    # CORS, logging, error handling

tests/
├── unit/                # ✅ Existing tests unchanged
├── integration/         # ✅ Existing tests unchanged
└── api/                 # 🆕 NEW - API integration tests
    ├── __init__.py
    ├── conftest.py      # Pytest fixtures (TestClient, mock config)
    ├── test_generate.py # Test POST /api/v1/slogans/generate
    ├── test_models.py   # Test GET /api/v1/models
    ├── test_health.py   # Test GET /api/v1/health
    └── test_errors.py   # Test error handling (422, 503, timeouts)

pyproject.toml           # Updated with FastAPI dependencies
README.md                # Updated with API usage examples
```

**Structure Decision**: Add new `src/api/` layer alongside existing layers. This maintains clean separation: CLI and API are both thin interfaces that call the same orchestration logic. No shared code between CLI and API layers (different concerns). Tests organized by layer for clarity.

## Phases

### Phase 0: Research & Dependencies ✅ FOUNDATION

**Goal**: Install FastAPI ecosystem and verify compatibility with existing project.

**Activities**:

1. **Dependency Analysis**:
   - Review FastAPI documentation for async patterns with sync orchestration
   - Confirm thread pool executor approach for wrapping `run_slogan_generation()`
   - Research Uvicorn production configuration (workers, timeouts)
   - Study httpx AsyncClient for testing async endpoints

2. **Install Dependencies**:
   ```bash
   uv add "fastapi>=0.104.0" "uvicorn[standard]>=0.24.0"
   uv add --dev "httpx>=0.25.0"
   ```

3. **Verify Environment**:
   - Confirm FastAPI installation with `python -c "import fastapi; print(fastapi.__version__)"`
   - Confirm Uvicorn installation with `uvicorn --version`
   - Run existing tests to ensure no regressions: `uv run pytest`

**Outputs**:
- Updated `pyproject.toml` with new dependencies
- Verified test suite still passes (64/64 tests)
- Confirmed Python 3.11+ environment compatible with FastAPI

**Success Criteria**:
- FastAPI and Uvicorn installed successfully
- Existing tests pass without modification
- No dependency conflicts

**Time Estimate**: 30 minutes

---

### Phase 1: API Foundation & Health Endpoint 🏗️ SCAFFOLDING

**Goal**: Create FastAPI application structure, implement health endpoint, verify async works.

**User Story**: US3 - Health Monitoring (Priority: P2)

**Activities**:

1. **Create API Structure**:
   - Create `src/api/` directory with `__init__.py`
   - Create `src/api/main.py` with basic FastAPI app:
     ```python
     from fastapi import FastAPI
     
     app = FastAPI(
         title="Slogan Writer-Reviewer API",
         version="1.0.0",
         description="Multi-agent slogan generation via Writer-Reviewer collaboration"
     )
     ```

2. **Configure CORS**:
   - Add CORS middleware in `main.py` for development origins
   - Make origins configurable via environment variable

3. **Implement Health Endpoint** (`src/api/routes/health.py`):
   - Create async health check route: `GET /api/v1/health`
   - Check Ollama connectivity asynchronously
   - Return structured JSON with status, version, timestamp, dependencies
   - Handle both healthy (200) and degraded (503) states

4. **Create Response Schemas** (`src/api/schemas/responses.py`):
   - `HealthResponse` Pydantic model
   - `DependencyStatus` model for Ollama status

5. **Root Endpoint** (`src/api/main.py`):
   - Implement `GET /` returning API metadata and documentation links
   - Simple synchronous endpoint (no external I/O)

6. **Test Basic API**:
   - Create `tests/api/conftest.py` with TestClient fixture
   - Test health endpoint (healthy and degraded scenarios)
   - Test root endpoint
   - Verify OpenAPI docs accessible at `/docs`

**Outputs**:
- Working FastAPI application with 2 endpoints
- Health monitoring functional
- Basic test infrastructure for API testing
- OpenAPI documentation auto-generated

**Success Criteria**:
- Health endpoint returns correct JSON schema
- CORS configured and working
- Tests pass for both endpoints
- `/docs` shows Swagger UI with endpoint documentation

**Time Estimate**: 2 hours

---

### Phase 2: Models Endpoint 📋 DATA ACCESS

**Goal**: Implement model discovery endpoint, reuse existing model listing logic.

**User Story**: US2 - Model Discovery (Priority: P2)

**Activities**:

1. **Create Models Route** (`src/api/routes/models.py`):
   - Implement `GET /api/v1/models` async endpoint
   - Reuse existing `get_available_models()` from config layer
   - Wrap sync model listing in thread pool executor (if needed)
   - Transform to API response format

2. **Create Request/Response Schemas**:
   - `ModelInfo` Pydantic model (name, display_name, is_default)
   - `ModelsResponse` model (models list, default_model, total_count)

3. **Error Handling**:
   - Handle Ollama unavailable (503 Service Unavailable)
   - Return structured error JSON

4. **Dependencies** (`src/api/dependencies.py`):
   - Create FastAPI dependency for config loading
   - Inject Ollama configuration into endpoints

5. **Testing** (`tests/api/test_models.py`):
   - Test successful model listing (200 OK)
   - Test Ollama unavailable scenario (503)
   - Verify response schema matches contract
   - Test default model indication

**Outputs**:
- Working models endpoint
- Dependency injection system for config
- API tests for model discovery

**Success Criteria**:
- Models endpoint returns list of available models
- Default model correctly indicated
- Error handling works for Ollama unavailable
- Tests pass for success and error scenarios

**Time Estimate**: 1.5 hours

---

### Phase 3: Generate Endpoint (Core) 🎯 CRITICAL PATH

**Goal**: Implement slogan generation endpoint with async wrapper around existing orchestration.

**User Story**: US1 - Programmatic Slogan Generation (Priority: P1)

**Activities**:

1. **Create Request Schema** (`src/api/schemas/requests.py`):
   - `SloganRequest` Pydantic model:
     - `input: str` (1-500 chars, required)
     - `model: str | None` (optional, default from config)
     - `max_turns: int | None` (1-10, optional, default 5)
     - `verbose: bool` (optional, default False)
   - Add field validators (string length, max_turns range)

2. **Create Response Schema** (`src/api/schemas/responses.py`):
   - `TurnInfo` model (turn_number, slogan, feedback, approved, timestamp)
   - `SloganResponse` model matching spec contract:
     - slogan, input, completion_reason, turn_count, model_name
     - total_duration_seconds, average_duration_per_turn
     - turns (list), created_at

3. **Implement Generate Route** (`src/api/routes/slogans.py`):
   - Create `POST /api/v1/slogans/generate` async endpoint
   - Implement thread pool executor pattern:
     ```python
     @router.post("/api/v1/slogans/generate")
     async def generate_slogan(request: SloganRequest):
         loop = asyncio.get_event_loop()
         result = await asyncio.wait_for(
             loop.run_in_executor(
                 None,
                 orchestration.run_slogan_generation,
                 request.input,
                 request.model
             ),
             timeout=600.0  # 10 minute timeout
         )
         return transform_to_api_response(result)
     ```
   - Transform `IterationSession` domain model to `SloganResponse`
   - Handle verbose mode (include/exclude turns)

4. **Error Handling**:
   - 422 Unprocessable Entity: Pydantic validation errors
   - 400 Bad Request: Invalid model name
   - 503 Service Unavailable: Ollama connection failure
   - 500 Internal Server Error: Unexpected errors
   - Handle `asyncio.TimeoutError` for 10-minute timeout

5. **Global Exception Handlers** (`src/api/main.py`):
   - Add exception handler for `asyncio.TimeoutError`
   - Add exception handler for Ollama connection errors
   - Ensure all errors return structured JSON

6. **Testing** (`tests/api/test_generate.py`):
   - Test successful generation (200 OK with full response)
   - Test with custom parameters (model, max_turns)
   - Test verbose mode (turns included)
   - Test validation errors (missing input, invalid max_turns)
   - Test invalid model (400 Bad Request)
   - Test Ollama unavailable (503)
   - Test timeout handling (mock long-running generation)

**Outputs**:
- Working slogan generation endpoint
- Complete request/response validation
- Comprehensive error handling
- Full test coverage for success and error paths

**Success Criteria**:
- Generate endpoint successfully calls existing orchestration
- Response matches API contract exactly
- All error scenarios handled correctly
- Timeout enforced at 600 seconds
- Tests pass for all acceptance scenarios from spec

**Time Estimate**: 3 hours

---

### Phase 4: Middleware & Configuration 🔧 POLISH

**Goal**: Add logging, error middleware, environment configuration.

**Activities**:

1. **Request/Response Logging** (`src/api/middleware.py`):
   - Log incoming requests (method, path, timestamp)
   - Log responses (status code, duration)
   - Generate request ID for tracing

2. **Error Handling Middleware**:
   - Catch unhandled exceptions
   - Return structured JSON error responses
   - Log errors with stack traces

3. **Environment Configuration**:
   - Add API-specific settings to config layer:
     - `API_HOST` (default: "0.0.0.0")
     - `API_PORT` (default: 8000)
     - `API_CORS_ORIGINS` (comma-separated list)
     - `API_REQUEST_TIMEOUT` (default: 630 seconds)
     - `API_GENERATION_TIMEOUT` (default: 600 seconds)
     - `API_WORKERS` (default: 4)
   - Update `src/config/settings.py` to load API settings

4. **Update Main App** (`src/api/main.py`):
   - Register all routers (slogans, models, health)
   - Apply middleware in correct order
   - Configure OpenAPI metadata (title, description, version, contact)
   - Add tags for endpoint grouping

5. **Testing** (`tests/api/test_errors.py`):
   - Test middleware logging
   - Test unhandled exception handling
   - Verify request IDs in responses

**Outputs**:
- Complete middleware stack
- Full environment configuration
- Production-ready error handling
- Comprehensive logging

**Success Criteria**:
- All requests logged with duration
- All errors return structured JSON
- Configuration loaded from environment
- Middleware tests pass

**Time Estimate**: 1.5 hours

---

### Phase 5: Integration Testing & Documentation 📝 VALIDATION

**Goal**: End-to-end testing, update documentation, verify all acceptance criteria.

**Activities**:

1. **Integration Tests** (`tests/api/test_integration.py`):
   - Test full request lifecycle (health → models → generate)
   - Test concurrent requests (simulate 3-5 parallel generations)
   - Verify async behavior (requests don't block each other)
   - Test API with real Ollama (not just mocks)

2. **Contract Validation**:
   - Verify OpenAPI schema matches spec
   - Export OpenAPI JSON: `curl http://localhost:8000/openapi.json`
   - Validate all response schemas with examples

3. **Update Documentation**:
   - Update `README.md` with API section:
     - Installation instructions (existing + FastAPI deps)
     - Running the API (development and production)
     - API endpoints with curl examples
     - Environment variables (API-specific)
   - Create API usage examples in README
   - Document timeout behavior and recommendations

4. **Manual Testing**:
   - Start API: `uvicorn src.api.main:app --reload`
   - Test via Swagger UI at `http://localhost:8000/docs`
   - Test via curl commands from spec
   - Verify ReDoc at `http://localhost:8000/redoc`

5. **Performance Verification**:
   - Test concurrent requests (10 parallel curl commands)
   - Verify timeout enforcement (mock 11-minute generation)
   - Check health endpoint response time (< 100ms)

**Outputs**:
- Complete integration test suite
- Updated README with API documentation
- Verified OpenAPI schema
- Manual test checklist completed

**Success Criteria**:
- All 10 success criteria from spec verified
- Integration tests pass
- Documentation complete and accurate
- Swagger UI shows all endpoints correctly
- Manual testing confirms all user stories work

**Time Estimate**: 2 hours

---

### Phase 6: Final Polish & Review ✨ PRODUCTION READY

**Goal**: Code quality checks, final review, prepare for merge.

**Activities**:

1. **Code Quality**:
   - Run linting: `uv run ruff check src/api tests/api`
   - Run type checking: `uv run mypy src/api`
   - Fix any linting or type errors
   - Ensure consistent formatting: `uv run ruff format src/api tests/api`

2. **Test Coverage**:
   - Run full test suite: `uv run pytest`
   - Verify all 64 existing tests still pass
   - Verify all new API tests pass
   - Check test coverage for API layer

3. **Documentation Review**:
   - Review all docstrings in API code
   - Verify OpenAPI descriptions are clear
   - Check README examples work
   - Proofread error messages

4. **Constitution Compliance**:
   - Verify no code duplication (orchestration reused, not duplicated)
   - Confirm simplicity (no premature optimization)
   - Check test quality (all endpoints covered)
   - Review PR checklist from spec

5. **Prepare for Merge**:
   - Commit all changes with clear messages
   - Update `CHANGELOG.md` if it exists
   - Tag commits by phase for review
   - Create PR description with testing instructions

**Outputs**:
- Clean, linted, type-checked code
- 100% test pass rate
- Complete documentation
- Merge-ready feature branch

**Success Criteria**:
- 0 ruff errors
- 0 mypy errors
- All tests pass (existing + new)
- Constitution compliance verified
- PR ready for review

**Time Estimate**: 1 hour

---

## Phase Dependencies

```
Phase 0 (Research)
    ↓
Phase 1 (Foundation) → Phase 2 (Models) → Phase 3 (Generate) → Phase 4 (Middleware) → Phase 5 (Testing) → Phase 6 (Polish)
                                             ↑
                                        CRITICAL PATH
```

**Critical Path**: Phase 3 (Generate Endpoint) is the core P1 user story and blocks final validation.

**Parallel Opportunities**: 
- Phase 1 and Phase 2 could be developed in parallel (different endpoints)
- Testing can begin as soon as each endpoint is complete (don't wait for Phase 5)

## Complexity Tracking

**No violations** - Constitution Check passed all gates. Architecture maintains simplicity through:

1. **Reuse over duplication**: API layer calls existing orchestration, no business logic in API
2. **Standard patterns**: Thread pool executor is well-established pattern for async/sync bridging
3. **Clear separation**: API layer only handles HTTP concerns (validation, serialization, routing)
4. **No premature optimization**: Simple REST API, deferred features (auth, rate limiting) to v2

## Risk Assessment

### Technical Risks

1. **Long-running requests (10 minutes)**:
   - **Risk**: Client timeouts, server resource exhaustion
   - **Mitigation**: Document timeout requirements, use async to avoid blocking, configure Uvicorn workers
   - **Severity**: Medium (user experience impact)

2. **Thread pool executor overhead**:
   - **Risk**: Thread pool might struggle with 10+ concurrent long-running operations
   - **Mitigation**: Test concurrent requests, configure worker count, document concurrency limits
   - **Severity**: Low (10 concurrent is reasonable for MVP)

3. **Error handling completeness**:
   - **Risk**: Unexpected errors might leak internal details or cause crashes
   - **Mitigation**: Global exception handler, structured error responses, comprehensive testing
   - **Severity**: Medium (API stability)

### Process Risks

1. **Scope creep** (adding auth, rate limiting, WebSockets):
   - **Risk**: Delays MVP delivery
   - **Mitigation**: Strict adherence to spec, explicit out-of-scope list
   - **Severity**: Low (team discipline)

2. **Integration with existing code**:
   - **Risk**: Assumptions about orchestration layer behavior
   - **Mitigation**: Thorough testing with real Ollama, no modifications to existing code
   - **Severity**: Low (orchestration is well-tested)

## Timeline Estimate

**Total Effort**: ~11.5 hours

- Phase 0: 0.5 hours (research & dependencies)
- Phase 1: 2 hours (foundation & health)
- Phase 2: 1.5 hours (models endpoint)
- Phase 3: 3 hours (generate endpoint - critical)
- Phase 4: 1.5 hours (middleware & config)
- Phase 5: 2 hours (integration testing & docs)
- Phase 6: 1 hour (polish & review)

**Development Schedule** (assuming 4 hours/day):
- Day 1: Phase 0-1 (foundation)
- Day 2: Phase 2-3 (endpoints)
- Day 3: Phase 4-6 (polish & testing)

**Recommendation**: Complete Phase 3 (generate endpoint) as early as possible to unblock validation and testing.

## Next Steps

1. ✅ Create this plan document
2. ⏳ Create contracts document (`specs/002-fastapi-api/contracts/api-interface.md`)
3. ⏳ Generate tasks breakdown with `/speckit.tasks` command
4. ⏳ Commit all planning documents to master
5. ⏳ Create feature branch `002-fastapi-api`
6. ⏳ Begin Phase 0 implementation

**Recommendation**: Review and approve this plan before creating tasks breakdown. Confirm async strategy and timeout values are acceptable.

---

**Status**: Draft (Pending Approval)  
**Last Updated**: 2025-10-21  
**Next**: Create contracts document and tasks breakdown
