# Developer Guide

This document provides technical documentation for developers contributing to Editor Assistant.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Module Reference](#module-reference)
3. [Adding a New LLM Model](#adding-a-new-llm-model)
4. [Adding a New Task Type](#adding-a-new-task-type)
5. [Configuration System](#configuration-system)
6. [Testing Guide](#testing-guide)
7. [Common Patterns](#common-patterns)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                           CLI Layer                             │
│                          (cli.py)                               │
│  Commands: brief, outline, translate, convert, clean            │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Orchestration Layer                        │
│                         (main.py)                               │
│                     EditorAssistant class                       │
└───────────────┬─────────────────────────────┬───────────────────┘
                │                             │
                ▼                             ▼
┌────────────────────────────┐     ┌──────────────────────────────────┐
│    Content Conversion      │     │       Content Processing         │
│    (md_converter.py)       │     │       (md_processor.py)          │
│    - PDF, DOCX, HTML       │ --> │       - Prompt building          │
│    - URL fetching          │     │       - LLM interaction          │
│    - Format detection      │     │       - Output formatting        │
└───────────────┬────────────┘     └───────────────┬──────────────────┘
                │                                  │
                ▼                                  ▼
┌────────────────────────────┐   ┌──────────────────────────────────┐
│   HTML Cleaning            │   │         LLM Client               │
│   (clean_html_to_md.py)    │   │       (llm_client.py)            │
│   - Readabilipy            │   │       - API calls                │
│   - Trafilatura            │   │       - Rate limiting            │
│                            │   │       - Response caching         │
└────────────────────────────┘   │       - Token tracking           │
                                 └───────────────┬──────────────────┘
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

### Data Flow

```
Input (URL/PDF/MD) 
    → MarkdownConverter.convert_content() 
    → MDArticle (normalized content)
    → MDProcessor.process() 
    → Prompt + LLMClient.generate_response()
    → Output (MD files + token report)
```

---

## Module Reference

### Core Modules

| Module | Purpose | Key Classes/Functions |
|--------|---------|----------------------|
| `cli.py` | Command-line interface | `main()`, `cmd_generate_brief()`, `cmd_generate_outline()` |
| `main.py` | Orchestration | `EditorAssistant` |
| `md_converter.py` | Format conversion | `MarkdownConverter` |
| `md_processor.py` | LLM processing | `MDProcessor` |
| `llm_client.py` | API interaction | `LLMClient`, `ResponseCache` |
| `clean_html_to_md.py` | HTML extraction | `CleanHTML2Markdown` |
| `content_validation.py` | Input validation | `validate_content()`, `BlockedPublisherError` |
| `data_models.py` | Data structures | `MDArticle`, `Input`, `ProcessType`, `InputType` |

### Config Modules

| Module | Purpose |
|--------|---------|
| `config/llm_config.yml` | LLM provider settings (API URLs, models, pricing) |
| `config/set_llm.py` | Model/Provider enums and YAML loader |
| `config/constants.py` | All configurable constants |
| `config/load_prompt.py` | Prompt template loader |
| `config/logging_config.py` | Logging utilities |
| `config/prompts/*.txt` | Jinja2 prompt templates |

---

## Adding a New LLM Model

### Step 1: Add to `LLMModel` Enum

Edit `config/set_llm.py`:

```python
class LLMModel(str, Enum):
    # existing models...
    
    # Add your new model
    your_new_model = "your-model-name"  # The CLI-facing name
```

### Step 2: Add Provider (if new)

If using a new provider, add to `ServiceProvider` enum:

```python
class ServiceProvider(str, Enum):
    # existing providers...
    
    your_provider = "your-provider"
```

### Step 3: Configure in YAML

Edit `config/llm_config.yml`:

```yaml
your-provider:
  api_key_env_var: "YOUR_API_KEY"
  api_base_url: "https://api.yourprovider.com/v1/chat/completions"
  temperature: 0.6
  max_tokens: 32000
  context_window: 128000
  pricing_currency: "$"
  models:
    your-model-name:
      id: "actual-api-model-id"
      pricing: {input: 1.00, output: 2.00}  # per 1M tokens
```

### Step 4: Set Environment Variable

```bash
export YOUR_API_KEY="your-api-key-here"
```

### Step 5: Test

```bash
editor-assistant brief paper=test.pdf --model your-model-name
```

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

Edit `cli.py`:

```python
def cmd_your_task(args):
    assistant = EditorAssistant(args.model, debug_mode=args.debug, thinking_level=args.thinking)
    input_obj = Input(type=InputType.PAPER, path=args.input_file)
    assistant.process_multiple([input_obj], "your-task")  # Use task name string

# In create_parser():
your_parser = subparsers.add_parser("your-task", help="Your task description")
your_parser.add_argument("input_file", help="Input file path")
add_common_arguments(your_parser)
your_parser.set_defaults(func=cmd_your_task)
```

### Step 4: Create Prompt Template

Create `config/prompts/your_task.txt` and add loader in `config/load_prompt.py`.

---

### Legacy Approach (deprecated)

The old approach required changes in 4 files:

### Step 1: Add ProcessType Enum

Edit `data_models.py`:

```python
class ProcessType(str, Enum):
    OUTLINE = 'outline'
    BRIEF = 'brief'
    TRANSLATE = 'translate'
    YOUR_NEW_TYPE = 'your_new_type'  # Add this
```

### Step 2: Create Prompt Template

Create `config/prompts/your_new_type.txt`:

```jinja2
You are an expert at {{ task_description }}.

## Input Content
{{ content }}

## Instructions
{{ specific_instructions }}
```

### Step 3: Add Prompt Loader

Edit `config/load_prompt.py`:

```python
def load_your_new_type_prompt(md_article: MDArticle) -> str:
    template = _load_template("your_new_type.txt")
    return template.render(
        content=md_article.content,
        title=md_article.title,
        # ... other variables
    )
```

### Step 4: Add Processing Logic

Edit `md_processor.py` in `process()` method:

```python
match process_type:
    case ProcessType.YOUR_NEW_TYPE:
        prompt = load_your_new_type_prompt(md_article)
        response = self.llm_client.generate_response(prompt, "your_new_type")
        self._save_response(response, md_article, "your_new_type")
```

### Step 5: Add CLI Command

Edit `cli.py`:

```python
def cmd_your_new_type(args):
    """Your new command description."""
    assistant = EditorAssistant(args.model, debug_mode=args.debug)
    input_obj = Input(type=InputType.PAPER, path=args.input_file)
    assistant.process_multiple([input_obj], ProcessType.YOUR_NEW_TYPE)

# In create_parser():
your_parser = subparsers.add_parser(
    "your-command",
    help="Description for help"
)
your_parser.add_argument("input_file", help="Input file path")
add_common_arguments(your_parser)
your_parser.set_defaults(func=cmd_your_new_type)
```

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
│   ├── test_md_processor.py
│   └── test_prompt_loader.py
└── integration/         # Integration tests
    ├── test_gemini_api.py
    └── test_multi_source_processing.py
```

### Writing Tests

```python
import pytest
from editor_assistant.data_models import ProcessType, InputType

def test_your_feature():
    """Test description."""
    # Arrange
    input_data = ...
    
    # Act
    result = your_function(input_data)
    
    # Assert
    assert result == expected
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

try:
    validate_content(md_article)
except BlockedPublisherError as e:
    error(f"Blocked publisher: {e}")
    return None
```

### Rate Limiting

The `LLMClient` handles rate limiting automatically. 

**Per-provider configuration** (in `llm_config.yml`):

```yaml
your-provider:
  # ... other settings ...
  rate_limit:
    min_interval_seconds: 1.0  # Min time between requests
    max_requests_per_minute: 30  # Max requests per minute (0 = unlimited)
```

**Global defaults** (in `constants.py`, used when provider doesn't specify):

```python
MIN_REQUEST_INTERVAL_SECONDS = 0.5  # Default min interval
MAX_REQUESTS_PER_MINUTE = 60        # Default max RPM
```

### Gemini 3 Thinking Mode

Control reasoning depth for Gemini 3+ models:

**CLI usage:**
```bash
# Let model decide dynamically (default)
editor-assistant brief paper=paper.pdf --model gemini-3-flash

# Force specific thinking level
editor-assistant brief paper=paper.pdf --model gemini-3-flash --thinking low
editor-assistant brief paper=paper.pdf --model gemini-3-pro --thinking high
```

**Thinking levels (via OpenAI-compatible `reasoning_effort`):**

| Level | Description |
|-------|-------------|
| `low` | Minimize latency, simple tasks |
| `medium` | Balanced (Flash only) |
| `high` | Deep reasoning, complex tasks |
| (default) | Model decides dynamically |

**Config file override** (in `llm_config.yml`):
```yaml
gemini:
  # ... other settings ...
  request_overrides:
    reasoning_effort: "high"  # Force all requests to use high
```

**Priority:** CLI `--thinking` > config `request_overrides` > model default

Reference: https://ai.google.dev/gemini-api/docs/gemini-3

---

### Streaming Output

By default, streaming is enabled for real-time response display:

```bash
# Default: streaming enabled
editor-assistant brief paper=paper.pdf

# Disable streaming (wait for complete response)
editor-assistant brief paper=paper.pdf --no-stream
```

**How it works:**
- Uses Server-Sent Events (SSE) for OpenAI-compatible APIs
- Content prints in real-time as it generates
- Token usage estimated if not provided by API in stream mode
- `--no-stream` applies to all tasks in multi-task mode

---

### Multi-task Execution

Process the same input with multiple tasks in one command:

```bash
# Serial execution: input converted once, then processed by each task
editor-assistant process paper=paper.pdf --tasks "brief,outline"

# Multi-source with multi-task
editor-assistant process paper=paper.pdf news=article.md --tasks "brief,outline,translate"
```

**How it works:**
1. Input files converted to markdown once
2. Each task executed serially on the same markdown content
3. Outputs saved separately per task

**Use cases:**
- Generate both brief and outline from same paper
- Batch processing for editorial workflows

---

### Response Caching

Enable for repeated prompts:

```python
# In constants.py
RESPONSE_CACHE_ENABLED = True
RESPONSE_CACHE_MAX_SIZE = 100
RESPONSE_CACHE_TTL_SECONDS = 3600

# Usage
client = LLMClient("model-name")
response = client.generate_response(prompt)  # May return cached response

# Check stats
print(client.get_cache_stats())
# {'hits': 5, 'misses': 10, 'hit_rate': '33.3%', 'size': 10, 'max_size': 100}
```

---

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes with tests
3. Update CHANGELOG.md
4. Submit PR to main

> Note: When new requirements or action items are discovered, record them in `TODO_agentname.md` under the appropriate branch/backlog section to keep work visible.

### Code Style

- Follow PEP 8
- Use type hints
- Document public functions with docstrings
- Keep functions focused and small

### Commit Messages

```
type: short description

- feat: new feature
- fix: bug fix
- docs: documentation
- refactor: code restructuring
- test: adding tests
- chore: maintenance
```

---

## Testing

### Test Structure

```
tests/
├── conftest.py              # Shared fixtures and pytest config
├── fixtures/                # Test data and sample files
│   ├── test_urls.py         # Real-world test URLs
│   ├── md_input.py          # Sample MDArticle fixtures
│   └── sample_data/         # PDF and markdown files
├── unit/                    # Fast tests with mocks (no API calls)
│   ├── test_data_models.py  # Data model tests
│   ├── test_tasks.py        # Task system tests
│   ├── test_llm_client.py   # LLM client tests
│   └── test_md_processor.py # Processor tests
└── integration/             # Tests with real API calls
    ├── test_llm_api.py      # LLM API integration
    ├── test_tasks_api.py    # Task execution tests
    └── test_cli.py          # CLI end-to-end tests
```

### Running Tests

```bash
# Run all unit tests (fast, no API calls)
pytest tests/unit/ -v

# Run specific test file
pytest tests/unit/test_tasks.py -v

# Run integration tests (costs money!)
pytest tests/integration/ -v

# Using the test runner script
python scripts/run_tests.py unit        # Unit tests only
python scripts/run_tests.py integration # Integration tests
python scripts/run_tests.py coverage    # With coverage report
python scripts/run_tests.py quick       # Essential tests only
```

**Integration model & cost note:** Integration tests default to `deepseek-v3.2` (cheap). Set `DEEPSEEK_API_KEY_VOLC`; legacy `DEEPSEEK_API_KEY` is no longer supported.

### Test Markers

| Marker | Description |
|--------|-------------|
| `@pytest.mark.unit` | Fast unit tests with mocks |
| `@pytest.mark.integration` | Tests with real API calls |
| `@pytest.mark.slow` | Tests taking > 5 seconds |
| `@pytest.mark.expensive` | Tests that cost significant money |

```bash
# Run only unit tests
pytest -m "unit"

# Skip slow tests
pytest -m "not slow"

# Run integration but skip expensive
pytest tests/integration/ -m "not expensive"

# Run storage tests specifically
pytest tests/unit/test_storage.py -v
```

### Test Categories

| Test File | Purpose | API Calls |
|-----------|---------|-----------|
| `test_data_models.py` | Data model validation | No |
| `test_tasks.py` | Task registry and validation | No |
| `test_llm_client.py` | LLM client initialization | No |
| `test_md_processor.py` | Processing pipeline | No |
| `test_storage.py` | Database operations (39 tests) | No |
| `test_llm_api.py` | Real LLM API calls | Yes |
| `test_tasks_api.py` | Tasks with real APIs | Yes |
| `test_cli.py` | CLI command execution | Yes |
| `test_storage_integration.py` | Storage with real runs | Yes |

### Writing New Tests

#### Unit Test Example

```python
import pytest
from editor_assistant.data_models import MDArticle, InputType

class TestMyFeature:
    
    @pytest.mark.unit
    def test_basic_functionality(self, mock_llm_client):
        """Test with mocked LLM client (no API call)."""
        # mock_llm_client is provided by conftest.py
        result = my_function(mock_llm_client)
        assert result is not None
```

#### Integration Test Example

```python
import pytest
import os

# Skip if API key not set
pytestmark = pytest.mark.skipif(
    not os.getenv("DEEPSEEK_API_KEY"),
    reason="DEEPSEEK_API_KEY not set"
)

class TestAPIIntegration:
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_real_api_call(self, budget_model_name):
        """Test with real API (costs money)."""
        from editor_assistant.llm_client import LLMClient
        client = LLMClient(budget_model_name)
        response = client.generate_response("Test prompt")
        assert len(response) > 0
```

### Test Fixtures

Key fixtures from `conftest.py`:

| Fixture | Description |
|---------|-------------|
| `temp_dir` | Temporary directory for test outputs |
| `sample_paper_content` | Shannon paper content as string |
| `sample_paper_article` | MDArticle with paper content |
| `mock_llm_client` | Mocked LLM client for unit tests |
| `mock_llm_response` | Standard mock response text |
| `budget_model_name` | Cheapest model name for integration tests |
| `real_llm_client` | Real LLM client (integration only) |

### Test Data

Test URLs in `tests/fixtures/test_urls.py`:

```python
from tests.fixtures.test_urls import (
    PAPER_HTML_LONG,  # Long arxiv paper (HTML)
    PAPER_PDF_LONG,   # Long arxiv paper (PDF)
    NEWS_BLOG,        # Blog post
    NEWS_SHORT,       # Short news article
)
```

Sample files in `tests/fixtures/sample_data/`:
- `A Mathematical Theory of Communication.md/.pdf` - Shannon's classic paper
- `Weaver_Warren_1949_The_Mathematics_of_Communication.md/.pdf` - Related essay

---

## Storage Module

The storage module provides SQLite-based persistence for run history, enabling tracking, querying, and analysis of all processing runs.

### Database Location

Default: `~/.editor_assistant/runs.db`

Override with environment variable:
```bash
export EDITOR_ASSISTANT_DB_DIR=/custom/path
```

### Schema Overview

```
inputs (independent, deduplication via content_hash)
    │
    ├── N:M ──► run_inputs ◄── N:1 ── runs
    │                              │
    │                              ├── 1:N ── outputs
    │                              │
    │                              └── 1:1 ── token_usage
```

**Tables:**

| Table | Purpose |
|-------|---------|
| `inputs` | Stores unique inputs with content hash for deduplication |
| `runs` | Run metadata (task, model, status, timestamp) |
| `run_inputs` | Many-to-many relationship between runs and inputs |
| `outputs` | Generated outputs (text or JSON) |
| `token_usage` | Token counts and costs per run |

### CLI Commands

```bash
# List recent runs
editor-assistant history
editor-assistant history -n 50              # Show last 50
editor-assistant history --search "arxiv"   # Search by title

# Usage statistics
editor-assistant stats                      # Last 7 days
editor-assistant stats -d 30                # Last 30 days

# Run details
editor-assistant show 1                     # Show run #1
editor-assistant show 1 --output            # Include full output
```

### Programmatic Usage

```python
from editor_assistant.storage import RunRepository

repo = RunRepository()

# Get recent runs
runs = repo.get_recent_runs(limit=20)

# Get run details
details = repo.get_run_details(run_id=1)

# Get statistics
stats = repo.get_stats(days=7)

# Search by title
matches = repo.search_by_title("quantum", limit=10)
```

### Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `EDITOR_ASSISTANT_TEST_DB_DIR` | **Test database** (highest priority) | - |
| `EDITOR_ASSISTANT_DB_DIR` | Production override | - |
| (none) | Default production | `~/.editor_assistant/` |

**Test/Production Isolation**:
- `conftest.py` automatically sets `EDITOR_ASSISTANT_TEST_DB_DIR` for all tests
- Production CLI never sees this variable (different process)
- Tests cannot accidentally pollute production database

### GUI Tools

Recommended tools for viewing the SQLite database:

- **DB Browser for SQLite**: `brew install --cask db-browser-for-sqlite`
- **TablePlus**: `brew install --cask tableplus`
- **datasette**: `pip install datasette && datasette ~/.editor_assistant/runs.db`

### Example Queries

```sql
-- All runs for a specific paper (by content hash)
SELECT r.*, i.title FROM runs r
JOIN run_inputs ri ON r.id = ri.run_id
JOIN inputs i ON ri.input_id = i.id
WHERE i.content_hash = 'abc123...';

-- Compare models on the same input
SELECT r.model, r.timestamp, o.content
FROM runs r
JOIN run_inputs ri ON r.id = ri.run_id
JOIN inputs i ON ri.input_id = i.id
JOIN outputs o ON r.id = o.run_id
WHERE i.title LIKE '%quantum%' AND o.output_type = 'main';

-- Cost summary by model (last 30 days)
SELECT r.model, 
       COUNT(*) as runs,
       SUM(t.cost_input + t.cost_output) as total_cost
FROM runs r
JOIN token_usage t ON r.id = t.run_id
WHERE r.timestamp > datetime('now', '-30 days')
GROUP BY r.model ORDER BY total_cost DESC;
```

### Testing the Storage Module

```bash
# Run all 39 storage unit tests
pytest tests/unit/test_storage.py -v

# Test specific categories
pytest tests/unit/test_storage.py -k "TestManyToManyRelationship"
pytest tests/unit/test_storage.py -k "TestCurrencyHandling"
pytest tests/unit/test_storage.py -k "TestEdgeCases"
```

Key test scenarios covered:
- **Input deduplication**: Same content → same input ID
- **Many-to-many relationships**: One input → multiple runs, one run → multiple inputs
- **Currency handling**: Different models can have different pricing currencies
- **Cascade deletes**: Deleting a run removes related outputs and token usage
- **Edge cases**: Unicode, empty content, long content, special characters
- **Concurrency**: Concurrent reads, concurrent writes (with expected SQLite limitations)

