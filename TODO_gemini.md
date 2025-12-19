# TODO_gemini

## Current Branch: docs/roadmap-cleanup

### Documentation Updates
- [x] Update `FUTURE_ROADMAP.md`: Mark "Persistence Layer" as completed (Phase 1).
- [x] Update `FUTURE_ROADMAP.md`: Clarify "Async Processing" (Streaming solved).
- [x] Update `FUTURE_ROADMAP.md`: Mark "Plugin System" as partial (Registry implemented).
- [x] Update `FUTURE_ROADMAP.md`: Move "Tiered Pricing" to Phase 2.
- [x] Verify "Persistence Layer" feature parity:
    - [x] Check DB schema (sessions/runs, inputs, outputs, token_usage).
    - [x] Check CLI commands (`history`, `stats`, `show`).
    - [x] Note missing features (`resume` command, Export) - Added to Roadmap backlog.

### Async/Concurrent Refactor (Planned Phase 2)
- [ ] **Design Async Architecture**:
    - [ ] Identify synchronous blocking points (`requests.post`, file I/O).
    - [ ] Choose async library: `httpx` (standard replacement for requests).
    - [ ] Plan concurrency limit (semaphore) to respect provider rate limits.
- [ ] **Implementation Steps**:
    1.  Create `AsyncLLMClient` (or refactor `LLMClient` to support both/async).
    2.  Update `MDProcessor` to use `async`/`await`.
    3.  Refactor `main.py` -> `process_multiple` to use `asyncio.gather`.
    4.  Update `cli.py` to run async entry point.
