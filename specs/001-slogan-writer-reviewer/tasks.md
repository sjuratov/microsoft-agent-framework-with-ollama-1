# Tasks: Iterative Slogan Writer-Reviewer Agent System

**Input**: Design documents from `/specs/001-slogan-writer-reviewer/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli-interface.md  
**Generated**: 2025-10-19

**Tests**: Not requested in specification - focusing on implementation tasks only.

**Organization**: Tasks are grouped by user story (P1, P2, P3) to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure per plan.md

- [ ] T001 Create project directory structure: src/{agents,orchestration,cli,config}/, tests/{unit,integration}/
- [ ] T002 Initialize Python project with uv: create pyproject.toml with dependencies (agent-framework, ollama, click, pydantic, pydantic-settings)
- [ ] T003 [P] Create .python-version file with Python 3.11+ requirement
- [ ] T004 [P] Configure Ruff for linting in pyproject.toml (line-length=100, extend-select=["I", "N", "UP"])
- [ ] T005 [P] Configure mypy for type checking in pyproject.toml (strict=true, python_version="3.11")
- [ ] T006 [P] Create README.md with project overview, installation instructions, and quick start examples
- [ ] T007 [P] Create .gitignore for Python (venv, **pycache**, .env, etc.)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data models and configuration that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T008 [P] Implement CompletionReason enum in src/orchestration/models.py
- [ ] T009 [P] Implement AgentRole enum in src/orchestration/models.py
- [ ] T010 [P] Implement Turn model in src/orchestration/models.py with validation (turn_number 1-10, slogan max 500 chars)
- [ ] T011 Implement IterationSession model in src/orchestration/models.py with add_turn() and complete() methods
- [ ] T012 [P] Implement WorkflowMessage model in src/orchestration/models.py
- [ ] T013 [P] Implement OllamaConfig settings in src/config/settings.py with BaseSettings and SLOGAN_ env prefix
- [ ] T014 [P] Create src/config/\_\_init\_\_.py to export OllamaConfig
- [ ] T015 [P] Create src/orchestration/\_\_init\_\_.py to export models

**Checkpoint**: Foundation ready - all data models available for user story implementation

---

## Phase 3: User Story 1 - Basic Slogan Generation (Priority: P1) 🎯 MVP

**Goal**: Enable users to provide input via CLI and receive a final approved slogan through Writer-Reviewer collaboration (default 5 turns, max 10)

**Independent Test**: Run `slogan-gen generate "eco-friendly water bottle"` and verify final slogan is output after writer-reviewer iterations complete

### Implementation for User Story 1

- [ ] T016 [P] [US1] Implement Writer agent in src/agents/writer.py using ChatAgent with OpenAIChatClient (base_url=<http://localhost:11434/v1>)
- [ ] T017 [P] [US1] Implement Reviewer agent in src/agents/reviewer.py using ChatAgent with OpenAIChatClient
- [ ] T018 [P] [US1] Create src/agents/\_\_init\_\_.py to export writer and reviewer creation functions
- [ ] T019 [US1] Implement approval detection function is_approved() in src/orchestration/workflow.py (check for "ship it" case-insensitive)
- [ ] T020 [US1] Implement should_continue_iteration() condition in src/orchestration/workflow.py (check turn count and approval status)
- [ ] T021 [US1] Implement build_slogan_workflow() in src/orchestration/workflow.py using WorkflowBuilder (Writer → Reviewer → conditional edge)
- [ ] T022 [US1] Implement run_slogan_generation() orchestrator in src/orchestration/workflow.py (creates session, runs workflow, returns final result)
- [ ] T023 [P] [US1] Create src/orchestration/\_\_init\_\_.py to export run_slogan_generation
- [ ] T024 [US1] Implement CLI entry point in src/cli/main.py with Click group and --version option
- [ ] T025 [US1] Implement `generate` command in src/cli/main.py with INPUT argument and --model option (default: llama2)
- [ ] T026 [US1] Implement basic output formatting in src/cli/output.py for final slogan display (non-verbose format)
- [ ] T027 [US1] Add error handling in src/cli/main.py for empty input validation
- [ ] T028 [US1] Add error handling in src/cli/main.py for Ollama connection errors with helpful messages
- [ ] T029 [US1] Add error handling in src/cli/main.py for model not found errors with available models list
- [ ] T030 [P] [US1] Create src/cli/\_\_init\_\_.py
- [ ] T031 [US1] Update pyproject.toml to add [project.scripts] entry for `slogan-gen` CLI command
- [ ] T032 [US1] Create tests/unit/test_workflow.py to test is_approved() and should_continue_iteration() logic
- [ ] T033 [P] [US1] Create tests/integration/test_end_to_end.py with mocked Ollama responses for full workflow validation

**Checkpoint**: User Story 1 complete - users can generate slogans via CLI with basic output

---

## Phase 4: User Story 2 - Iteration Visibility (Priority: P2)

**Goal**: Enable users to see the iterative process with turn-by-turn display of slogans and feedback

**Independent Test**: Run `slogan-gen generate "tech startup" --verbose` and verify all turns are displayed with writer slogans and reviewer feedback

### Implementation for User Story 2

- [ ] T034 [US2] Add --verbose flag to `generate` command in src/cli/main.py
- [ ] T035 [P] [US2] Implement verbose output formatting in src/cli/output.py with turn-by-turn display (✏️ Writer, 💬 Reviewer emojis)
- [ ] T036 [P] [US2] Implement session summary formatting in src/cli/output.py (total turns, approval status, timing)
- [ ] T037 [US2] Update run_slogan_generation() in src/orchestration/workflow.py to track timestamps for timing display
- [ ] T038 [US2] Modify `generate` command in src/cli/main.py to use verbose output when --verbose flag set
- [ ] T039 [US2] Add styling with Click.style() in src/cli/output.py for colored/formatted turn output
- [ ] T040 [P] [US2] Create tests/unit/test_output.py to verify verbose formatting logic

**Checkpoint**: User Story 2 complete - users can see detailed iteration process with --verbose flag

---

## Phase 5: User Story 3 - Configurable Model Selection (Priority: P3)

**Goal**: Enable users to specify Ollama models and view/manage configuration

**Independent Test**: Run `slogan-gen generate "coffee shop" --model mistral` and verify mistral model is used; run `slogan-gen config show` and verify configuration displays

### Implementation for User Story 3

- [ ] T041 [P] [US3] Implement `config show` subcommand in src/cli/main.py to display current OllamaConfig settings
- [ ] T042 [P] [US3] Implement `config set` subcommand in src/cli/main.py to update configuration values
- [ ] T043 [P] [US3] Implement get_available_models() function in src/config/settings.py to query Ollama API for model list
- [ ] T044 [US3] Implement `models` command in src/cli/main.py to list available Ollama models
- [ ] T045 [US3] Add --refresh flag to `models` command in src/cli/main.py to force refresh model list
- [ ] T046 [US3] Add --max-turns option to `generate` command in src/cli/main.py (1-10 range validation)
- [ ] T047 [US3] Add --output option to `generate` command in src/cli/main.py for saving results to file
- [ ] T048 [US3] Update run_slogan_generation() in src/orchestration/workflow.py to accept max_turns parameter
- [ ] T049 [US3] Add model validation in src/cli/main.py before starting generation (check if model exists)
- [ ] T050 [P] [US3] Create tests/unit/test_config.py to verify configuration management logic

**Checkpoint**: User Story 3 complete - full configuration management and model selection available

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements affecting multiple user stories

- [ ] T051 [P] Add docstrings to all public functions and classes in src/agents/
- [ ] T052 [P] Add docstrings to all public functions and classes in src/orchestration/
- [ ] T053 [P] Add docstrings to all public functions and classes in src/cli/
- [ ] T054 [P] Add docstrings to all public functions and classes in src/config/
- [ ] T055 [P] Add type hints verification - run mypy on entire src/ directory
- [ ] T056 [P] Add linting verification - run ruff check on entire src/ directory
- [ ] T057 [P] Format code - run ruff format on entire src/ directory
- [ ] T058 Update README.md with complete usage examples from quickstart.md
- [ ] T059 [P] Add troubleshooting section to README.md (Ollama connection, model not found, slow generation)
- [ ] T060 [P] Create DEVELOPMENT.md with testing, linting, and type checking instructions
- [ ] T061 Validate all quickstart.md examples work as documented
- [ ] T062 [P] Add logging configuration in src/config/settings.py for debugging support
- [ ] T063 Review code for simplicity violations and refactor if needed
- [ ] T064 Final constitution compliance check (Code Quality, Simplicity, Development Workflow)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational - MVP functionality
- **User Story 2 (Phase 4)**: Depends on Foundational AND User Story 1 (extends generate command)
- **User Story 3 (Phase 5)**: Depends on Foundational (can be parallel to US2, but extends generate command)
- **Polish (Phase 6)**: Depends on completion of all desired user stories

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Requires User Story 1 completion (extends the generate command with --verbose flag)
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Mostly independent but adds options to generate command

### Within Each User Story

**User Story 1 Flow**:

1. T016-T018 (Agents) can run in parallel [P]
2. T019-T023 (Orchestration) must follow agents - T019→T020→T021→T022→T023 sequential
3. T024-T031 (CLI) follow orchestration - T024→T025→T026, with T027-T030 parallel [P]
4. T032-T033 (Tests) can run in parallel [P] after implementation

**User Story 2 Flow**:

1. T034 (Add flag) → T035-T036 (Formatting, parallel [P]) → T037-T040 sequential

**User Story 3 Flow**:

1. T041-T045 (Config/models commands) all parallel [P]
2. T046-T049 (Generate command extensions) sequential
3. T050 (Tests) independent [P]

### Parallel Opportunities

**Phase 1 (Setup)** - All [P] tasks can run together:

- T003, T004, T005, T006, T007 (config files and docs)

**Phase 2 (Foundational)** - All [P] tasks can run together:

- T008, T009, T010, T012, T013, T014, T015 (all model definitions)

**User Story 1**:

- T016, T017, T018 (both agents + exports)
- T027, T028, T029, T030 (error handling + init)
- T032, T033 (tests)

**User Story 2**:

- T035, T036 (formatting functions)
- T040 (tests)

**User Story 3**:

- T041, T042, T043 (config commands)
- T050 (tests)

**Phase 6 (Polish)**:

- T051, T052, T053, T054, T055, T056, T057, T059, T060 (all documentation and quality checks)

---

## Parallel Example: User Story 1 - Agents

```bash
# Launch both agents in parallel:
Task T016: "Implement Writer agent in src/agents/writer.py"
Task T017: "Implement Reviewer agent in src/agents/reviewer.py"
Task T018: "Create src/agents/__init__.py exports"

