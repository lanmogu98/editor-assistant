# LLM Package Extraction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extract the current Editor Assistant LLM infrastructure into an external Python package that can be consumed by both `editor-assistant` and LinkResearcher workers.

**Architecture:** Create a provider-agnostic LLM execution package with config loading, retry/rate limiting, response caching, token estimation, usage reporting, structured output hooks, and execution metadata. `editor-assistant` becomes an application layer that owns document conversion, tasks, prompts, SQLite persistence, CLI behavior, and optional file output. LinkResearcher consumes the same package for LLM execution while keeping durable task lifecycle, attempts, artifacts, apply semantics, and worker schemas in its own repositories.

**Tech Stack:** Python 3.10+, `uv`, `httpx`, `pydantic`, `pyyaml`, stdlib `logging`, `pytest`, `pytest-asyncio`, `black`, `flake8`, `mypy`.

## Global Constraints

- External package target distribution name: `llm-exec-core`.
- External package target import name: `llm_exec_core`.
- `editor-assistant` version bump target: `0.6.0`.
- Preserve one compatibility cycle for `editor_assistant.llm_client`.
- Preserve one compatibility cycle for `editor_assistant.config.llm_models`.
- Preserve legacy LLM constants from `editor_assistant.config.constants` for one compatibility cycle.
- Do not move task definitions, prompt templates, document conversion, SQLite storage, CLI commands, or app logging into `llm_exec_core`.
- Core package must use stdlib `logging`; it must not import `editor_assistant.config.logging_config`.
- Core package must not write token usage reports to disk; formatting returns strings, persistence belongs to callers.
- Unit tests must mock API calls; no test API calls in unit tests.
- LinkResearcher durable task lifecycle, task/attempt/artifact/result schema, and apply semantics stay outside this package.
- This plan is a discussion artifact until approved by the repository owner.

---

## Scope Interpretation

Issue #24 describes an in-repo lift-ready refactor, but the owner clarification makes the true deliverable larger: the LLM infrastructure should become an external dependency used by `editor-assistant` and LinkResearcher.

The implementation should therefore not stop at `src/editor_assistant/llm/`. That intermediate shape is useful only as a short-lived extraction technique. The completion state is:

- `llm_exec_core` exists as a separate Python package.
- `editor-assistant` imports LLM execution from `llm_exec_core`.
- Legacy `editor_assistant` import paths still work for one release cycle.
- LinkResearcher has a documented minimal import/API contract.
- Package reference and version pin strategy are documented.

## Approach Options

### Option A: In-Repo Lift-Ready Only

Move `llm_client.py`, `llm_models.py`, `llm_config.yml`, constants, and token helpers into `src/editor_assistant/llm/`, then leave external package creation for another issue.

Trade-off: lowest immediate blast radius, but it does not satisfy the clarified goal. LinkResearcher still cannot depend on a package without copying from `editor-assistant`.

### Option B: Direct External Package Extraction

Create `llm-exec-core` as the canonical package, migrate core logic into it, then update `editor-assistant` to consume it through a pinned dependency and compatibility shims.

Trade-off: larger first PR and requires package/version decisions now, but it matches the actual target state and forces the public API to be designed before migration.

### Option C: Temporary Monorepo Package

Create `packages/llm_exec_core/` inside `editor-assistant`, consume it via a path dependency, and split it into a separate repository after tests pass.

Trade-off: simpler local editing, but the dependency is not truly external. It risks treating the monorepo layout as the API boundary and delaying downstream packaging decisions.

**Recommendation:** Use Option B. The owner intent is an external package shared by two applications, so the implementation should make package boundaries, versioning, and downstream contracts real from the start.

## Target File Structure

### External Package: `../llm-exec-core`

- Create: `../llm-exec-core/pyproject.toml`
- Create: `../llm-exec-core/README.md`
- Create: `../llm-exec-core/CHANGELOG.md`
- Create: `../llm-exec-core/src/llm_exec_core/__init__.py`
- Create: `../llm-exec-core/src/llm_exec_core/client.py`
- Create: `../llm-exec-core/src/llm_exec_core/config.py`
- Create: `../llm-exec-core/src/llm_exec_core/constants.py`
- Create: `../llm-exec-core/src/llm_exec_core/tokens.py`
- Create: `../llm-exec-core/src/llm_exec_core/usage.py`
- Create: `../llm-exec-core/src/llm_exec_core/types.py`
- Create: `../llm-exec-core/src/llm_exec_core/llm_config.yml`
- Create: `../llm-exec-core/tests/unit/test_client.py`
- Create: `../llm-exec-core/tests/unit/test_config.py`
- Create: `../llm-exec-core/tests/unit/test_tokens.py`
- Create: `../llm-exec-core/tests/unit/test_usage.py`
- Create: `../llm-exec-core/tests/unit/test_types.py`

Responsibilities:

