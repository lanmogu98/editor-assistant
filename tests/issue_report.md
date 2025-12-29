# Tests Module Review — Issue Report

This document is a review of the current `tests/` suite with two lenses:

- **Engineering / Best Practice**: correctness, robustness, maintainability, extensibility
- **Functional Coverage**: which modules/behaviors are covered, and which edge cases are missing

It also records the concrete fixes applied during this review so the test suite is safer to run by default.

---

## 1) Engineering / Best Practice Findings

### A. Hard failures caused by missing API keys (constructor-time)

- **Observation**: `LLMClient.__init__()` raises if its provider API key env var is missing (`DEEPSEEK_API_KEY_VOLC` for `deepseek-v3.2`).
- **Impact**: Any test that constructs `LLMClient(...)` or `MDProcessor(...)` will **fail immediately** unless either:
  - The test sets a dummy env var, or
  - The test is skipped when the env var is missing, or
  - The constructor is patched/mocked.
- **Fix applied**:
  - `tests/unit/test_llm_client.py`: switched from `skipif` to a **module-local autouse fixture** setting a dummy `DEEPSEEK_API_KEY_VOLC`.
  - `tests/stress/test_error_boundaries.py`: added an **autouse dummy key** fixture.
  - `tests/stress/test_sqlite_concurrency.py`: sets a dummy key via `monkeypatch` argument.
  - `tests/integration/test_storage_integration.py`: added `skipif(DEEPSEEK_API_KEY_VOLC missing)` **only on the real-API tests**.
  - `tests/integration/test_cli.py`: added `skipif(DEEPSEEK_API_KEY_VOLC missing)` **only on the real-API CLI tests**.

### B. Wrong env var used in skip conditions

- **Observation**: Several tests used `DEEPSEEK_API_KEY` but the active config for `deepseek-v3.2` is `DEEPSEEK_API_KEY_VOLC` (`src/editor_assistant/config/llm_config.yml`).
- **Impact**:
  - Tests could be skipped incorrectly even when the correct key exists, or
  - Tests could run and then fail (because the constructor checks a different env var).
- **Fix applied**: switched affected tests to `DEEPSEEK_API_KEY_VOLC` or removed the skip by making the test hermetic with a dummy key (unit tests).

### C. Module-level skip marks that accidentally skip unrelated “no-key” tests

- **Observation**: `tests/integration/test_cli.py` originally applied a module-level skip, which also skipped `--help/--version` tests that **do not require any API key**.
- **Fix applied**: removed module-level skip and applied `skipif` only to tests that actually do LLM work.

### D. Marker inconsistencies (tests disappearing from `pytest -m unit`)

- **Observation**: Some unit tests only used `@pytest.mark.asyncio` and were missing `@pytest.mark.unit`.
- **Impact**: `pytest -m unit` would silently omit them, reducing confidence.
- **Fix applied**:
  - `tests/unit/test_md_processor_async.py`: added module-level `pytestmark = pytest.mark.unit`
  - `tests/unit/test_llm_client_async.py`: added module-level `pytestmark = pytest.mark.unit`
  - `tests/integration/test_batch_ui.py`: marked as `unit` (it’s fully mocked and does not require external services)

### E. A duplicated test module (copy/paste inside itself)

- **Observation**: `tests/unit/test_content_validation.py` contained an entire duplicated copy of itself.
- **Impact**: confusing to maintain; later definitions override earlier ones; noisy diffs.
- **Fix applied**: removed the duplicated second half.

### F. CLI tests assumed an installed `editor-assistant` console script

- **Observation**: Some tests spawned `editor-assistant ...` directly.
- **Impact**: these fail in environments where the package is not installed as a script (common in CI or isolated runners).
- **Fix applied**: use `python -m editor_assistant.cli ...` via `sys.executable` in:
  - `tests/integration/test_cli.py`
  - `tests/integration/test_storage_integration.py` (history/stats)