# All three can be developed simultaneously by different developers
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T007) - 7 tasks
2. Complete Phase 2: Foundational (T008-T015) - 8 tasks
3. Complete Phase 3: User Story 1 (T016-T033) - 18 tasks
4. **STOP and VALIDATE**: Test with `slogan-gen generate "eco-friendly water bottle"`
5. Verify output: Final slogan appears after writer-reviewer iterations
6. **MVP Complete** - 33 tasks total for working CLI

### Incremental Delivery

1. **Foundation** (Setup + Foundational): Tasks T001-T015 → Core infrastructure ready
2. **MVP Release** (+ User Story 1): Tasks T016-T033 → Basic slogan generation working
3. **Enhanced Visibility** (+ User Story 2): Tasks T034-T040 → Verbose iteration display
4. **Full Configuration** (+ User Story 3): Tasks T041-T050 → Model selection and config management
5. **Production Ready** (+ Polish): Tasks T051-T064 → Documentation, testing, quality

### Parallel Team Strategy

With multiple developers:

1. **Together**: Complete Phase 1 (Setup) and Phase 2 (Foundational)
2. **Once Foundational is done**:
   - Developer A: User Story 1 (T016-T033)
   - Developer B: Can start User Story 3 models/config parts (T041-T045, T050) in parallel