- `client.py`: async HTTP execution, retry, rate limiting, response cache, streaming, token usage tracking.
- `config.py`: Pydantic provider/model schema and injectable catalog loading.
- `constants.py`: LLM-only constants.
- `tokens.py`: `estimate_tokens`.
- `usage.py`: pure usage report formatting.
- `types.py`: result, usage, execution metadata, structured output hook types.
- `llm_config.yml`: default model catalog copied from current `editor_assistant` config.

### Editor Assistant Repository

- Modify: `pyproject.toml`
- Modify: `README.md`
- Modify: `CHANGELOG.md`
- Modify: `DEVELOPER_GUIDE.md`
- Modify: `src/editor_assistant/__init__.py`
- Modify: `src/editor_assistant/config/__init__.py`
- Modify: `src/editor_assistant/config/constants.py`
- Modify: `src/editor_assistant/config/llm_models.py`
- Modify: `src/editor_assistant/llm_client.py`
- Modify: `src/editor_assistant/md_processor.py`
- Modify: `src/editor_assistant/cli.py`
- Modify: `tests/conftest.py`
- Modify: `tests/unit/test_regression_refactor.py`
- Modify: `tests/unit/test_llm_client.py`
- Modify: `tests/unit/test_llm_client_async.py`
- Modify: `tests/unit/test_md_processor.py`
- Modify: `tests/unit/test_md_processor_async.py`
- Modify: `tests/stress/test_sqlite_concurrency.py`
- Modify: `tests/stress/test_error_boundaries.py`
- Modify: `tests/stress/test_real_load.py`

Responsibilities:

- App code owns tasks, document conversion, SQLite, CLI, output file paths, progress formatting, and app logging.
- Compatibility shims keep old imports working.
- Tests verify both the new dependency path and the old import paths.

## Public API Contract

### Package Import Contract

```python
from llm_exec_core import LLMClient
from llm_exec_core.config import get_model_details, get_supported_models, load_all_settings
from llm_exec_core.tokens import estimate_tokens
from llm_exec_core.usage import format_usage_report
from llm_exec_core.types import ExecutionMetadata, LLMResult, TokenUsage
```

### Client Contract

```python
from pathlib import Path
from typing import Any, Callable


class LLMClient:
    def __init__(
        self,
        model_name: str,
        thinking_level: str | None = None,
        config_source: Path | dict | None = None,
    ) -> None:
        raise NotImplementedError

    async def generate(
        self,
        prompt: str,
        request_name: str = "unnamed_request",
        stream: bool = False,
        stream_callback: Callable[[str], None] | None = None,
        structured_output_hook: Callable[[str], Any] | None = None,
        trace_context: dict[str, Any] | None = None,
        run_id: str | None = None,
        request_id: str | None = None,
    ) -> LLMResult:
        raise NotImplementedError

    async def generate_response(
        self,
        prompt: str,
        request_name: str = "unnamed_request",
        stream: bool = False,
        stream_callback: Callable[[str], None] | None = None,
    ) -> tuple[str, dict[str, Any]]:
        raise NotImplementedError
```

`generate()` is the new structured API. `generate_response()` remains the compatibility API and returns `(text, usage_dict)` like the current implementation.

### Result Contract

```python
from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class TokenUsage:
    input_tokens: int
    output_tokens: int
    total_tokens: int
    input_cost: float
    output_cost: float
    total_cost: float
    currency: str

    def to_legacy_dict(self) -> dict[str, Any]:
        return {
            "total_input_tokens": self.input_tokens,
            "total_output_tokens": self.output_tokens,
            "cost": {
                "input_cost": self.input_cost,
                "output_cost": self.output_cost,
                "total_cost": self.total_cost,
            },
            "process_times": {"total_time": 0},
        }


@dataclass
class ExecutionMetadata:
    request_id: str
    run_id: str | None
    request_name: str
    model_name: str
    model_id: str
    provider_name: str
    started_at: str
    finished_at: str
    duration_seconds: float
    trace_context: dict[str, Any]


@dataclass
class LLMResult:
    text: str
    usage: TokenUsage
    metadata: ExecutionMetadata
    structured: Any | None = None

    def to_legacy_tuple(self) -> tuple[str, dict[str, Any]]:
        usage = self.usage.to_legacy_dict()
        usage["metadata"] = asdict(self.metadata)
        return self.text, usage
```

### Config Injection Contract

```python
from pathlib import Path
from typing import Any


def load_all_settings(
    config_source: Path | dict[str, Any] | None = None,
) -> dict[str, ProviderSettings]:
    raise NotImplementedError


def get_model_details(
    model_name: str,
    config_source: Path | dict[str, Any] | None = None,
) -> tuple[str, ProviderSettings, ModelDetails]:
    raise NotImplementedError
```

`get_model_details()` returns provider name as the first tuple item in the new package. The legacy `editor_assistant.config.llm_models.get_model_details()` shim preserves the old two-item return shape for one compatibility cycle unless the owner approves a breaking change.

