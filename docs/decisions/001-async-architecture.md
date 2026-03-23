# ADR-001: Full Async Architecture with httpx

**Date**: 2025-12-19
**Status**: accepted

## Context

The original implementation used synchronous `requests`, creating a bottleneck when processing multiple documents or making concurrent LLM API calls. Batch processing was sequential, resulting in poor throughput for multi-document workflows.

## Decision

Migrate to full async architecture using `asyncio` + `httpx`. Use Semaphore-based concurrency control (default 5 concurrent requests). CLI entry point uses `asyncio.run()`.

## Consequences

**Positive**:
- 4.46x performance improvement on batch workloads
- Natural concurrency model for I/O-bound LLM API calls
- Semaphore provides configurable backpressure

**Negative**:
- All downstream code must be async-aware
- Debugging async code is more complex
- `requests` kept temporarily for compatibility (deprecated)

**Neutral**:
- Test suite required `pytest-asyncio`
- Rich progress bars work well with async via `asyncio.create_task()`
