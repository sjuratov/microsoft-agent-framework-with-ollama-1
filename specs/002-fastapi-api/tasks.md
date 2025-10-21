# Task Breakdown: FastAPI REST API for Slogan Generation

**Branch**: `002-fastapi-api` | **Date**: 2025-10-21 | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md) | **Contracts**: [contracts/api-interface.md](./contracts/api-interface.md)

## Overview

This document breaks down the implementation of the FastAPI REST API into atomic, testable tasks. Each task is self-contained and includes clear acceptance criteria. Tasks are organized by phase from the implementation plan.

**Total Estimated Effort**: 11.5 hours across 6 phases

---

## Phase 0: Research & Dependencies (0.5 hours)

### T001: Install FastAPI Dependencies

**Description**: Install FastAPI, Uvicorn, and httpx (dev) dependencies using uv package manager.

**Dependencies**: None

**Acceptance Criteria**:
- [ ] `fastapi>=0.104.0` installed
- [ ] `uvicorn[standard]>=0.24.0` installed
- [ ] `httpx>=0.25.0` installed as dev dependency
- [ ] `pyproject.toml` updated with new dependencies
- [ ] Can import FastAPI: `python -c "import fastapi; print(fastapi.__version__)"`
- [ ] Can run Uvicorn: `uvicorn --version`

**Commands**:
```bash
uv add "fastapi>=0.104.0" "uvicorn[standard]>=0.24.0"
uv add --dev "httpx>=0.25.0"
```

**Time Estimate**: 15 minutes

---

### T002: Verify Existing Tests Pass

**Description**: Run existing test suite to ensure no regressions from new dependencies.

**Dependencies**: T001

**Acceptance Criteria**:
- [ ] All 64 existing tests pass without modification
- [ ] 0 ruff errors
- [ ] 0 mypy errors
- [ ] No dependency conflicts reported

**Commands**:
```bash
uv run pytest
uv run ruff check .
uv run mypy src/
```

**Time Estimate**: 15 minutes

---

## Phase 1: API Foundation & Health Endpoint (2 hours)

### T003: Create API Directory Structure

**Description**: Create the `src/api/` directory with initial module structure and empty files.

**Dependencies**: T002

**Acceptance Criteria**:
- [ ] Directory `src/api/` created
- [ ] File `src/api/__init__.py` created (empty)
- [ ] File `src/api/main.py` created with basic FastAPI app
- [ ] Directory `src/api/routes/` created
- [ ] File `src/api/routes/__init__.py` created (empty)
- [ ] Directory `src/api/schemas/` created
- [ ] File `src/api/schemas/__init__.py` created (empty)
- [ ] Python can import: `python -c "from src.api.main import app"`

**Files to Create**:
- `src/api/__init__.py`
- `src/api/main.py`
- `src/api/routes/__init__.py`
- `src/api/schemas/__init__.py`

**Time Estimate**: 15 minutes

---

### T004: Implement Basic FastAPI Application

**Description**: Create the main FastAPI app instance with metadata and minimal configuration.

**Dependencies**: T003

**Acceptance Criteria**:
- [ ] FastAPI app created with title "Slogan Writer-Reviewer API"
- [ ] App version set to "1.0.0"
- [ ] App description set per contract
- [ ] CORS middleware configured with development origins
- [ ] CORS origins configurable via `API_CORS_ORIGINS` environment variable
- [ ] App can start: `uvicorn src.api.main:app --reload`
- [ ] `/docs` endpoint shows Swagger UI
- [ ] `/redoc` endpoint shows ReDoc documentation
- [ ] `/openapi.json` returns OpenAPI schema

**Contract Reference**: contracts/api-interface.md - API Metadata section

**Time Estimate**: 30 minutes

---

### T005: Create Response Schemas for Health and Root

**Description**: Implement Pydantic models for HealthResponse, DependencyStatus, and RootResponse.

**Dependencies**: T003

**Acceptance Criteria**:
- [ ] File `src/api/schemas/responses.py` created
- [ ] `DependencyStatus` model implemented with fields: connected, url, response_time_ms, error
- [ ] `HealthResponse` model implemented with fields: status, version, timestamp, dependencies
- [ ] `RootResponse` model implemented with fields: name, version, description, documentation
- [ ] All models use proper type hints (str, bool, dict, datetime, Literal)
- [ ] All models have field descriptions
- [ ] All models have example values in Field()
- [ ] Models pass mypy type checking