### Structured Output Hook Contract

```python
def parse_json_response(text: str) -> dict[str, Any]:
    return json.loads(text)


result = await client.generate(
    prompt,
    request_name="extract_metadata",
    structured_output_hook=parse_json_response,
    trace_context={"source": "linkresearcher-content-worker"},
    run_id="worker-run-123",
)
```

The hook receives final text and returns caller-owned structured data. The core package does not define LinkResearcher schemas.

### Cancellation Contract

`LLMClient.generate()` and `LLMClient.generate_response()` must not swallow `asyncio.CancelledError`. They may let context managers close HTTP resources, then re-raise cancellation. Caller-owned systems decide how to mark runs, attempts, and artifacts.

## Implementation Tasks

### Task 1: Create External Package Skeleton

**Files:**
- Create: `../llm-exec-core/pyproject.toml`
- Create: `../llm-exec-core/src/llm_exec_core/__init__.py`
- Create: `../llm-exec-core/tests/unit/test_types.py`

**Interfaces:**
- Produces: importable package `llm_exec_core`
- Produces: version `0.1.0`

- [ ] **Step 1: Write failing import/version test**

```python
def test_package_imports_with_version():
    import llm_exec_core

    assert llm_exec_core.__version__ == "0.1.0"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest ../llm-exec-core/tests/unit/test_types.py::test_package_imports_with_version -v`

Expected: FAIL with `ModuleNotFoundError: No module named 'llm_exec_core'`.

- [ ] **Step 3: Add package metadata and version export**

`../llm-exec-core/pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=64.0"]
build-backend = "setuptools.build_meta"

[project]
name = "llm-exec-core"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "httpx>=0.25.0",
    "pydantic",
    "pyyaml",
]

[dependency-groups]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.0.0",
    "flake8>=6.0.0",
    "mypy>=1.0.0",
]

[tool.setuptools]
package-data = { "llm_exec_core" = ["*.yml"] }
```

`../llm-exec-core/src/llm_exec_core/__init__.py`:

```python
"""Provider-agnostic LLM execution core."""

__version__ = "0.1.0"

__all__ = ["__version__"]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest ../llm-exec-core/tests/unit/test_types.py::test_package_imports_with_version -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git -C ../llm-exec-core add pyproject.toml src tests
git -C ../llm-exec-core commit -m "chore: scaffold llm execution core"
```

### Task 2: Move LLM Constants and Token Estimation

**Files:**
- Create: `../llm-exec-core/src/llm_exec_core/constants.py`
- Create: `../llm-exec-core/src/llm_exec_core/tokens.py`
- Create: `../llm-exec-core/tests/unit/test_tokens.py`

**Interfaces:**
- Produces: `estimate_tokens(text: str) -> int`
- Produces: LLM constants used by `client.py`

- [ ] **Step 1: Write failing token estimation tests**

```python
from llm_exec_core.tokens import estimate_tokens


def test_estimate_tokens_empty_text_is_zero():
    assert estimate_tokens("") == 0


def test_estimate_tokens_english_uses_default_ratio():
    assert estimate_tokens("a" * 35) == 10


def test_estimate_tokens_chinese_heavy_text_uses_cjk_ratio():
    assert estimate_tokens("科学" * 20) > estimate_tokens("science" * 5)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest ../llm-exec-core/tests/unit/test_tokens.py -v`

Expected: FAIL with `ModuleNotFoundError` for `llm_exec_core.tokens`.

- [ ] **Step 3: Add constants and token estimator**

`../llm-exec-core/src/llm_exec_core/constants.py`:

```python
"""LLM execution constants."""

CHAR_TOKEN_RATIO_EN = 3.5
CHAR_TOKEN_RATIO_ZH = 1.5
CHAR_TOKEN_RATIO = CHAR_TOKEN_RATIO_EN

MAX_API_RETRIES = 3
INITIAL_RETRY_DELAY_SECONDS = 1
API_REQUEST_TIMEOUT_SECONDS = 180

MIN_REQUEST_INTERVAL_SECONDS = 0.5
MAX_REQUESTS_PER_MINUTE = 60
RATE_LIMIT_WARNINGS_ENABLED = True

RESPONSE_CACHE_ENABLED = False
RESPONSE_CACHE_MAX_SIZE = 100
RESPONSE_CACHE_TTL_SECONDS = 3600
```

`../llm-exec-core/src/llm_exec_core/tokens.py`:

