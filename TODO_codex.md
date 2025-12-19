# TODO_codex

## Branch: feature/test-hardening
- [x] Update test fixtures to require `DEEPSEEK_API_KEY_VOLC`.
- [x] Add unit coverage for content validation (blocked publishers, short content).
- [x] Keep integration tests note: default model `deepseek-v3.2` is cheap; use minimal samples.
- [x] Update changelog/docs after test changes.

## Branch: feature/reliability-hardening
- [ ] Add LLM request timeouts and safer retry handling.
- [ ] Reserve output tokens in context-size checks using `estimate_tokens`.
- [ ] Integrate content validation into processing/conversion flow.
- [ ] Handle per-input failures without aborting all inputs.
- [ ] Align README/DEVELOPER env var guidance with `llm_config.yml`.
- [ ] Add targeted tests and run unit + minimal integration.

## Backlog
- [ ] Pydantic v2 migration: replace class-based Config with ConfigDict to clear warnings.
# TODO_codex

## Branch: feature/test-hardening
- [ ] Improve test fixtures to accept new Deepseek env var.
- [ ] Add unit coverage for content validation (blocked sources, short content).
- [ ] Document cheap default model for integration checks.
- [ ] Update changelog and docs for test changes.

## Branch: feature/reliability-hardening
- [ ] Add LLM request timeouts and safer retry handling.
- [ ] Reserve output tokens in context-size checks using estimate_tokens.
- [ ] Integrate content validation into processing/conversion flow.
- [ ] Handle per-input failures without aborting all inputs.
- [ ] Align README/DEVELOPER env var guidance with llm_config.yml.
- [ ] Add targeted tests and run unit + minimal integration.