**Contract Reference**: contracts/api-interface.md - Pydantic Models section (responses.py)

**Time Estimate**: 30 minutes

---

### T006: Implement Root Endpoint

**Description**: Create GET / endpoint returning API metadata and documentation links.

**Dependencies**: T004, T005

**Acceptance Criteria**:
- [ ] Endpoint `GET /` implemented in `src/api/main.py`
- [ ] Returns `RootResponse` schema
- [ ] Returns 200 OK with JSON body
- [ ] Response includes name, version, description, documentation links
- [ ] Documentation links include: swagger (/docs), redoc (/redoc), openapi (/openapi.json)
- [ ] Endpoint is synchronous (no async)
- [ ] Endpoint visible in Swagger UI with correct schema

**Contract Reference**: contracts/api-interface.md - Root Endpoint section

**Time Estimate**: 15 minutes

---

### T007: Implement Health Check Endpoint

**Description**: Create GET /api/v1/health endpoint with Ollama connectivity check.

**Dependencies**: T004, T005

**Acceptance Criteria**:
- [ ] File `src/api/routes/health.py` created
- [ ] Router with prefix `/api/v1` and tag `["monitoring"]` created
- [ ] Endpoint `GET /api/v1/health` implemented (async)
- [ ] Checks Ollama connectivity using httpx.AsyncClient
- [ ] Returns 200 OK with status "healthy" when Ollama connected
- [ ] Returns 503 Service Unavailable with status "degraded" when Ollama down
- [ ] Response includes: status, version, timestamp, dependencies.ollama
- [ ] Ollama dependency includes: connected, url, response_time_ms (if connected), error (if not)
- [ ] Endpoint registered in `src/api/main.py`
- [ ] Endpoint visible in Swagger UI under "monitoring" tag

**Contract Reference**: contracts/api-interface.md - Health Check section

**Time Estimate**: 45 minutes

---

### T008: Create API Test Infrastructure

**Description**: Set up pytest fixtures and test structure for API testing.

**Dependencies**: T003

**Acceptance Criteria**:
- [ ] Directory `tests/api/` created
- [ ] File `tests/api/__init__.py` created (empty)
- [ ] File `tests/api/conftest.py` created
- [ ] Pytest fixture `client` created using FastAPI TestClient
- [ ] Fixture provides clean TestClient instance for each test
- [ ] Can import test client: `from tests.api.conftest import client`
- [ ] Sample test runs successfully: `pytest tests/api/conftest.py -v`

**Files to Create**:
- `tests/api/__init__.py`
- `tests/api/conftest.py`

**Time Estimate**: 20 minutes

---

### T009: Test Root and Health Endpoints

**Description**: Write integration tests for root and health endpoints.

**Dependencies**: T006, T007, T008

**Acceptance Criteria**:
- [ ] File `tests/api/test_health.py` created
- [ ] Test `test_health_endpoint_healthy` - verifies 200 OK when Ollama available
- [ ] Test `test_health_endpoint_degraded` - verifies 503 when Ollama unavailable (mock)
- [ ] Test `test_health_response_schema` - validates response matches contract
- [ ] Test `test_root_endpoint` - verifies GET / returns correct metadata
- [ ] Test `test_root_response_schema` - validates response includes documentation links
- [ ] All tests pass: `pytest tests/api/test_health.py -v`
- [ ] Test coverage includes success and failure scenarios

**Contract Reference**: contracts/api-interface.md - Root Endpoint, Health Check sections

**Time Estimate**: 25 minutes

---

## Phase 2: Models Endpoint (1.5 hours)

### T010: Create Dependencies Module

**Description**: Implement FastAPI dependency for injecting configuration.

**Dependencies**: T004

**Acceptance Criteria**:
- [ ] File `src/api/dependencies.py` created
- [ ] Function `get_config()` implemented as FastAPI dependency
- [ ] Function returns config instance from `src.config.settings`
- [ ] Function can be used with `Depends(get_config)` in route handlers
- [ ] Function properly typed with return type annotation

**Time Estimate**: 15 minutes

---

### T011: Implement Models Endpoint

**Description**: Create GET /api/v1/models endpoint that lists available Ollama models.

**Dependencies**: T010, T005

