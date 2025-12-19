# TODO_codex

## Branch: feature/test-hardening
- [x] Improve test fixtures to accept new Deepseek env var (`DEEPSEEK_API_KEY_VOLC`).
- [x] Add unit coverage for content validation (blocked sources, short content).
- [x] Document cheap default model for integration checks.
- [x] Update changelog and docs for test changes.

## Branch: feature/reliability-hardening
- [x] Add LLM request timeouts and safer retry handling.
- [x] Reserve output tokens in context-size checks using `estimate_tokens`.
- [x] Integrate content validation into processing/conversion flow.
- [x] Handle per-input failures without aborting all inputs.
- [x] Align README/DEVELOPER env var guidance with `llm_config.yml`.
- [ ] Add targeted tests and run unit + minimal integration.

## Backlog
- [ ] Pydantic v2 migration: replace class-based Config with ConfigDict to clear warnings.

