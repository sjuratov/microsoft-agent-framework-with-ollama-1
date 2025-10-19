<!--
SYNC IMPACT REPORT
==================
Version: 0.0.0 → 1.0.0
Change Type: MAJOR (Initial constitution creation)
Ratification Date: 2025-10-19

Modified/Added Principles:
- ✅ Added: I. Code Quality - Ensures maintainability through reviews, documentation, and standards
- ✅ Added: II. Simplicity - Prevents over-engineering and keeps codebase approachable

Added Sections:
- ✅ Development Workflow Requirements - Lightweight process ensuring quality gates

Templates Status:
- ✅ plan-template.md - Compatible (Constitution Check section already present)
- ✅ spec-template.md - Compatible (User scenarios and testing alignment maintained)
- ✅ tasks-template.md - Compatible (Task organization supports incremental development)

Follow-up TODOs: None
==================
-->

# Microsoft Agent Framework with Ollama Constitution

## Core Principles

### I. Code Quality

**All code MUST meet high-quality standards to ensure maintainability and reliability.**

- Every code change requires peer review before merge
- All features and public APIs MUST have clear, up-to-date documentation
- Code MUST follow established style guides and pass linting checks
- Complex logic MUST include inline comments explaining the "why"
- Breaking changes MUST be documented with migration guides

**Rationale**: Building an agentic solution requires reliable, maintainable code that the team can confidently evolve. Poor code quality leads to technical debt that hampers innovation and increases maintenance burden.

### II. Simplicity

**Favor simple, clear solutions over clever or complex ones.**

- Start with the simplest solution that meets requirements (YAGNI principle)
- Avoid premature optimization and over-engineering
- Prefer composition over inheritance; explicit over implicit
- If a feature requires extensive explanation, reconsider the design
- Dependencies MUST be justified; minimize external dependencies

**Rationale**: Simplicity reduces cognitive load, makes debugging easier, and allows faster onboarding. Complex solutions are harder to maintain and more prone to bugs, especially critical in AI agent systems where behavior must be predictable.

## Development Workflow Requirements

**Lightweight process ensuring quality and simplicity gates.**

### Code Review Process

- All changes require at least one peer review
- Reviewers MUST verify alignment with Code Quality and Simplicity principles
- PRs should be small and focused (prefer incremental development)

### Documentation Standards

- Every feature MUST have user-facing documentation before merge
- API changes MUST update relevant documentation in the same PR
- README.md MUST stay current with setup and usage instructions

### Incremental Development

- Build in small, testable increments
- Each increment should deliver demonstrable value
- Favor shipping smaller working features over large incomplete ones

## Governance

**This constitution supersedes all other development practices.**

### Amendment Process

1. Proposed changes MUST be documented with rationale
2. Team discussion and consensus required for approval
3. Version bump per semantic versioning rules (see below)
4. All dependent templates and docs updated before finalization

### Versioning Policy

- **MAJOR**: Backward incompatible principle removals or redefinitions
- **MINOR**: New principle/section added or materially expanded guidance
- **PATCH**: Clarifications, wording, typo fixes, non-semantic refinements

### Compliance

- All PRs and reviews MUST verify compliance with these principles
- Deviations from principles require explicit justification and approval
- Periodic constitution reviews (quarterly recommended) to ensure relevance

**Version**: 1.0.0 | **Ratified**: 2025-10-19 | **Last Amended**: 2025-10-19