**Acceptance Criteria**:
- [ ] File `src/api/routes/models.py` created
- [ ] Router with prefix `/api/v1` and tag `["models"]` created
- [ ] Endpoint `GET /api/v1/models` implemented (async)
- [ ] Reuses `get_available_models()` from config layer
- [ ] Wraps sync model listing in thread pool executor if needed
- [ ] Returns `ModelsResponse` schema (models, default_model, total_count)
- [ ] Returns 200 OK with list of models
- [ ] Returns 503 Service Unavailable if Ollama unavailable
- [ ] Each model includes: name, display_name, is_default
- [ ] Endpoint registered in `src/api/main.py`
- [ ] Endpoint visible in Swagger UI under "models" tag

**Contract Reference**: contracts/api-interface.md - List Models section

**Time Estimate**: 45 minutes

---

### T012: Create Response Schemas for Models

**Description**: Implement Pydantic models for ModelsResponse and ModelInfo.

**Dependencies**: T005

**Acceptance Criteria**:
- [ ] `ModelInfo` model added to `src/api/schemas/responses.py`
- [ ] Fields: name (str), display_name (str), is_default (bool)
- [ ] `ModelsResponse` model added to same file
- [ ] Fields: models (list[ModelInfo]), default_model (str), total_count (int)
- [ ] All fields have descriptions and examples
- [ ] Models pass mypy type checking
- [ ] Models match contract schema exactly

**Contract Reference**: contracts/api-interface.md - Pydantic Models section (ModelsResponse)

**Time Estimate**: 15 minutes

---

### T013: Test Models Endpoint

**Description**: Write integration tests for models endpoint.

**Dependencies**: T011, T012

**Acceptance Criteria**:
- [ ] File `tests/api/test_models.py` created
- [ ] Test `test_list_models_success` - verifies 200 OK with model list
- [ ] Test `test_list_models_response_schema` - validates response matches contract
- [ ] Test `test_default_model_indicated` - confirms is_default=true for default model
- [ ] Test `test_models_ollama_unavailable` - verifies 503 when Ollama down (mock)
- [ ] Test `test_models_total_count` - validates count matches list length
- [ ] All tests pass: `pytest tests/api/test_models.py -v`

**Contract Reference**: contracts/api-interface.md - List Models section

**Time Estimate**: 35 minutes

---

## Phase 3: Generate Endpoint - CRITICAL PATH (3 hours)

### T014: Create Request Schemas

**Description**: Implement Pydantic model for SloganRequest with validation.

**Dependencies**: T003

**Acceptance Criteria**:
- [ ] File `src/api/schemas/requests.py` created
- [ ] `SloganRequest` model implemented
- [ ] Field `input`: str, required, minLength=1, maxLength=500
- [ ] Field `model`: str | None, optional, default None
- [ ] Field `max_turns`: int, optional, ge=1, le=10, default 5
- [ ] Field `verbose`: bool, optional, default False
- [ ] All fields have descriptions and examples
- [ ] Model passes mypy type checking
- [ ] Pydantic validation enforces constraints (string length, integer range)

**Contract Reference**: contracts/api-interface.md - Pydantic Models section (SloganRequest)

**Time Estimate**: 20 minutes

---

### T015: Create Response Schemas for Generate

**Description**: Implement Pydantic models for SloganResponse, TurnInfo, and QueuedResponse.

**Dependencies**: T005

**Acceptance Criteria**:
- [ ] `TurnInfo` model added to `src/api/schemas/responses.py`
- [ ] Fields: turn_number (int), slogan (str), feedback (str | None), approved (bool), timestamp (datetime)
- [ ] `SloganResponse` model added to same file
- [ ] Fields: slogan, input, completion_reason, turn_count, model_name, total_duration_seconds, average_duration_per_turn, turns, created_at, request_id
- [ ] `QueuedResponse` model added to same file
- [ ] Fields: request_id (UUID), status (Literal["queued"]), estimated_wait_seconds (int), message (str)
- [ ] All fields properly typed (UUID, datetime, Literal, lists)
- [ ] All fields have descriptions and examples
- [ ] Models match contract schema exactly

**Contract Reference**: contracts/api-interface.md - Pydantic Models section (SloganResponse, TurnInfo, QueuedResponse)

**Time Estimate**: 30 minutes

---

### T016: Implement Generate Endpoint - Core Logic

**Description**: Create POST /api/v1/slogans/generate endpoint with async wrapper.

**Dependencies**: T014, T015, T010

