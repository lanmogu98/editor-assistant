# LLM Exec Core Downstream Contract

## Package

- Distribution: `llm-exec-core`
- Import package: `llm_exec_core`
- Initial package version: `0.1.0`
- First editor-assistant consumer version: `0.6.0`

## Reference Strategy

During local migration, `editor-assistant` references the sibling package with relative `[tool.uv.sources]` or a uv workspace.

For release consumption, applications pin `llm-exec-core==0.1.0`.

Final committed `editor-assistant` config must not contain absolute `file://` paths. Local development uses relative `[tool.uv.sources]` or a uv workspace; release consumption uses the pinned package.

## Minimal Worker Import

```python
from llm_exec_core import LLMClient


async def run_llm_step(prompt: str) -> str:
    client = LLMClient("glm-4.7-or")
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