```python
"""Token estimation helpers."""

from .constants import CHAR_TOKEN_RATIO_EN, CHAR_TOKEN_RATIO_ZH


def estimate_tokens(text: str) -> int:
    if not text:
        return 0

    chinese_chars = sum(1 for char in text if "\u4e00" <= char <= "\u9fff")
    total_chars = len(text)
    if total_chars == 0:
        return 0

    chinese_ratio = chinese_chars / total_chars
    if chinese_ratio > 0.2:
        blended_ratio = (
            chinese_ratio * CHAR_TOKEN_RATIO_ZH
            + (1 - chinese_ratio) * CHAR_TOKEN_RATIO_EN
        )
    else:
        blended_ratio = CHAR_TOKEN_RATIO_EN

    return int(total_chars / blended_ratio)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest ../llm-exec-core/tests/unit/test_tokens.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git -C ../llm-exec-core add src/llm_exec_core/constants.py src/llm_exec_core/tokens.py tests/unit/test_tokens.py
git -C ../llm-exec-core commit -m "feat: add llm constants and token estimation"
```

### Task 3: Implement Injectable Model Catalog

**Files:**
- Create: `../llm-exec-core/src/llm_exec_core/config.py`
- Create: `../llm-exec-core/src/llm_exec_core/llm_config.yml`
- Create: `../llm-exec-core/tests/unit/test_config.py`

**Interfaces:**
- Produces: `load_all_settings(config_source: Path | dict[str, Any] | None = None) -> dict[str, ProviderSettings]`
- Produces: `get_model_details(model_name: str, config_source: Path | dict[str, Any] | None = None) -> tuple[str, ProviderSettings, ModelDetails]`
- Produces: `get_supported_models(config_source: Path | dict[str, Any] | None = None) -> list[str]`

- [ ] **Step 1: Write failing config injection tests**

```python
from llm_exec_core.config import get_model_details, get_supported_models, load_all_settings


CUSTOM_CONFIG = {
    "_shared": {"ignored": True},
    "test-provider": {
        "api_key_env_var": "TEST_API_KEY",
        "api_base_url": "https://example.invalid/chat/completions",
        "temperature": 0.1,
        "max_tokens": 128,
        "context_window": 4096,
        "pricing_currency": "$",
        "models": {
            "test-model": {
                "id": "provider-model-id",
                "pricing": {"input": 1.0, "output": 2.0},
            }
        },
    },
}


def test_load_all_settings_accepts_dict_and_skips_private_keys():
    settings = load_all_settings(CUSTOM_CONFIG)

    assert list(settings) == ["test-provider"]


def test_get_supported_models_accepts_dict():
    assert get_supported_models(CUSTOM_CONFIG) == ["test-model"]


def test_get_model_details_returns_provider_name_settings_and_model():
    provider_name, provider_settings, model_details = get_model_details(
        "test-model", CUSTOM_CONFIG
    )

    assert provider_name == "test-provider"
    assert provider_settings.api_key_env_var == "TEST_API_KEY"
    assert model_details.id == "provider-model-id"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest ../llm-exec-core/tests/unit/test_config.py -v`

Expected: FAIL with `ModuleNotFoundError` for `llm_exec_core.config`.

- [ ] **Step 3: Implement config loader**

Implementation must preserve the current Pydantic schemas from `src/editor_assistant/config/llm_models.py` and add dict/path injection. Default `config_source=None` loads `Path(__file__).parent / "llm_config.yml"`.

- [ ] **Step 4: Copy default model catalog**

Copy `src/editor_assistant/config/llm_config.yml` to `../llm-exec-core/src/llm_exec_core/llm_config.yml`.

- [ ] **Step 5: Run tests to verify they pass**

Run: `uv run pytest ../llm-exec-core/tests/unit/test_config.py -v`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git -C ../llm-exec-core add src/llm_exec_core/config.py src/llm_exec_core/llm_config.yml tests/unit/test_config.py
git -C ../llm-exec-core commit -m "feat: add injectable llm model catalog"
```

### Task 4: Add Result, Usage, Metadata, and Report Formatting

**Files:**
- Create: `../llm-exec-core/src/llm_exec_core/types.py`
- Create: `../llm-exec-core/src/llm_exec_core/usage.py`
- Modify: `../llm-exec-core/src/llm_exec_core/__init__.py`
- Create: `../llm-exec-core/tests/unit/test_usage.py`
- Modify: `../llm-exec-core/tests/unit/test_types.py`

**Interfaces:**
- Produces: `TokenUsage`
- Produces: `ExecutionMetadata`
- Produces: `LLMResult`
- Produces: `format_usage_report(project_name: str, model: str, model_name: str, pricing_currency: str, token_usage: dict[str, Any]) -> str`

- [ ] **Step 1: Write failing usage/report tests**

```python
from llm_exec_core.usage import format_usage_report