**Acceptance Criteria**:
- [ ] File `src/api/routes/slogans.py` created
- [ ] Router with prefix `/api/v1` and tag `["slogans"]` created
- [ ] Endpoint `POST /api/v1/slogans/generate` implemented (async)
- [ ] Uses thread pool executor to wrap `orchestration.run_slogan_generation()`
- [ ] Uses `asyncio.wait_for()` with 600 second timeout
- [ ] Accepts `SloganRequest` as request body
- [ ] Returns `SloganResponse` on success (200 OK)
- [ ] Transforms `IterationSession` domain model to API response
- [ ] Includes all required fields in response (slogan, input, completion_reason, etc.)
- [ ] Handles verbose mode: includes turns if verbose=true, omits if false
- [ ] Uses injected config for default model if not specified
- [ ] Endpoint registered in `src/api/main.py`

**Contract Reference**: contracts/api-interface.md - Generate Slogan section

**Time Estimate**: 60 minutes

---

### T017: Implement Generate Endpoint - Error Handling

**Description**: Add comprehensive error handling to generate endpoint.

**Dependencies**: T016

**Acceptance Criteria**:
- [ ] Returns 422 Unprocessable Entity for Pydantic validation errors (automatic)
- [ ] Returns 400 Bad Request for invalid model name with available models list
- [ ] Returns 503 Service Unavailable for Ollama connection errors
- [ ] Returns 500 Internal Server Error for unexpected errors
- [ ] Handles `asyncio.TimeoutError` and returns appropriate error
- [ ] All error responses include structured JSON with "detail" field
- [ ] Error messages are clear and actionable
- [ ] Errors logged with appropriate level (ERROR for 500, WARNING for others)

**Contract Reference**: contracts/api-interface.md - Generate Slogan section (error responses)

**Time Estimate**: 30 minutes

---

### T018: Test Generate Endpoint - Success Cases

**Description**: Write integration tests for successful slogan generation.

**Dependencies**: T016

**Acceptance Criteria**:
- [ ] File `tests/api/test_generate.py` created
- [ ] Test `test_generate_slogan_success` - verifies 200 OK with complete response
- [ ] Test `test_generate_response_schema` - validates response matches contract
- [ ] Test `test_generate_with_custom_model` - tests model parameter
- [ ] Test `test_generate_with_max_turns` - tests max_turns parameter
- [ ] Test `test_generate_verbose_mode` - verifies turns included when verbose=true
- [ ] Test `test_generate_non_verbose_mode` - verifies turns omitted when verbose=false
- [ ] Test `test_generate_completion_reasons` - tests approved, max_turns, error reasons
- [ ] All tests pass with real or mocked orchestration

**Contract Reference**: contracts/api-interface.md - Generate Slogan section (200 OK)

**Time Estimate**: 45 minutes

---

### T019: Test Generate Endpoint - Error Cases

**Description**: Write integration tests for error scenarios.

**Dependencies**: T017

**Acceptance Criteria**:
- [ ] File `tests/api/test_errors.py` created (or add to test_generate.py)
- [ ] Test `test_generate_missing_input` - verifies 422 for missing required field
- [ ] Test `test_generate_input_too_short` - verifies 422 for empty string
- [ ] Test `test_generate_input_too_long` - verifies 422 for 501+ character input
- [ ] Test `test_generate_invalid_max_turns` - verifies 422 for max_turns < 1 or > 10
- [ ] Test `test_generate_invalid_model` - verifies 400 for non-existent model
- [ ] Test `test_generate_ollama_unavailable` - verifies 503 when Ollama down (mock)
- [ ] Test `test_generate_timeout` - verifies timeout handling for 600+ second generation (mock)
- [ ] All error responses include correct status codes and detail messages

**Contract Reference**: contracts/api-interface.md - Generate Slogan section (error responses)

**Time Estimate**: 45 minutes

---

## Phase 4: Middleware & Configuration (1.5 hours)

### T020: Create Middleware Module

**Description**: Implement request/response logging and error handling middleware.

**Dependencies**: T004

**Acceptance Criteria**:
- [ ] File `src/api/middleware.py` created
- [ ] Function `log_requests()` middleware implemented
- [ ] Logs incoming requests: method, path, timestamp
- [ ] Logs responses: status code, duration in milliseconds
- [ ] Generates UUID v4 request ID for each request
- [ ] Adds `X-Request-ID` header to all responses
- [ ] Middleware registered in `src/api/main.py`
- [ ] Request ID appears in logs for correlation