### G. Unit tests touching the database (unnecessary coupling)

- **Observation**: some `MDProcessor` unit tests were writing to SQLite via `RunRepository` indirectly.
- **Impact**: slower tests; more moving parts; harder to reason about failures.
- **Fix applied**:
  - `tests/unit/test_md_processor.py`: patched `RunRepository` in the processor fixture so unit tests don’t do SQLite I/O.
  - (Storage behavior remains covered in `tests/unit/test_storage.py`.)

---

## 2) Functional Coverage Review (Modules & Boundaries)

### Current high-signal coverage (good)

- **Storage layer**: `tests/unit/test_storage.py` is comprehensive (schema, CRUD, edge cases, isolation).
- **Tasks**: `tests/unit/test_tasks.py` covers task registry and core task behaviors.
- **Async orchestration**: `tests/unit/test_main.py` covers `EditorAssistant.process_multiple` error handling paths.
- **LLM client async mechanics**: `tests/unit/test_llm_client_async.py` covers non-streaming, streaming, and context manager behavior with mocked `httpx`.

### Coverage gaps (notable)

- **Markdown conversion (`MarkdownConverter`)**:
  - Previously had no direct tests.
  - **Fix applied**: added `tests/unit/test_md_converter.py` to validate converter selection/fallback and file output behavior without network.

- **MDProcessor error paths** (partial):
  - Existing tests cover: unknown task, empty inputs, basic happy path, semaphore concurrency (async test module).
  - Missing unit coverage for: task validation failures, prompt build failures, post-process exceptions, save/DB failure handling, cancellation handling.
  - Recommendation: add targeted unit tests that patch `TaskRegistry` to force each failure mode deterministically.

- **CLI parsing**:
  - There is some CLI execution coverage, plus help/version tests.
  - Recommendation: add fast unit tests for `parse_source_spec()` error cases (bad format, empty path, invalid type).

---

## 3) Recommendations / Standards (Going Forward)

### Standardize markers

- **Rule**: every test should have at least one of:
  - `unit` (fast, fully mocked, no real external services)
  - `integration` (may touch real components / subprocess / filesystem / DB)
  - `expensive` (costs money) and/or `slow` (takes long)

### Avoid module-level skips unless every test truly shares the same requirement

- Prefer applying `skipif` at class/function scope so unrelated tests still run.

### Prefer module execution for CLI tests

- Use `sys.executable -m editor_assistant.cli` to avoid relying on `console_scripts`.

### Don’t require real API keys for unit tests

- If a constructor requires an env var, use **module-local** dummy env fixtures.
- Never set dummy API keys globally in `tests/conftest.py` (it can accidentally enable expensive integration tests).

---

## 4) Files Changed / Added in This Review

- **Fixed**:
  - `tests/unit/test_content_validation.py` (removed duplicated content)
  - `tests/unit/test_md_processor.py` (mock repository for unit tests; improved assertions; dummy key for “real constructor” test)
  - `tests/unit/test_md_processor_async.py` (added `unit` marker; clarified fixtures; renamed fixtures for clarity)
  - `tests/unit/test_llm_client.py` (dummy key fixture; removed incorrect skipifs)
  - `tests/unit/test_llm_client_async.py` (added `unit` marker)
  - `tests/integration/test_cli.py` (fixed skipping, safer CLI invocation)
  - `tests/integration/test_storage_integration.py` (skip only real-API tests; safer CLI invocation; robustness fix for run_id)
  - `tests/integration/test_async_flow.py` (fixed skip env var; removed broken `__main__` block)
  - `tests/integration/test_batch_ui.py` (marked as unit)
  - `tests/stress/test_sqlite_concurrency.py` (dummy key + `slow` marker)
  - `tests/stress/test_error_boundaries.py` (dummy key + `slow` marker; more correct HTTPStatusError construction)

- **Added**:
  - `tests/unit/test_md_converter.py` (MarkdownConverter unit tests)


