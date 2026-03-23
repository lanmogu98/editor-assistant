# Roadmap

> Strategic direction and milestones for Editor Assistant.
> For current work items, see GitHub Issues (`gh issue list`).

## Vision

A complete AI-powered document processing toolkit: CLI for power users, web UI for broader access, with a pluggable task system and multi-model support that adapts to evolving LLM capabilities.

## Current Phase: Reliability & Cost Optimization (Phase 1)

Hardening the async architecture shipped in v0.5.x. Focus areas: tiered pricing for accurate cost tracking, input token limit validation, and reliability improvements (optional file output, error handling).

### Milestones

| Milestone | Target | Theme |
|-----------|--------|-------|
| Tiered pricing | Phase 1 | Accurate cost tracking for models with variable pricing tiers |
| Model parameter validation | Phase 1 | Correct input token limit enforcement |
| Reliability hardening | Phase 1 | Optional file output, no DB writes on failure |

## Future Phases

### Phase 2: Extensibility

Dependency injection for testability, external plugin loading (`~/.editor-assistant/plugins/`), structured output tasks (ClassifyTask), and a benchmark module for systematic evaluation of LLM performance across scientific content scenarios.

### Phase 3: User Experience

Web UI (FastAPI + SPA), Chrome extension for browser-based document processing, YAML configuration file support (`~/.editor-assistant/config.yml`).

### Long-term

Persistence layer optimization (resume semantics, query efficiency), interactive AI assistant with autonomous topic selection and feedback loop.

## Non-Goals (for now)

- Mobile app
- Self-hosted / local LLM support (all models are API-based)
- Multi-user / authentication system
- Real-time collaborative editing