**Time Estimate**: 30 minutes

---

### T021: Implement Global Exception Handler

**Description**: Add global exception handler for unhandled errors.

**Dependencies**: T004

**Acceptance Criteria**:
- [ ] Exception handler for `Exception` added to `src/api/main.py`
- [ ] Catches all unhandled exceptions
- [ ] Returns 500 Internal Server Error with structured JSON
- [ ] Logs exception with full stack trace at ERROR level
- [ ] Includes request ID in error response
- [ ] Does not leak internal details in production
- [ ] Error response matches contract format ({"detail": "message"})

**Contract Reference**: contracts/api-interface.md - Error Handling Conventions

**Time Estimate**: 20 minutes

---

### T022: Add API Configuration Settings

**Description**: Update config layer with API-specific environment variables.

**Dependencies**: T004

**Acceptance Criteria**:
- [ ] File `src/config/settings.py` updated with API settings
- [ ] Setting `API_HOST`: str, default "0.0.0.0"
- [ ] Setting `API_PORT`: int, default 8000
- [ ] Setting `API_CORS_ORIGINS`: list[str], comma-separated, default "http://localhost:3000,http://localhost:8080"
- [ ] Setting `API_REQUEST_TIMEOUT`: int, default 630 (seconds)
- [ ] Setting `API_GENERATION_TIMEOUT`: int, default 600 (seconds)
- [ ] Setting `API_WORKERS`: int, default 4
- [ ] All settings loaded from environment variables
- [ ] Settings have docstrings explaining purpose
- [ ] Settings accessible via config instance

**Contract Reference**: spec.md - Configuration section

**Time Estimate**: 20 minutes

---

### T023: Update Main App with All Routers and Middleware

**Description**: Register all routers and apply middleware in correct order.

**Dependencies**: T020, T021, T022, T007, T011, T016

**Acceptance Criteria**:
- [ ] All routers registered in `src/api/main.py`:
  - health router from `src/api/routes/health.py`
  - models router from `src/api/routes/models.py`
  - slogans router from `src/api/routes/slogans.py`
- [ ] CORS middleware applied first
- [ ] Request logging middleware applied after CORS
- [ ] Global exception handler registered
- [ ] OpenAPI metadata complete (title, description, version, contact)
- [ ] OpenAPI tags defined for grouping: monitoring, models, slogans, info
- [ ] All endpoints appear in Swagger UI with correct tags
- [ ] `/openapi.json` schema complete and valid

**Contract Reference**: contracts/api-interface.md - API Metadata section

**Time Estimate**: 20 minutes

---

### T024: Test Middleware and Error Handling

**Description**: Write tests for middleware functionality.

**Dependencies**: T020, T021

**Acceptance Criteria**:
- [ ] Test `test_request_id_in_headers` - verifies X-Request-ID present in all responses
- [ ] Test `test_request_id_unique` - confirms each request gets unique ID
- [ ] Test `test_cors_headers` - validates CORS headers present
- [ ] Test `test_global_exception_handler` - triggers unhandled exception, verifies 500 response
- [ ] Test `test_error_response_format` - validates all errors return {"detail": "..."} format
- [ ] Test `test_request_logging` - confirms requests logged (check logs or use mock)
- [ ] All tests pass: `pytest tests/api/ -v -k middleware`

**Time Estimate**: 20 minutes

---

## Phase 5: Integration Testing & Documentation (2 hours)

### T025: Create Integration Test Suite

**Description**: Write end-to-end tests covering full request lifecycle.

**Dependencies**: T023

**Acceptance Criteria**:
- [ ] File `tests/api/test_integration.py` created
- [ ] Test `test_full_lifecycle` - health → models → generate in sequence
- [ ] Test `test_concurrent_requests` - 3-5 parallel generate requests don't block
- [ ] Test `test_async_behavior` - verifies requests processed concurrently
- [ ] Test `test_with_real_ollama` - end-to-end test with real Ollama (optional, can skip in CI)
- [ ] Test `test_openapi_schema_valid` - validates /openapi.json is valid OpenAPI 3.1.0
- [ ] All tests pass: `pytest tests/api/test_integration.py -v`

**Time Estimate**: 45 minutes

---

### T026: Validate API Contracts

**Description**: Verify all endpoints match the contract specifications exactly.

