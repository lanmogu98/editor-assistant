# RFC: Async/Concurrent Processing Refactor

## 1. Summary
Refactor the current synchronous `requests`-based LLM interaction to an asynchronous architecture using `httpx` and `asyncio`. This will enable parallel processing of multiple documents, significantly reducing total processing time for batch tasks.

## 2. Motivation
- **Current State**: Documents are processed sequentially (`process_multiple` loop).
- **Problem**: LLM API calls have high latency (avg 10-30s). Processing 10 docs takes ~5 mins.
- **Goal**: Process documents concurrently. Theoretical speedup approaches N-fold (bounded by rate limits).

## 3. Proposed Architecture

### 3.1. Dependency Changes
- Replace `requests` with `httpx` (standard async HTTP client).
- Keep `requests`? No, fully replace to avoid dual-stack complexity.

### 3.2. Core Components Changes

#### `LLMClient` (src/editor_assistant/llm_client.py)
- Change `__init__`: Initialize `httpx.AsyncClient`.
- Change `generate_response()` -> `async def generate_response()`.
- Refactor `_make_api_request` to use `await client.post()`.
- **Streaming**: Update SSE parser to use `async for line in response.aiter_lines()`.
- **Resource Management**: Implement `__aenter__` and `__aexit__` for context manager usage (auto-close client).

#### `MDProcessor` (src/editor_assistant/md_processor.py)
- Change `process_mds` -> `async def process_mds`.
- Use `asyncio.Semaphore` to limit concurrency (respect provider Rate Limits).
  - e.g., `max_concurrent = 5` (configurable).

#### `EditorAssistant` (src/editor_assistant/main.py)
- Change `process_multiple` -> `async def process_multiple`.
- Logic shift:
  - From:
    ```python
    for input in inputs:
        processor.process_mds([input])
    ```
  - To:
    ```python
    tasks = [processor.process_mds([input]) for input in inputs]
    await asyncio.gather(*tasks)
    ```

#### `CLI` (src/editor_assistant/cli.py)
- Wrap entry points (e.g., `cmd_generate_brief`) with `asyncio.run()`.

## 4. Rate Limiting Strategy
- Current `_wait_for_rate_limit()` is blocking (`time.sleep`).
- **New Strategy**:
  - Use `asyncio.sleep`.
  - Global `asyncio.Semaphore` in `LLMClient` or `MDProcessor` to limit active requests.
  - Per-provider limits: The `LLMClient` already has logic for RPM (Requests Per Minute). This needs to be thread/task-safe.

## 5. Implementation Plan (Phased)

### Phase 1: Async LLMClient (Low Level)
- [ ] Install `httpx`.
- [ ] Convert `LLMClient` methods to `async`.
- [ ] Update unit tests for `LLMClient`.

### Phase 2: Async Processor (Mid Level)
- [ ] Update `MDProcessor` to be async.
- [ ] Implement `Semaphore` for concurrency control.

### Phase 3: CLI & Entry Points (High Level)
- [ ] Update `main.py` and `cli.py` to drive async execution.
- [ ] Verify `batch_process` scripts.

## 6. Risks
- **Rate Limits**: Parallel requests might hit provider 429 errors instantly. Need robust backoff (already partially implemented).
- **SQLite**: `sqlite3` is synchronous. Concurrent writes might lock DB.
  - Mitigation: Use a dedicated thread for DB writes, or just rely on SQLite's WAL mode + `threading` lock (asyncio runs on single thread, so standard `sqlite3` usage is mostly safe if not using threads, but we need to be careful not to block the event loop).
  - Better: Run DB operations in `run_in_executor`.