def test_format_usage_report_returns_text_without_writing_file():
    report = format_usage_report(
        project_name="Test Project",
        model="provider-model-id",
        model_name="test-model",
        pricing_currency="$",
        token_usage={
            "total_input_tokens": 10,
            "total_output_tokens": 20,
            "requests": [
                {
                    "name": "brief",
                    "input_tokens": 10,
                    "output_tokens": 20,
                    "total_tokens": 30,
                    "process_time": 0.5,
                    "input_cost": 0.001,
                    "output_cost": 0.002,
                    "total_cost": 0.003,
                    "timestamp": "2026-06-18 12:00:00",
                }
            ],
            "process_times": {"total_time": 0.5, "request_times": []},
            "cost": {
                "input_cost": 0.001,
                "output_cost": 0.002,
                "total_cost": 0.003,
            },
        },
        timestamp="2026-06-18 12:00:01",
    )

    assert "Token Usage Report for Test Project" in report
    assert "Model: provider-model-id (test-model)" in report
    assert "Total Tokens: 30" in report
    assert "Request 1: brief" in report
```

- [ ] **Step 2: Write failing result compatibility test**

```python
from llm_exec_core.types import ExecutionMetadata, LLMResult, TokenUsage


def test_llm_result_to_legacy_tuple_preserves_existing_usage_shape():
    result = LLMResult(
        text="hello",
        usage=TokenUsage(
            input_tokens=1,
            output_tokens=2,
            total_tokens=3,
            input_cost=0.1,
            output_cost=0.2,
            total_cost=0.3,
            currency="$",
        ),
        metadata=ExecutionMetadata(
            request_id="req-1",
            run_id="run-1",
            request_name="brief",
            model_name="test-model",
            model_id="provider-model-id",
            provider_name="test-provider",
            started_at="2026-06-18T00:00:00Z",
            finished_at="2026-06-18T00:00:01Z",
            duration_seconds=1.0,
            trace_context={"source": "unit"},
        ),
    )

    text, usage = result.to_legacy_tuple()

    assert text == "hello"
    assert usage["total_input_tokens"] == 1
    assert usage["total_output_tokens"] == 2
    assert usage["cost"]["total_cost"] == 0.3
    assert usage["metadata"]["request_id"] == "req-1"
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `uv run pytest ../llm-exec-core/tests/unit/test_usage.py ../llm-exec-core/tests/unit/test_types.py -v`

Expected: FAIL with missing `llm_exec_core.usage` and missing dataclasses.

- [ ] **Step 4: Implement dataclasses and report formatting**

`format_usage_report()` must contain the current report text shape from `LLMClient.save_token_usage_report()` and must not call `open()`, `Path.mkdir()`, or app progress functions.

- [ ] **Step 5: Run tests to verify they pass**

Run: `uv run pytest ../llm-exec-core/tests/unit/test_usage.py ../llm-exec-core/tests/unit/test_types.py -v`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git -C ../llm-exec-core add src/llm_exec_core/types.py src/llm_exec_core/usage.py src/llm_exec_core/__init__.py tests/unit/test_usage.py tests/unit/test_types.py
git -C ../llm-exec-core commit -m "feat: add llm result metadata and usage formatting"
```

### Task 5: Extract Async LLM Client into Core Package

**Files:**
- Create: `../llm-exec-core/src/llm_exec_core/client.py`
- Modify: `../llm-exec-core/src/llm_exec_core/__init__.py`
- Create: `../llm-exec-core/tests/unit/test_client.py`

**Interfaces:**
- Produces: `LLMClient.generate(...) -> LLMResult`
- Produces: `LLMClient.generate_response(...) -> tuple[str, dict[str, Any]]`
- Consumes: config loader, constants, token estimator, result dataclasses, usage formatting

- [ ] **Step 1: Write failing non-streaming compatibility test**

```python
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from llm_exec_core.client import LLMClient


@pytest.mark.asyncio
async def test_generate_response_returns_legacy_tuple(monkeypatch):
    monkeypatch.setenv("TEST_API_KEY", "test-key")
    config = {
        "test-provider": {
            "api_key_env_var": "TEST_API_KEY",
            "api_base_url": "https://example.invalid/chat/completions",
            "temperature": 0.1,
            "max_tokens": 128,
            "context_window": 4096,
            "pricing_currency": "$",
            "models": {
                "test-model": {
                    "id": "provider-model-id",
                    "pricing": {"input": 1.0, "output": 2.0},
                }
            },
        }
    }

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Test response"}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 20},
    }
    mock_response.raise_for_status = MagicMock()

    with patch("llm_exec_core.client.httpx.AsyncClient") as mock_cls:
        mock_httpx_client = AsyncMock()
        mock_httpx_client.post.return_value = mock_response
        mock_cls.return_value = mock_httpx_client

        client = LLMClient("test-model", config_source=config)
        response, usage = await client.generate_response("Hello")

    assert response == "Test response"
    assert usage["total_input_tokens"] == 10
    assert usage["total_output_tokens"] == 20
```

- [ ] **Step 2: Write failing structured result test**

```python
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from llm_exec_core.client import LLMClient