**Dependencies**: T023

**Acceptance Criteria**:
- [ ] Export OpenAPI schema: `curl http://localhost:8000/openapi.json > openapi-export.json`
- [ ] Verify all 4 endpoints present: /, /api/v1/health, /api/v1/models, /api/v1/slogans/generate
- [ ] Compare schemas with contracts/api-interface.md - all fields match
- [ ] Test all example requests from contract work correctly
- [ ] All response schemas include required fields
- [ ] All HTTP status codes used correctly per contract
- [ ] All error responses follow contract format

**Contract Reference**: contracts/api-interface.md - all sections

**Time Estimate**: 30 minutes

---

### T027: Update README with API Documentation

**Description**: Add comprehensive API usage section to README.md.

**Dependencies**: T023

**Acceptance Criteria**:
- [ ] `README.md` updated with new "API Usage" section
- [ ] Installation instructions include FastAPI dependencies
- [ ] Running the API documented:
  - Development: `uvicorn src.api.main:app --reload`
  - Production: `uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4`
- [ ] All 4 endpoints documented with curl examples
- [ ] Environment variables documented (API_* settings)
- [ ] Timeout behavior explained (10 minute max per request)
- [ ] Links to Swagger UI (/docs) and ReDoc (/redoc)
- [ ] Example request/response for generate endpoint
- [ ] Troubleshooting section (Ollama unavailable, timeouts)

**Time Estimate**: 30 minutes

---

### T028: Manual Testing Checklist

**Description**: Perform manual testing via Swagger UI and curl.

**Dependencies**: T023

**Acceptance Criteria**:
- [ ] Start API: `uvicorn src.api.main:app --reload`
- [ ] Verify Swagger UI accessible at http://localhost:8000/docs
- [ ] Test GET / via Swagger UI - returns metadata
- [ ] Test GET /api/v1/health via Swagger UI - returns healthy status
- [ ] Test GET /api/v1/models via Swagger UI - returns model list
- [ ] Test POST /api/v1/slogans/generate via Swagger UI - generates slogan
- [ ] Test with verbose=true - response includes turns
- [ ] Test with verbose=false - response excludes turns
- [ ] Test with invalid input - returns 422 validation error
- [ ] Test with invalid model - returns 400 error
- [ ] Stop Ollama and test - returns 503 errors appropriately
- [ ] Verify ReDoc accessible at http://localhost:8000/redoc
- [ ] All manual tests documented in checklist

**Time Estimate**: 15 minutes

---

## Phase 6: Final Polish & Review (1 hour)

### T029: Run Code Quality Checks

**Description**: Run linting and type checking on all API code.

**Dependencies**: T023

**Acceptance Criteria**:
- [ ] Run linting: `uv run ruff check src/api tests/api` - 0 errors
- [ ] Run formatting: `uv run ruff format src/api tests/api` - all files formatted
- [ ] Run type checking: `uv run mypy src/api` - 0 errors
- [ ] Fix any linting or type errors found
- [ ] Verify consistent code style across all API files
- [ ] All docstrings present and well-formatted

**Time Estimate**: 20 minutes

---

### T030: Run Full Test Suite

**Description**: Execute complete test suite including existing and new tests.

**Dependencies**: T029

**Acceptance Criteria**:
- [ ] Run all tests: `uv run pytest` - all pass
- [ ] Verify all 64 existing tests still pass (no regressions)
- [ ] Verify all new API tests pass (health, models, generate, errors, integration)
- [ ] Check test coverage for API layer: `pytest --cov=src/api tests/api/`
- [ ] Test coverage > 80% for API layer
- [ ] No flaky tests (run multiple times to confirm)

**Time Estimate**: 15 minutes

---

### T031: Final Constitution Compliance Check

**Description**: Verify implementation meets constitution principles.

**Dependencies**: T030

**Acceptance Criteria**:
- [ ] **Code Quality**: All API code has docstrings, type hints, passes linting/type checking
- [ ] **Simplicity**: No code duplication - orchestration reused, not duplicated
- [ ] **YAGNI**: No premature optimization - no auth, rate limiting, WebSockets in v1
- [ ] **Testing**: All endpoints have test coverage for success and error cases
- [ ] **Documentation**: README updated, OpenAPI auto-generated, code well-commented
- [ ] **Architecture**: Clean separation - API layer only handles HTTP concerns
- [ ] Constitution compliance checklist complete

