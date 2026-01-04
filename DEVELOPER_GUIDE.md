# Developer Guide (Project-Specific)

This document provides technical documentation for developers contributing to Editor Assistant.

## Documentation Map

- General engineering norms (reusable across projects): configured as Cursor user rules.
- This file focuses on project-specific architecture, configs, models, tasks, storage, and test matrix.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Module Reference](#module-reference)
3. [Adding a New LLM Model](#adding-a-new-llm-model)
4. [Adding a New Task Type](#adding-a-new-task-type)
5. [Configuration System](#configuration-system)
6. [Testing Guide](#testing-guide)
7. [Common Patterns](#common-patterns)
8. [Performance & Concurrency](#performance--concurrency)

## Documentation Synchronization

(General engineering norms are configured as Cursor user rules)

**Agent Protocol**:

1. **Roadmap**: `FUTURE_ROADMAP.md` is the source of truth for planning. `TODO.md` is the current execution checklist. Always sync status back to Roadmap.
2. **Developer Guide**: This file (`DEVELOPER_GUIDE.md`) must reflect the *current* architecture. If you add a module (e.g. `async_processor`), update the "Architecture Overview" and "Module Reference" immediately.
3. **Changelog**: All user-facing changes go to `CHANGELOG.md`.

---

## Architecture Overview

```text
┌─────────────────────────────────────────────────────────────────┐
│                           CLI Layer                             │
│                          (cli.py)                               │
│  Commands: brief, outline, translate, process, batch, convert   │
│            clean, history, stats, show, resume, export          │
│  [Async Entry Point] via asyncio.run()                          │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Orchestration Layer                        │
│                         (main.py)                               │
│                     EditorAssistant class                       │
│  [Async] process_multiple() uses asyncio.gather()               │
└───────────────┬─────────────────────────────┬───────────────────┘
                │                             │
                ▼                             ▼
┌────────────────────────────┐     ┌──────────────────────────────────┐
│    Content Conversion      │     │       Content Processing         │
│    (md_converter.py)       │     │       (md_processor.py)          │
│    - PDF, DOCX, HTML       │ --> │       [Async] process_mds()      │
│    - URL fetching          │     │       - Prompt building          │
│    - Format detection      │     │       - Semaphore control        │
│    [Sync] (CPU Bound)      │     │       - Output formatting        │
└───────────────┬────────────┘     └───────────────┬──────────────────┘
                │                                  │
                ▼                                  ▼
┌────────────────────────────┐   ┌──────────────────────────────────┐
│   HTML Cleaning            │   │         LLM Client               │
│   (clean_html_to_md.py)    │   │       (llm_client.py)            │
│   - Readabilipy            │   │       [Async] httpx.AsyncClient  │
│   - Trafilatura            │   │       - Rate limiting (async)    │
│                            │   │       - Streaming (SSE)          │
│                            │   │       - Token tracking           │
└────────────────────────────┘   └───────────────┬──────────────────┘
                                                 │
                                                 ▼
                                 ┌─────────────────────────────────┐
                                 │        Config Layer             │
                                 │        (config/)                │
                                 │  - llm_config.yml (models)      │
                                 │  - constants.py (settings)      │
                                 │  - prompts/ (templates)         │
                                 └─────────────────────────────────┘
```

### Data Flow (Async)

```text
Input (URL/PDF/MD) 
    → MarkdownConverter.convert_content() [Sync] (or direct `.md` read)
    → MDArticle (normalized content)
    → EditorAssistant.process_multiple() [Async Fan-out]
    → MDProcessor.process_mds() [Async] (Semaphore-limited)
    → LLMClient.generate_response() [Async]
    → Output (SQLite run history + optional files under `llm_summaries/`)
```

---

## Module Reference

### Core Modules

| Module | Purpose | Key Classes/Functions |
| ------ | ------- | ------------------- |
| `cli.py` | Async Command-line interface | `main()`, `create_parser()`, `cmd_generate_brief()` (async), `cmd_resume()` (async), `cmd_export()` |
| `main.py` | Async Orchestration | `EditorAssistant` |
| `md_converter.py` | Format conversion (Sync) | `MarkdownConverter` |
| `md_processor.py` | Async LLM processing | `MDProcessor` (uses `asyncio.Semaphore`) |
| `llm_client.py` | Async API interaction | `LLMClient` (uses `httpx`) |
| `clean_html_to_md.py` | HTML extraction | `CleanHTML2Markdown` |
| `content_validation.py` | Input validation | `validate_content()`, `BlockedPublisherError` |
| `data_models.py` | Data structures | `MDArticle`, `Input`, `ProcessType`, `InputType` |

### Config Modules

| Module | Purpose |
| ------ | ------- |
| `config/llm_config.yml` | LLM provider settings (API URLs, models, pricing) |
| `config/llm_models.py` | YAML loader + model/provider lookup |
| `config/constants.py` | All configurable constants |
| `config/load_prompt.py` | Prompt template loader |
| `config/logging_config.py` | Logging utilities |
| `config/prompts/*.txt` | Jinja2 prompt templates |

---

## Adding a New LLM Model

**Single Source of Truth:** `config/llm_config.yml` is the only file you need to edit.

### Step 1: Add to YAML Config

Edit `config/llm_config.yml`:

```yaml
# Add new model to existing provider
existing-provider:
  models:
    your-new-model:
      id: "actual-api-model-id"
      pricing: {input: 1.00, output: 2.00}  # per 1M tokens

# Or add a new provider with models
your-new-provider:
  api_key_env_var: "YOUR_API_KEY"
  api_base_url: "https://api.yourprovider.com/v1/chat/completions"
  temperature: 0.6
  max_tokens: 32000
  context_window: 128000
  pricing_currency: "$"
  models:
    your-model-name:
      id: "actual-api-model-id"
      pricing: {input: 1.00, output: 2.00}
```

### Step 2: Set Environment Variable

```bash
export YOUR_API_KEY="your-api-key-here"
```

### Step 3: Test

```bash
editor-assistant brief paper=test.pdf --model your-model-name
```

That's it! No Python code changes needed. The model list is dynamically loaded from YAML.

---

## Adding a New Task Type

With the new pluggable task system, adding a new task is simple:

### Step 1: Create Task Class

Create `tasks/your_task.py`:

```python
from typing import List, Dict
from .base import Task, TaskRegistry
from ..data_models import MDArticle
from ..config.load_prompt import load_your_task_prompt

@TaskRegistry.register("your-task")
class YourTask(Task):
    name = "your-task"
    description = "Description of your task"
    supports_multi_input = False  # or True for multi-source tasks
    
    def validate(self, articles: List[MDArticle]) -> tuple[bool, str]:
        if len(articles) != 1:
            return False, "This task requires exactly one article"
        return True, ""
    
    def build_prompt(self, articles: List[MDArticle]) -> str:
        return load_your_task_prompt(content=articles[0].content)
    
    def post_process(self, response: str, articles: List[MDArticle]) -> Dict[str, str]:
        # Return {"main": response} for single output
        # Return {"main": response, "extra": extra_content} for multiple outputs
        return {"main": response}
```

### Step 2: Register in `__init__.py`

Edit `tasks/__init__.py`:

```python
from .your_task import YourTask

__all__ = [
    # ... existing exports ...
    "YourTask",
]
```

### Step 3: Add CLI Command

Edit `cli.py` (ensure to use `async def`):

```python
async def cmd_your_task(args):
    assistant = EditorAssistant(args.model, debug_mode=args.debug, thinking_level=args.thinking)
    input_obj = Input(type=InputType.PAPER, path=args.input_file)
    await assistant.process_multiple([input_obj], "your-task")  # Use task name string

# In create_parser():
your_parser = subparsers.add_parser("your-task", help="Your task description")
your_parser.add_argument("input_file", help="Input file path")
add_common_arguments(your_parser)
your_parser.set_defaults(func=cmd_your_task)
```

### Step 4: Create Prompt Template

Create `config/prompts/your_task.txt` and add loader in `config/load_prompt.py`.

---

## Configuration System

### Constants (`config/constants.py`)

All magic numbers are centralized here:

```python
# Token estimation
CHAR_TOKEN_RATIO = 3.5
MINIMAL_TOKEN_ACCEPTED = 100
PROMPT_OVERHEAD_TOKENS = 10000

# API retry
MAX_API_RETRIES = 3
INITIAL_RETRY_DELAY_SECONDS = 1

# Rate limiting
MIN_REQUEST_INTERVAL_SECONDS = 0.5
MAX_REQUESTS_PER_MINUTE = 60

# Caching
RESPONSE_CACHE_ENABLED = False
RESPONSE_CACHE_MAX_SIZE = 100
RESPONSE_CACHE_TTL_SECONDS = 3600
```

### Model Configuration (`config/llm_config.yml`)

Structure:

```yaml
provider-name:
  api_key_env_var: "ENV_VAR_NAME"
  api_base_url: "https://..."
  temperature: 0.6
  max_tokens: 32000
  context_window: 128000
  pricing_currency: "$"
  request_overrides: {}  # Optional: extra API params
  models:
    model-name:
      id: "actual-api-id"
      pricing: {input: X, output: Y}
```

---

## Testing Guide

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/unit/test_md_processor.py

# With coverage
pytest --cov=src/editor_assistant

# Verbose output
pytest -v
```

### Test Structure

```
tests/
├── conftest.py          # Shared fixtures
├── fixtures/            # Test data
│   ├── sample_data/     # Sample input files
│   └── *.py             # Python fixtures
├── unit/                # Unit tests
│   ├── test_md_converter.py
│   ├── test_md_processor_async.py # Async Processor tests
│   ├── test_llm_client_async.py   # Async Client tests
│   └── ...
└── integration/         # Integration tests
    ├── test_llm_api.py      # LLM API integration
    ├── test_async_flow.py   # End-to-end async flow
    └── ...
```

### Writing Tests (Async)

Tests for async components must use `pytest-asyncio`.

#### Test Data Thresholds
- **Content Length**: Benchmark and Stress tests require input content length > **1000 characters**.
  - *Reasoning*: Content validation warns when extracted content is shorter than `MIN_CHARS_WARNING_THRESHOLD` (default: 1000). Test generators (like `benchmark_async.py`) should exceed this threshold to avoid noisy warnings.

#### Unit Test Example (Async)

```python
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_my_async_feature(mock_llm_client):
    """Test with mocked async LLM client."""
    # mock_llm_client is provided by conftest.py
    # Ensure method is awaited
    result = await my_async_function(mock_llm_client)
    assert result is not None
```

#### Integration Test Example (Async)

```python
import pytest
import os

@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_api_call(budget_model_name):
    """Test with real API (costs money)."""
    from editor_assistant.llm_client import LLMClient
    
    # Initialize async client
    client = LLMClient(budget_model_name)
    async with client: # Or rely on auto-client management
        response = await client.generate_response("Test prompt")
        assert len(response) > 0
```

---

## Common Patterns

### Error Handling

Use the logging helpers from `config/logging_config.py`:

```python
from .config.logging_config import error, warning, progress, user_message

# User-facing error (red ✗)
error(f"Failed to process: {reason}")

# Warning (yellow ⚠)
warning(f"Content may be incomplete")

# Progress update (green •)
progress(f"Processing document...")

# Important info (blue •)
user_message(f"Output saved to: {path}")
```

### Content Validation

```python
from .content_validation import validate_content, BlockedPublisherError
from .config.logging_config import error

try:
    source_url = (
        md_article.source_path
        if md_article.source_path and str(md_article.source_path).startswith("http")
        else None
    )
    # validate_content() returns (is_valid, message) and may raise BlockedPublisherError
    is_valid, warn_msg = validate_content(md_article.content or "", source_url=source_url)
    if not is_valid:
        error(f"Content invalid: {warn_msg}")
        return None
except BlockedPublisherError as e:
    error(f"Blocked publisher: {e}")
    return None
```

### Rate Limiting (Async)

The `LLMClient` handles rate limiting automatically using `asyncio.sleep`. 

**Per-provider configuration** (in `llm_config.yml`):

```yaml
your-provider:
  # ... other settings ...
  rate_limit:
    min_interval_seconds: 1.0  # Min time between requests
    max_requests_per_minute: 30  # Max requests per minute (0 = unlimited)
```

---

## Performance & Concurrency

### Async Architecture

The system uses `asyncio` + `httpx` to handle high-concurrency workloads.

1. **Orchestration**: `EditorAssistant.process_multiple` uses `asyncio.gather` to fan out tasks.
2. **Concurrency Control**: `MDProcessor` uses `asyncio.Semaphore` (default: 5) to prevent overwhelming the API or local resources.
3. **Non-blocking I/O**: Network requests yielded to the event loop, allowing other tasks to proceed.

### Tuning

Adjust concurrency in `MDProcessor` (currently hardcoded or via init):

```python
# md_processor.py
class MDProcessor:
    def __init__(self, ..., max_concurrent: int = 5):
        self._semaphore = asyncio.Semaphore(max_concurrent)
```

### SQLite Persistence

SQLite is thread-safe but not fully concurrent for writes. The `storage` module handles locking, but extremely high write concurrency might hit `database is locked` errors. The current implementation uses synchronous SQLite calls offloaded to a thread pool (`asyncio.to_thread`) to prevent blocking the event loop.

### Run Lifecycle: Resume Command (`editor-assistant resume`)

The `resume` command is a **best-effort re-execution mechanism** for runs that were interrupted or never completed. It is intentionally simple: it does **not** attempt to checkpoint/continue mid-request; it **re-runs** the task using the stored inputs and metadata.

#### Current Behavior (as implemented)

- **Source of truth**: SQLite `runs` + `run_inputs` + `inputs` tables via `RunRepository.get_resumable_runs()` (`storage/repository.py`).
- **Eligibility**: runs with `status IN ('pending', 'aborted')`, ordered by `id ASC` (oldest first).
- **Dry run**: `editor-assistant resume --dry-run` prints resumable runs and exits without executing.
- **Execution path**:
  - For each resumable run, reconstructs input list from stored `inputs.type` and `inputs.source_path`.
  - Reconstructs execution settings from stored metadata (`task`, `model`, `thinking_level`, `stream`).
  - Calls the normal pipeline: `EditorAssistant(...).process_multiple(inputs, task, save_files=...)`.
- **Status updates**:
  - On success: updates the **original run** status to `success`.
  - On failure: updates the **original run** status to `failed` with an error message.
  - Note: the resumed execution also creates a **new** run record (because `MDProcessor.process_mds()` always creates a new run in the DB). The `resume` command treats the original run as the “work item” to close out.

#### Rationale (why this design)

- **Correctness-first**: continuing mid-stream is hard (partial outputs, unknown token usage, provider-dependent streaming semantics). Full re-run avoids inconsistent state.
- **Minimal surface area**: `resume` reuses the same production path (`process_multiple` → `process_mds`) instead of adding a parallel “resume pipeline”, lowering regression risk.
- **Operational practicality**: DB `status` acts like a lightweight queue. `aborted` (e.g. Ctrl+C) and stuck `pending` items can be inspected and re-run later without manual reconstruction.
- **Forward compatibility**: by re-running with current code/prompts/config, improved prompts/bug fixes automatically apply when resuming older runs.

### Run History Storage Schema + Export Command (`editor-assistant export`)

The run history database is normalized so that inputs can be **deduplicated** and reused across many runs, while outputs and token usage remain tied to a specific run.

#### Schema relationships (conceptual)

```text
            (many-to-many)                     (one-to-many)
  runs ───────────┐                     ┌───────────────► outputs
                  │                     │                 (run_id FK)
                  ▼                     │
              run_inputs                │
          (run_id, input_id)            │
                  ▲                     │                 (0..1 per run)
                  │                     └───────────────► token_usage
                inputs                                     (run_id FK)
          (dedup by content_hash)
```

- **`runs`**: one execution attempt (task/model/status/stream/thinking_level/currency/error_message, plus timestamp).
- **`inputs`**: a document/source (paper/news) with a `content_hash` to deduplicate identical content across runs.
- **`run_inputs`**: association table so a single run can have multiple inputs (e.g. `brief paper=... news=...`) and a single input can participate in many runs.
- **`outputs`**: one run can produce multiple named outputs (`main`, `bilingual`, etc.).
- **`token_usage`**: optional per-run aggregate usage/cost/time.

#### Current export implementation (as implemented)

The `export` command is a **snapshot export** of run history from SQLite to a file (`.json` or `.csv`):

- **CLI entry**: `cmd_export()` in `cli.py` chooses format by `--format` or file extension, then calls `RunRepository.export_runs(...)`.
- **Data assembly**: `export_runs()` loads runs (`ORDER BY id DESC`, optional `LIMIT`), and for each run:
  - loads `inputs` via `inputs JOIN run_inputs WHERE run_id = ?`
  - loads `outputs` via `outputs WHERE run_id = ?`
  - loads `token_usage` via `token_usage WHERE run_id = ?` (may be missing)
- **Output formats**:
  - **JSON**: full nested structure (runs + inputs + outputs + token_usage).
  - **CSV**: flattened summary (input titles combined; costs/tokens per run).

#### Rationale (why this design)

- **Avoid duplication**: storing full input content once (dedup by `content_hash`) keeps DB size smaller when reprocessing the same documents.
- **Support multi-source tasks**: `run_inputs` naturally models `paper + multiple news` use cases.
- **Flexible outputs**: `outputs` supports multiple output variants without schema changes.
- **Simple export logic**: export uses small, readable queries per run; easier to validate and extend.

### Batch Processing UI
The `batch` command uses the [Rich](https://github.com/Textualize/rich) library to display concurrent progress bars.
- **Overall Progress**: A main bar tracking total files processed.
- **Active Tasks**: Individual progress bars for currently processing files (concurrency limit: 5). Pending tasks are hidden to prevent terminal clutter.
- **Completion Handling**: Completed tasks are removed from the live view and replaced by a permanent log line.
- **Streaming**: Output tokens are streamed to update the progress bar status, keeping the interface clean.
- **Fallback**: If `rich` is not installed, it gracefully degrades to standard console output.

## Refactor Verification Protocol (Project Specific)

Lessons learned from v0.5.x async refactor. Verify these before merging complex changes:

### 1. State Isolation (The "Accumulator" Bug)
* **Context**: `LLMClient` is long-lived.
* **Check**: Ensure `token_usage` returned by `generate_response` is for *that specific request*, not the client's lifetime total. Run 3 items and check individual costs.

### 2. Negative Configuration (The "Flag Ignored" Bug)
* **Context**: `argparse` defaults vs code defaults.
* **Check**: Run `batch` *without* `--save-files` and ensure no files are created. Code like `val = args.flag or True` is forbidden.

### 3. Lifecycle & Interruption (The "Zombie" Bug)
* **Context**: Async tasks can be cancelled.
* **Check**: `Ctrl+C` must update DB status to `aborted`. Ensure `process_mds` has `try/except asyncio.CancelledError` blocks around API calls.

### 4. UI/Log Interference (The "Scrolling" Bug)
* **Context**: `Rich` TUI vs `logging` module.
* **Check**: When `Progress` is active, root logger level must be `WARNING` to suppress `INFO` logs that break the layout. Use `Console(force_terminal=True)` for robustness.