@pytest.mark.asyncio
async def test_generate_applies_structured_output_hook(monkeypatch):
    monkeypatch.setenv("TEST_API_KEY", "test-key")
    config = {
        "test-provider": {
            "api_key_env_var": "TEST_API_KEY",
            "api_base_url": "https://example.invalid/chat/completions",
            "temperature": 0.1,
            "max_tokens": 128,
            "context_window": 4096,
            "pricing_currency": "$",
            "models": {
                "test-model": {
                    "id": "provider-model-id",
                    "pricing": {"input": 1.0, "output": 2.0},
                }
            },
        }
    }
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": '{"title": "A"}'}}],
        "usage": {"prompt_tokens": 5, "completion_tokens": 6},
    }
    mock_response.raise_for_status = MagicMock()

    with patch("llm_exec_core.client.httpx.AsyncClient") as mock_cls:
        mock_httpx_client = AsyncMock()
        mock_httpx_client.post.return_value = mock_response
        mock_cls.return_value = mock_httpx_client

        client = LLMClient("test-model", config_source=config)
        result = await client.generate(
            "Hello",
            request_name="extract",
            structured_output_hook=json.loads,
            trace_context={"source": "unit"},
            run_id="run-1",
            request_id="req-1",
        )

    assert result.text == '{"title": "A"}'
    assert result.structured == {"title": "A"}
    assert result.metadata.provider_name == "test-provider"
    assert result.metadata.request_id == "req-1"
    assert result.metadata.trace_context == {"source": "unit"}
```

- [ ] **Step 3: Write failing cancellation test**

```python
import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from llm_exec_core.client import LLMClient


@pytest.mark.asyncio
async def test_generate_response_reraises_cancelled_error(monkeypatch):
    monkeypatch.setenv("TEST_API_KEY", "test-key")
    config = {
        "test-provider": {
            "api_key_env_var": "TEST_API_KEY",
            "api_base_url": "https://example.invalid/chat/completions",
            "temperature": 0.1,
            "max_tokens": 128,
            "context_window": 4096,
            "pricing_currency": "$",
            "models": {
                "test-model": {
                    "id": "provider-model-id",
                    "pricing": {"input": 1.0, "output": 2.0},
                }
            },
        }
    }

    with patch("llm_exec_core.client.httpx.AsyncClient") as mock_cls:
        mock_httpx_client = AsyncMock()
        mock_httpx_client.post.side_effect = asyncio.CancelledError()
        mock_cls.return_value = mock_httpx_client

        client = LLMClient("test-model", config_source=config)

        with pytest.raises(asyncio.CancelledError):
            await client.generate_response("Hello")
```

- [ ] **Step 4: Run tests to verify they fail**

Run: `uv run pytest ../llm-exec-core/tests/unit/test_client.py -v`

Expected: FAIL with missing `llm_exec_core.client`.

- [ ] **Step 5: Move and adapt client implementation**

Move the behavior from `src/editor_assistant/llm_client.py` into `../llm-exec-core/src/llm_exec_core/client.py` with these changes:

- Replace `.config.logging_config.warning` and `.config.logging_config.progress` with `logger.warning()` and `logger.info()` from `logging.getLogger(__name__)`.
- Replace `.config.constants` imports with `.constants`.
- Replace `.utils.estimate_tokens` with `.tokens.estimate_tokens`.
- Replace `.config.llm_models` imports with `.config`.
- Add `generate()` returning `LLMResult`.
- Keep `generate_response()` returning the current tuple shape through `LLMResult.to_legacy_tuple()`.
- Remove `save_token_usage_report()` from `LLMClient`.
- Preserve async context manager and `close()` behavior.
- Re-raise `asyncio.CancelledError`.

- [ ] **Step 6: Run tests to verify they pass**

Run: `uv run pytest ../llm-exec-core/tests/unit/test_client.py -v`

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git -C ../llm-exec-core add src/llm_exec_core/client.py src/llm_exec_core/__init__.py tests/unit/test_client.py
git -C ../llm-exec-core commit -m "feat: extract async llm client"
```

### Task 6: Wire Editor Assistant to External Package

**Files:**
- Modify: `pyproject.toml`
- Modify: `src/editor_assistant/llm_client.py`
- Modify: `src/editor_assistant/config/llm_models.py`
- Modify: `src/editor_assistant/config/constants.py`
- Modify: `src/editor_assistant/utils.py`
- Modify: `src/editor_assistant/md_processor.py`
- Modify: `src/editor_assistant/cli.py`

**Interfaces:**
- Consumes: `llm_exec_core.LLMClient`
- Consumes: `llm_exec_core.usage.format_usage_report`
- Produces: old import paths that still work
- Produces: CLI version `0.6.0`

- [ ] **Step 1: Write failing editor-assistant dependency tests**

Add tests to `tests/unit/test_regression_refactor.py`:

