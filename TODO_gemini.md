# TODO_gemini

## Current Branch: feature/async-refactor

### Async/Concurrent Refactor (Phase 2)
- [x] **Design Async Architecture**: RFC created in `docs/design_docs/rfc_async_refactor.md`.
- [x] **Phase 1: Async LLMClient**:
    - [x] Add `httpx` dependency.
    - [x] Update `LLMClient` to use `httpx.AsyncClient`.
    - [x] Implement async streaming support.
    - [x] Unit tests (`tests/unit/test_llm_client_async.py`).
- [x] **Phase 2: Async MDProcessor**:
    - [x] Refactor `process_mds` to be async.
    - [x] Implement concurrency control (`asyncio.Semaphore`).
    - [x] Unit tests (`tests/unit/test_md_processor_async.py`).
- [x] **Phase 3: Integration**:
    - [x] Refactor `main.py` `process_multiple` to use `asyncio.gather`.
    - [x] Refactor `cli.py` to use `asyncio.run`.
    - [x] Integrate `batch` processing command into CLI.
    - [x] Add end-to-end integration test (`tests/integration/test_async_flow.py`).
- [x] **Phase 4: Verification & Docs**:
    - [x] Perform stress testing (Rate Limits, Concurrency, Partial Failures).
    - [x] Benchmark performance (4.46x speedup achieved).
    - [x] Update `README.md` (Batch usage, Async features).
    - [x] Update `DEVELOPER_GUIDE.md` (Async architecture, Performance).
    - [x] Update `CHANGELOG.md` (v0.5.0).

### Next Steps (Post-Merge)
- [ ] Monitor SQLite concurrent write performance (may need `run_in_executor` optimization).
- [ ] Optimize `MDConverter` to run in thread pool for parallel conversion.
