---
paths:
  - "**/*"
---

# Editor Assistant — Project Rules

Read `AGENTS.md` at project root for full context before making any changes.

## Critical Constraints

- All I/O must be async (httpx, not requests)
- `LLMClient` is the sole API interface — no direct HTTP calls to LLM providers elsewhere
- Task modules register via `@TaskRegistry.register()` decorator only
- External API contract (`LLMClient`, `config.llm_models`, `config.constants`) must not break without version bump
- Model/provider config lives in `config/llm_config.yml` only — no hardcoded model names in Python

## Code Style

- `black` formatting, `flake8` linting, `mypy` type checking
- Type hints on all public APIs
- Async/await throughout hot paths

## Architecture

- Project root detected by locating `pyproject.toml`
- Package manager: uv (`pip install -e .` for dev)
- src layout: `src/editor_assistant/`

## Do NOT

- Commit secrets (`.env`, `*.db`, tokens)
- Use synchronous I/O (`requests`, `urllib`) in production code
- Modify `llm_config.yml` schema without updating `DEVELOPER_GUIDE.md`
- Break the library API contract without a version bump