```python
def test_new_llm_core_import_path_available():
    from llm_exec_core import LLMClient

    assert hasattr(LLMClient, "generate_response")


def test_legacy_llm_client_import_path_still_available():
    from editor_assistant.llm_client import LLMClient

    assert hasattr(LLMClient, "generate_response")


def test_legacy_llm_models_import_path_still_available():
    from editor_assistant.config.llm_models import get_supported_models

    assert isinstance(get_supported_models(), list)


def test_legacy_llm_constants_still_exported_from_app_constants():
    from editor_assistant.config.constants import MAX_API_RETRIES

    assert isinstance(MAX_API_RETRIES, int)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/unit/test_regression_refactor.py -v`

Expected: FAIL because `llm_exec_core` is not installed in `editor-assistant`.

- [ ] **Step 3: Add dependency pin**

For local development, use a path dependency until the first package release is published:

```toml
dependencies = [
    "llm-exec-core @ file:///Users/mogu/Projects/tools/llm-exec-core",
    "markitdown[all]",
    "requests",
    "httpx>=0.25.0",
    "pydantic",
    "trafilatura",
    "readabilipy",
    "html2text",
    "pyyaml",
    "jinja2",
    "rich>=13.0.0",
]
```

For published use, replace the path dependency with:

```toml
dependencies = [
    "llm-exec-core==0.1.0",
    "markitdown[all]",
    "requests",
    "httpx>=0.25.0",
    "pydantic",
    "trafilatura",
    "readabilipy",
    "html2text",
    "pyyaml",
    "jinja2",
    "rich>=13.0.0",
]
```

- [ ] **Step 4: Add compatibility shims**

`src/editor_assistant/llm_client.py` should alias the core module so legacy monkeypatches affect the actual implementation:

```python
"""Compatibility shim for the extracted LLM client."""

import sys

import llm_exec_core.client as _client

sys.modules[__name__] = _client
```

`src/editor_assistant/config/llm_models.py` should preserve the old two-item `get_model_details()` return shape:

```python
"""Compatibility shim for extracted LLM model configuration."""

from typing import Any
from pathlib import Path

from llm_exec_core.config import (
    ModelDetails,
    Pricing,
    ProviderSettings,
    RateLimitSettings,
    get_provider_settings,
    get_supported_models,
    load_all_settings,
)
from llm_exec_core.config import get_model_details as _core_get_model_details


def get_model_details(
    model_name: str,
    config_source: Path | dict[str, Any] | None = None,
) -> tuple[ProviderSettings, ModelDetails]:
    _, provider_settings, model_details = _core_get_model_details(
        model_name, config_source
    )
    return provider_settings, model_details
```

`src/editor_assistant/config/constants.py` should import and re-export LLM constants while keeping app constants local:

```python
from llm_exec_core.constants import (
    API_REQUEST_TIMEOUT_SECONDS,
    CHAR_TOKEN_RATIO,
    CHAR_TOKEN_RATIO_EN,
    CHAR_TOKEN_RATIO_ZH,
    INITIAL_RETRY_DELAY_SECONDS,
    MAX_API_RETRIES,
    MAX_REQUESTS_PER_MINUTE,
    MIN_REQUEST_INTERVAL_SECONDS,
    RATE_LIMIT_WARNINGS_ENABLED,
    RESPONSE_CACHE_ENABLED,
    RESPONSE_CACHE_MAX_SIZE,
    RESPONSE_CACHE_TTL_SECONDS,
)
```

`src/editor_assistant/utils.py` should preserve the legacy helper:

```python
"""Utility functions for Editor Assistant."""

from llm_exec_core.tokens import estimate_tokens

__all__ = ["estimate_tokens"]
```

- [ ] **Step 5: Move app token report persistence to MDProcessor**

Replace `self.llm_client.save_token_usage_report(title, output_dir)` with app-owned file writing:

```python
from llm_exec_core.usage import format_usage_report


def _save_token_usage_report(self, project_name: str, output_dir: Path) -> None:
    report = format_usage_report(
        project_name=project_name,
        model=self.llm_client.model,
        model_name=self.llm_client.model_name,
        pricing_currency=self.llm_client.pricing_currency,
        token_usage=self.llm_client.get_token_usage(),
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / f"token_usage_{project_name}.txt"
    report_path.write_text(report, encoding="utf-8")
```

- [ ] **Step 6: Bump editor-assistant version**

Set these values to `0.6.0`:

- `pyproject.toml` project version.
- `src/editor_assistant/config/__init__.py` `__version__`.
- `src/editor_assistant/cli.py` `--version` string.
- English and Chinese README version badges.

- [ ] **Step 7: Run tests to verify they pass**

