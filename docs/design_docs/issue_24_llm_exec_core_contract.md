# LLM Exec Core Downstream Contract

## Package

- Distribution: `llm-exec-core`
- Import package: `llm_exec_core`
- Initial package version: `0.1.0`
- Reviewed typed-result release: `0.4.1`
- First editor-assistant consumer version: `0.6.0`

## Reference Strategy

`editor-assistant` consumes the published 0.4.1 wheel from the GitHub release
and records its SHA-256
`30dbc41afa29cf1e74d572703a93111f65ab7581eae4d69d739fe292d007e6f7`
in `uv.lock`. The committed project and lock files contain no sibling,
editable, or unreleased core source.

## Minimal Worker Import

```python
from pathlib import Path

from llm_exec_core import LLMClient


async def run_llm_step(prompt: str, catalog: Path) -> str:
    client = LLMClient("glm-5.2-or", config_source=catalog)
    result = await client.generate(
        prompt,
        request_name="linkresearcher_ingest",
        trace_context={"worker": "content-ingestion"},
        run_id="attempt-123",
    )
    return result.text
```

## Result Shape

`LLMClient.generate()` returns `LLMResult` with:

- `text`: final response text.
- `usage`: token counts, costs, and currency.
- `metadata`: request id, run id, model, provider, timing, and trace context.
- `structured`: parsed caller-owned structured output, or `None`.

## Editor Task Result

`MDProcessor.execute_task()` is the additive typed Editor entry point. On
success it returns `TaskExecutionResult` with:

- `task_name`: the resolved registry task name.
- `run_id`: the Editor persistence run id.
- `outputs`: a mapping of output names to `OutputArtifact` values.
- `llm_result`: the original core `LLMResult` object.

`OutputArtifact` retains a typed string or JSON value, an explicit
`text/plain` or `application/json` content type, and its serialized text. The
existing `brief`, `outline`, and `translate` tasks remain text-only and produce
text artifacts without prompt or output changes.

The typed entry point calls core `generate()` and propagates validation,
provider, and post-processing exceptions. `process_mds() -> tuple[bool, int]`
continues using the legacy `generate_response()` adapter and translates the
same expected failures to its existing boolean/run-id result.
`EditorAssistant.process_multiple()` remains a `None`-returning compatibility
orchestrator over `process_mds()`.

## Execution Metadata Boundary

`llm-exec-core` owns request execution and execution metadata capture. The caller owns worker lifecycle state, attempt state, downstream persistence, and any schema that wraps the result.

## Structured Output Hook

```python
import json


def parse_worker_payload(text: str) -> dict:
    return json.loads(text)


result = await client.generate(
    prompt,
    request_name="extract_payload",
    structured_output_hook=parse_worker_payload,
)
```

## Cancellation Boundary

The core package re-raises `asyncio.CancelledError`. Worker lifecycle state is caller-owned.

## Protocol Boundary

`llm-exec-core` initially supports OpenAI-compatible `/chat/completions` APIs. Native Anthropic, Bedrock, Vertex, or provider-specific protocols are out of scope until explicitly designed.

## Rate Limit and Cache Boundary

Built-in rate limiting and response cache are in-process/per-client conveniences. They are not distributed worker coordination. LinkResearcher must use its own shared limiter or durable coordination if attempts run across multiple processes or hosts. Response cache is disabled by default and should stay disabled for idempotent worker accounting unless a caller explicitly opts in.

## App/Core Responsibility Boundary

`llm-exec-core` handles LLM execution. `editor-assistant` owns document workflow, task orchestration, prompts, SQLite persistence, CLI commands, output paths, and application logging.

## Out of Scope

LinkResearcher task lifecycle, attempt schema, artifact schema, result schema, and apply semantics are not part of `llm-exec-core`.
Native Anthropic, Bedrock, Vertex, or provider-specific protocol support is also out of scope.