**Time Estimate**: 10 minutes

---

### T032: Prepare for Merge

**Description**: Final commit and PR preparation.

**Dependencies**: T031

**Acceptance Criteria**:
- [ ] All changes committed with clear commit messages
- [ ] Commits organized logically (by phase or feature)
- [ ] Branch up to date with master: `git merge master`
- [ ] No merge conflicts
- [ ] Final test run passes on merged code
- [ ] PR description drafted with:
  - Summary of changes
  - Link to spec, plan, contracts
  - Testing instructions
  - Breaking changes (none expected)
  - Deployment notes
- [ ] Branch ready for code review

**Time Estimate**: 15 minutes

---

## Task Dependencies Graph

```
T001 (Install Dependencies)
  ↓
T002 (Verify Tests)
  ↓
T003 (Create Structure) → T008 (Test Infra)
  ↓                          ↓
T004 (Basic App) → T006 (Root) → T009 (Test Root/Health)
  ↓                ↓                   ↓
T005 (Schemas) → T007 (Health) ------+
  ↓                                    
T010 (Dependencies) → T011 (Models) → T012 (Model Schemas) → T013 (Test Models)
  ↓
T014 (Request Schemas) → T016 (Generate Core) → T017 (Generate Errors) → T018 (Test Generate Success)
  ↓                          ↓                                              ↓
T015 (Response Schemas) ----+                                              T019 (Test Generate Errors)

T004 → T020 (Middleware) → T024 (Test Middleware)
  ↓      ↓
T021 (Exception Handler)
  ↓
T022 (Config Settings)
  ↓
T023 (Register All) → T025 (Integration Tests)
                    → T026 (Validate Contracts)
                    → T027 (Update README)
                    → T028 (Manual Testing)
                    → T029 (Code Quality)
                    → T030 (Full Test Suite)
                    → T031 (Constitution Check)
                    → T032 (Prepare Merge)
```

**Critical Path**: T001 → T002 → T003 → T004 → T014 → T015 → T016 → T017 → T023 → T029 → T030 → T032

---

## Testing Checklist

### Functional Tests
- [ ] Root endpoint returns correct metadata
- [ ] Health endpoint returns healthy when Ollama up
- [ ] Health endpoint returns degraded when Ollama down
- [ ] Models endpoint returns list of available models
- [ ] Generate endpoint creates slogan with default parameters
- [ ] Generate endpoint respects custom model parameter
- [ ] Generate endpoint respects max_turns parameter
- [ ] Generate endpoint includes turns when verbose=true
- [ ] Generate endpoint excludes turns when verbose=false

### Error Handling Tests
- [ ] Missing required field returns 422
- [ ] Input too short returns 422
- [ ] Input too long (>500 chars) returns 422
- [ ] max_turns < 1 returns 422
- [ ] max_turns > 10 returns 422
- [ ] Invalid model name returns 400
- [ ] Ollama unavailable returns 503
- [ ] Timeout after 600 seconds handled correctly
- [ ] Unhandled exception returns 500

### Non-Functional Tests
- [ ] Request ID present in all responses (X-Request-ID header)
- [ ] CORS headers present in all responses
- [ ] Request/response logged with duration
- [ ] Concurrent requests don't block each other
- [ ] OpenAPI schema valid (3.1.0)
- [ ] Swagger UI accessible and functional
- [ ] ReDoc accessible and functional

### Integration Tests
- [ ] Full lifecycle test (health → models → generate)
- [ ] Multiple concurrent generate requests succeed
- [ ] Real Ollama integration works end-to-end

---

## Success Criteria Summary

All tasks complete and passing when:

1. ✅ All 32 tasks marked complete with acceptance criteria met
2. ✅ All tests pass (existing 64 + new API tests)
3. ✅ 0 ruff errors, 0 mypy errors
4. ✅ All 4 endpoints functional and tested
5. ✅ API contracts validated against specification
6. ✅ README updated with API documentation
7. ✅ Manual testing checklist complete
8. ✅ Constitution compliance verified
9. ✅ PR ready for review
10. ✅ Feature meets all 10 success criteria from spec.md

---

**Total Tasks**: 32  
**Total Estimated Time**: 11.5 hours  
**Status**: Ready for Implementation  
**Last Updated**: 2025-10-21

**Next Step**: Commit this tasks document, then begin T001 (Install Dependencies)