Run: `uv run pytest tests/unit/ -v`

Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add pyproject.toml src/editor_assistant tests/unit tests/stress README.md CHANGELOG.md DEVELOPER_GUIDE.md
git commit -m "refactor: consume extracted llm execution package"
```

### Task 7: Add Downstream Readiness Documentation

**Files:**
- Create: `docs/design_docs/issue_24_llm_exec_core_contract.md`
- Modify: `README.md`
- Modify: `DEVELOPER_GUIDE.md`
- Modify: `CHANGELOG.md`

**Interfaces:**
- Produces: documented package name.
- Produces: documented publish/reference strategy.
- Produces: documented version pin strategy.
- Produces: documented worker skeleton import/API contract.
- Produces: documented usage/result structure.
- Produces: documented structured output hook example.
- Produces: documented cancellation and execution metadata boundary.

- [ ] **Step 1: Write contract doc**

`docs/design_docs/issue_24_llm_exec_core_contract.md` should include:

````markdown
# LLM Exec Core Downstream Contract

## Package

- Distribution: `llm-exec-core`
- Import package: `llm_exec_core`
- Initial package version: `0.1.0`
- First editor-assistant consumer version: `0.6.0`

## Reference Strategy

During local migration, `editor-assistant` references the sibling package with a `file://` dependency.

For release consumption, applications pin `llm-exec-core==0.1.0`.

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

## Out of Scope

LinkResearcher task lifecycle, attempt schema, artifact schema, result schema, and apply semantics are not part of `llm-exec-core`.
````

- [ ] **Step 2: Update README and DEVELOPER_GUIDE**

Add a short section explaining that Editor Assistant uses `llm-exec-core` for LLM execution while the app owns document workflows and tasks.

- [ ] **Step 3: Update CHANGELOG**

Add an `Unreleased` entry:

```markdown
### Changed
- Extracted LLM execution infrastructure into `llm-exec-core` and updated Editor Assistant to consume it as an external package.

### Added
- Documented downstream package contract for LinkResearcher and other workers.
```

- [ ] **Step 4: Commit**

```bash
git add docs/design_docs/issue_24_llm_exec_core_contract.md README.md DEVELOPER_GUIDE.md CHANGELOG.md
git commit -m "docs: document llm core downstream contract"
```

### Task 8: Verification and Release Readiness

**Files:**
- Modify only files required by failed verification commands.

**Interfaces:**
- Produces: passing unit tests in both packages.
- Produces: passing lint/type checks for touched code.
- Produces: clean working trees.

- [ ] **Step 1: Verify external package**

Run:

```bash
cd ../llm-exec-core
uv sync
uv run pytest tests/unit/
uv run flake8 src/
uv run mypy src/
uv run black src/ tests/ --check
```

Expected: all commands pass.

- [ ] **Step 2: Verify editor-assistant**

Run:

```bash
cd /Users/mogu/Projects/tools/editor-assistant
uv sync
uv run pytest tests/unit/
uv run flake8 src/
uv run mypy src/
uv run black src/ tests/ --check
```

Expected: all commands pass.

- [ ] **Step 3: Verify old import paths**

Run:

```bash
uv run python -c "from editor_assistant.llm_client import LLMClient; print(LLMClient.__name__)"
uv run python -c "from editor_assistant.config.llm_models import get_supported_models; print(len(get_supported_models()))"
uv run python -c "from editor_assistant.config.constants import MAX_API_RETRIES; print(MAX_API_RETRIES)"
```

Expected:

```text
LLMClient
<positive integer>
3
```

- [ ] **Step 4: Verify new import path**

Run:

```bash
uv run python -c "from llm_exec_core import LLMClient; print(LLMClient.__name__)"
```

Expected:

```text
LLMClient
```

- [ ] **Step 5: Verify working tree state**

Run:

```bash
git -C ../llm-exec-core status --short
git status --short
```

Expected: both outputs are empty.

## Discussion Decisions Before Execution

1. Confirm package name: recommended `llm-exec-core` distribution and `llm_exec_core` import package.
2. Confirm repository location: recommended sibling repo `/Users/mogu/Projects/tools/llm-exec-core`.
3. Confirm whether the first Editor Assistant migration uses a local `file://` dependency before publishing.
4. Confirm whether legacy `editor_assistant.config.llm_models.get_model_details()` must preserve the two-item tuple for one release cycle.
5. Confirm whether `generate()` plus compatibility `generate_response()` is the right public API shape.
6. Confirm whether LinkResearcher needs only documented examples in this issue, with worker lifecycle implementation staying in its own issue.

## Self-Review

- Spec coverage: The plan covers external package creation, LLM constants, stdlib logging, injectable config, token estimation, pure usage formatting, editor-assistant migration, backward compatibility, version bump, changelog, and LinkResearcher downstream readiness.
- Scope check: The plan excludes task schemas, prompt semantics, SQLite schema changes, document conversion, and LinkResearcher durable workflow state from `llm_exec_core`.
- Placeholder scan: The plan contains concrete recommended decisions, file paths, signatures, commands, and expected results.
- Type consistency: `LLMClient.generate()` returns `LLMResult`; `generate_response()` returns the legacy tuple; `TokenUsage.to_legacy_dict()` and `LLMResult.to_legacy_tuple()` bridge the old usage shape.