3. **After User Story 1**:
   - Developer A: User Story 2 (T034-T040)
   - Developer B: Complete User Story 3 (T046-T049)
4. **Together**: Polish (T051-T064)

---

## Task Summary

- **Total Tasks**: 64
- **Phase 1 (Setup)**: 7 tasks
- **Phase 2 (Foundational)**: 8 tasks (BLOCKING)
- **Phase 3 (User Story 1 - MVP)**: 18 tasks
- **Phase 4 (User Story 2)**: 7 tasks
- **Phase 5 (User Story 3)**: 10 tasks
- **Phase 6 (Polish)**: 14 tasks

**Parallel Tasks**: 28 tasks marked with [P] can run in parallel within their phase/story

**MVP Scope**: 33 tasks (Setup + Foundational + User Story 1)

**Suggested First Delivery**: Complete through Phase 3 for working MVP, then iterate

---

## Notes

- All tasks include exact file paths for clarity
- [P] tasks work on different files with no dependencies - can parallelize
- [Story] labels enable tracking which user story each task belongs to
- Each user story has a checkpoint for independent validation
- Constitution alignment: Small focused tasks (Code Quality ✅), No over-engineering (Simplicity ✅), Incremental delivery (Development Workflow ✅)
- Tests were not requested in specification, but test file structure provided in tasks for future enhancement
- Stop after any user story phase to validate and potentially deploy
