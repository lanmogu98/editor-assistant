# LLM 外部包抽离实施计划

> **给 agentic workers:** REQUIRED SUB-SKILL: 实施本计划时必须使用 `superpowers:subagent-driven-development`（推荐）或 `superpowers:executing-plans`，按任务逐项执行。任务步骤使用 checkbox（`- [ ]`）语法跟踪。

**目标:** 将 Editor Assistant 当前的 LLM 基础设施抽离成一个外部 Python package，供 `editor-assistant` 和 LinkResearcher worker 共同调用。

**架构:** 新建一个 OpenAI-compatible LLM execution package，负责 provider 配置、模型目录、重试、限速、响应缓存、token 估算、usage/result metadata、structured output hook 和取消边界。`editor-assistant` 回到应用层，只保留文档转换、任务规则、prompt、SQLite 持久化、CLI、输出文件路径和用户可见日志。LinkResearcher 只消费同一个 LLM execution package；durable task lifecycle、attempt/artifact/result schema 和 apply semantics 仍由 LinkResearcher 自己的 worker 负责。

**技术栈:** Python 3.10+、`uv`、`httpx`、`pydantic`、`pyyaml`、stdlib `logging`、`pytest`、`pytest-asyncio`、`black`、`flake8`、`mypy`。

## 全局约束

- 外部 package 的 distribution name 使用 `llm-exec-core`。
- 外部 package 的 import package 使用 `llm_exec_core`。
- `editor-assistant` 目标版本升级到 `0.6.0`。
- `editor_assistant.llm_client` 保留一个 release cycle 的兼容 shim。
- `editor_assistant.config.llm_models` 保留一个 release cycle 的兼容 shim。
- `editor_assistant.config.constants` 中的 LLM 相关常量保留一个 release cycle 的旧路径导出。
- 不把 task 定义、prompt 模板、文档转换、SQLite storage、CLI 命令或 app logging 放入 `llm_exec_core`。
- core package 只使用 stdlib `logging`，不得 import `editor_assistant.config.logging_config`。
- core package 不负责把 token usage report 写到磁盘；格式化函数只返回字符串，持久化由调用方处理。
- model catalog 的新 SSOT 是 `llm_exec_core/llm_config.yml`；`editor-assistant` 删除自己的 `config/llm_config.yml`，旧 `config.llm_models` shim 默认委托 core catalog。
- 如需 app-specific model catalog，调用方必须显式传 `config_source`，不得维护隐式双副本。
- 本地协同开发不得 commit 绝对 local file URL dependency；使用相对 `[tool.uv.sources]` 或 uv workspace。发布前切换到 registry/Git pin。
- core streaming 在 `stream_callback is None` 时不得写 stdout；CLI/app 如需展示流式输出，必须显式传 callback。
- core cache 默认关闭；rate limiter/cache 均为 in-process/per-client 能力，不声明为 distributed worker 级限流或持久缓存。
- unit tests 必须 mock API 调用，不允许真实 API 请求。
- LinkResearcher 的 durable task lifecycle、task/attempt/artifact/result schema 和 apply semantics 不进入这个 package。
- 本文档是讨论用计划；未经 owner 批准前，不开始实施代码。

---

## Scope 解释

GitHub issue #24 原文更偏向 in-repo lift-ready refactor，但 owner 已澄清真实目标是外部 package：LLM 基础设施要能作为独立依赖被 `editor-assistant` 和 LinkResearcher 调用。

因此，最终状态不能停在 `src/editor_assistant/llm/` 子包。这个形态最多作为短暂的抽离技巧，不是完成态。完成态是：

- `llm_exec_core` 是一个独立 Python package。
- `editor-assistant` 从 `llm_exec_core` import LLM execution 能力。
- 旧的 `editor_assistant` import 路径在一个 release cycle 内继续可用。
- LinkResearcher 有明确的最小 import/API contract 文档。
- package 引用方式和 version pin 策略已写清楚。

## 方案选项

### 方案 A: 只做 In-Repo Lift-Ready

把 `llm_client.py`、`llm_models.py`、`llm_config.yml`、LLM constants 和 token helper 移到 `src/editor_assistant/llm/`，外部包创建另开 issue。

取舍：短期改动最小，但不满足 owner 澄清后的目标。LinkResearcher 仍然没有可依赖的 package，只能继续 copy-paste 或等待后续工作。

### 方案 B: 直接抽外部包

创建 `llm-exec-core` 作为 canonical package，把核心逻辑迁入其中，再让 `editor-assistant` 通过 pinned dependency 和兼容 shim 消费它。

取舍：第一轮 PR 更大，也需要现在就确认 package/version/API 决策；但它直接抵达目标形态，并迫使我们在迁移前把公共 API 设计清楚。

### 方案 C: 临时 Monorepo Package

在 `editor-assistant` 内部创建 `packages/llm_exec_core/`，通过 path dependency 消费，测试通过后再拆成独立 repo。

取舍：本地编辑更容易，但如果不严格禁止 `llm_exec_core` import `editor_assistant`，容易让 repo 布局掩盖真实包边界。

**推荐:** 终态采用方案 B，但实施期显式安排一个可移植 workspace/path-dep 协同开发阶段。这个阶段仍使用真实 `llm_exec_core` import 边界，并禁止 core import `editor_assistant`；等 `editor-assistant` 和 LinkResearcher 都跑过 API 后，再发布 `llm-exec-core` 并切换到 pinned dependency。

## 目标文件结构

### 外部包: `../llm-exec-core`

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

职责划分：

- `client.py`: async HTTP execution、retry、rate limiting、response cache、streaming、token usage tracking。
- `config.py`: Pydantic provider/model schema 和可注入 catalog loading。
- `constants.py`: 只放 LLM execution 常量。
- `tokens.py`: `estimate_tokens`。
- `usage.py`: 纯 usage report formatting。
- `types.py`: result、usage、execution metadata、structured output hook 类型。
- `llm_config.yml`: 新的默认 model catalog SSOT。

### Editor Assistant 仓库

- Modify: `pyproject.toml`
- Modify: `README.md`
- Modify: `CHANGELOG.md`
- Modify: `DEVELOPER_GUIDE.md`
- Modify: `src/editor_assistant/__init__.py`
- Modify: `src/editor_assistant/config/__init__.py`
- Modify: `src/editor_assistant/config/constants.py`
- Modify: `src/editor_assistant/config/llm_models.py`
- Delete: `src/editor_assistant/config/llm_config.yml`
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

职责划分：

- app code 继续负责 tasks、document conversion、SQLite、CLI、output file paths、progress formatting 和 app logging。
- compatibility shims 保证旧 import 路径继续工作。
- tests 同时验证新依赖路径和旧兼容路径。

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

`generate()` 是新的结构化 API。`generate_response()` 是兼容 API，保持当前返回 `(text, usage_dict)` 的形状。

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

    def to_legacy_dict(self, duration_seconds: float = 0.0) -> dict[str, Any]:
        return {
            "total_input_tokens": self.input_tokens,
            "total_output_tokens": self.output_tokens,
            "cost": {
                "input_cost": self.input_cost,
                "output_cost": self.output_cost,
                "total_cost": self.total_cost,
            },
            "process_times": {"total_time": duration_seconds},
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
        usage = self.usage.to_legacy_dict(
            duration_seconds=self.metadata.duration_seconds
        )
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

新 package 的 `get_model_details()` 返回三项：provider name、provider settings、model details。旧路径 `editor_assistant.config.llm_models.get_model_details()` 在一个兼容周期内保留当前两项返回形状，除非 owner 明确批准 breaking change。

默认 `config_source=None` 使用 module-level cache，避免每次查询重读 YAML。显式传入 `Path` 或 `dict` 时按该 source 构建 catalog，不得被默认 cache 污染。

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

hook 接收最终文本，并返回调用方拥有的结构化数据。core package 不定义 LinkResearcher schema。

### Cancellation Contract

`LLMClient.generate()` 和 `LLMClient.generate_response()` 不吞掉 `asyncio.CancelledError`。它们可以让 context manager 关闭 HTTP 资源，然后重新抛出 cancellation。run、attempt、artifact 的状态由调用方系统决定。

## 实施任务

### Task 1: 创建外部包骨架

**Files:**
- Create: `../llm-exec-core/pyproject.toml`
- Create: `../llm-exec-core/src/llm_exec_core/__init__.py`
- Create: `../llm-exec-core/tests/unit/test_types.py`

**Interfaces:**
- Produces: importable package `llm_exec_core`
- Produces: version `0.1.0`

- [ ] **Step 1: 写失败的 import/version 测试**

```python
def test_package_imports_with_version():
    import llm_exec_core

    assert llm_exec_core.__version__ == "0.1.0"
```

- [ ] **Step 2: 运行测试，确认按预期失败**

Run: `uv run pytest ../llm-exec-core/tests/unit/test_types.py::test_package_imports_with_version -v`

Expected: FAIL with `ModuleNotFoundError: No module named 'llm_exec_core'`.

- [ ] **Step 3: 添加 package metadata 和 version export**

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

- [ ] **Step 4: 运行测试，确认通过**

Run: `uv run pytest ../llm-exec-core/tests/unit/test_types.py::test_package_imports_with_version -v`

Expected: PASS.

- [ ] **Step 5: 提交**

```bash
git -C ../llm-exec-core add pyproject.toml src tests
git -C ../llm-exec-core commit -m "chore: scaffold llm execution core"
```

### Task 2: 移动 LLM 常量和 Token Estimation

**Files:**
- Create: `../llm-exec-core/src/llm_exec_core/constants.py`
- Create: `../llm-exec-core/src/llm_exec_core/tokens.py`
- Create: `../llm-exec-core/tests/unit/test_tokens.py`

**Interfaces:**
- Produces: `estimate_tokens(text: str) -> int`
- Produces: `client.py` 使用的 LLM constants

- [ ] **Step 1: 写失败的 token estimation 测试**

```python
from llm_exec_core.tokens import estimate_tokens


def test_estimate_tokens_empty_text_is_zero():
    assert estimate_tokens("") == 0


def test_estimate_tokens_english_uses_default_ratio():
    assert estimate_tokens("a" * 35) == 10


def test_estimate_tokens_chinese_heavy_text_uses_cjk_ratio():
    assert estimate_tokens("科学" * 20) > estimate_tokens("science" * 5)
```

- [ ] **Step 2: 运行测试，确认按预期失败**

Run: `uv run pytest ../llm-exec-core/tests/unit/test_tokens.py -v`

Expected: FAIL with `ModuleNotFoundError` for `llm_exec_core.tokens`.

- [ ] **Step 3: 添加 constants 和 token estimator**

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

- [ ] **Step 4: 运行测试，确认通过**

Run: `uv run pytest ../llm-exec-core/tests/unit/test_tokens.py -v`

Expected: PASS.

- [ ] **Step 5: 提交**

```bash
git -C ../llm-exec-core add src/llm_exec_core/constants.py src/llm_exec_core/tokens.py tests/unit/test_tokens.py
git -C ../llm-exec-core commit -m "feat: add llm constants and token estimation"
```

### Task 3: 实现可注入 Model Catalog

**Files:**
- Create: `../llm-exec-core/src/llm_exec_core/config.py`
- Create: `../llm-exec-core/src/llm_exec_core/llm_config.yml`
- Create: `../llm-exec-core/tests/unit/test_config.py`

**Interfaces:**
- Produces: `load_all_settings(config_source: Path | dict[str, Any] | None = None) -> dict[str, ProviderSettings]`
- Produces: `get_model_details(model_name: str, config_source: Path | dict[str, Any] | None = None) -> tuple[str, ProviderSettings, ModelDetails]`
- Produces: `get_supported_models(config_source: Path | dict[str, Any] | None = None) -> list[str]`

- [ ] **Step 1: 写失败的 config injection 测试**

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


def test_explicit_config_source_is_not_polluted_by_default_cache():
    first = get_supported_models(CUSTOM_CONFIG)
    second = get_supported_models(
        {
            "other-provider": {
                "api_key_env_var": "OTHER_API_KEY",
                "api_base_url": "https://example.invalid/chat/completions",
                "temperature": 0.1,
                "max_tokens": 128,
                "context_window": 4096,
                "pricing_currency": "$",
                "models": {
                    "other-model": {
                        "id": "other-model-id",
                        "pricing": {"input": 1.0, "output": 2.0},
                    }
                },
            }
        }
    )

    assert first == ["test-model"]
    assert second == ["other-model"]
```

- [ ] **Step 2: 运行测试，确认按预期失败**

Run: `uv run pytest ../llm-exec-core/tests/unit/test_config.py -v`

Expected: FAIL with `ModuleNotFoundError` for `llm_exec_core.config`.

- [ ] **Step 3: 实现 config loader**

实现时保留 `src/editor_assistant/config/llm_models.py` 当前的 Pydantic schemas，并新增 dict/path injection。`config_source=None` 时默认加载并缓存 `Path(__file__).parent / "llm_config.yml"`；显式传 `Path` 或 `dict` 时用传入 source 构建 catalog，不复用默认 cache。

- [ ] **Step 4: 复制默认 model catalog，确立 core SSOT**

Copy `src/editor_assistant/config/llm_config.yml` to `../llm-exec-core/src/llm_exec_core/llm_config.yml`.

抽离完成后，`../llm-exec-core/src/llm_exec_core/llm_config.yml` 是默认 catalog 的唯一 SSOT。后续 Task 6 删除 `src/editor_assistant/config/llm_config.yml`，避免两份 YAML 副本漂移。

- [ ] **Step 5: 运行测试，确认通过**

Run: `uv run pytest ../llm-exec-core/tests/unit/test_config.py -v`

Expected: PASS.

- [ ] **Step 6: 提交**

```bash
git -C ../llm-exec-core add src/llm_exec_core/config.py src/llm_exec_core/llm_config.yml tests/unit/test_config.py
git -C ../llm-exec-core commit -m "feat: add injectable llm model catalog"
```

### Task 4: 添加 Result、Usage、Metadata 和 Report Formatting

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
- Produces: `format_usage_report(project_name: str, model: str, model_name: str, pricing_currency: str, token_usage: dict[str, Any], timestamp: str | None = None) -> str`

- [ ] **Step 1: 写失败的 usage/report 测试**

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

- [ ] **Step 2: 写失败的 result compatibility 测试**

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
    assert usage["process_times"]["total_time"] == 1.0
    assert usage["metadata"]["request_id"] == "req-1"
```

- [ ] **Step 3: 运行测试，确认按预期失败**

Run: `uv run pytest ../llm-exec-core/tests/unit/test_usage.py ../llm-exec-core/tests/unit/test_types.py -v`

Expected: FAIL with missing `llm_exec_core.usage` and missing dataclasses.

- [ ] **Step 4: 实现 dataclasses 和 report formatting**

`format_usage_report()` 必须复用当前 `LLMClient.save_token_usage_report()` 的报告文本形状，并且不得调用 `open()`、`Path.mkdir()` 或 app progress functions。

- [ ] **Step 5: 运行测试，确认通过**

Run: `uv run pytest ../llm-exec-core/tests/unit/test_usage.py ../llm-exec-core/tests/unit/test_types.py -v`

Expected: PASS.

- [ ] **Step 6: 提交**

```bash
git -C ../llm-exec-core add src/llm_exec_core/types.py src/llm_exec_core/usage.py src/llm_exec_core/__init__.py tests/unit/test_usage.py tests/unit/test_types.py
git -C ../llm-exec-core commit -m "feat: add llm result metadata and usage formatting"
```

### Task 5A: 行为保持地抽离 Async LLM Client

**Files:**
- Create: `../llm-exec-core/src/llm_exec_core/client.py`
- Modify: `../llm-exec-core/src/llm_exec_core/__init__.py`
- Create: `../llm-exec-core/tests/unit/test_client_legacy.py`

**Interfaces:**
- Produces: `LLMClient.generate_response(...) -> tuple[str, dict[str, Any]]`
- Consumes: config loader、constants、token estimator、usage formatting

- [ ] **Step 1: 写失败的 non-streaming compatibility 测试**

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
    assert usage["process_times"]["total_time"] >= 0
```

- [ ] **Step 2: 运行测试，确认按预期失败**

Run: `uv run pytest ../llm-exec-core/tests/unit/test_client_legacy.py -v`

Expected: FAIL with missing `llm_exec_core.client`.

- [ ] **Step 3: 行为保持地移动 client 实现**

把 `src/editor_assistant/llm_client.py` 的现有行为迁到 `../llm-exec-core/src/llm_exec_core/client.py`，本任务只允许这些变化：

- 将 `.config.logging_config.warning` 和 `.config.logging_config.progress` 替换为 `logging.getLogger(__name__)` 的 `logger.warning()` 和 `logger.info()`。
- 将 `.config.constants` imports 替换为 `.constants`。
- 将 `.utils.estimate_tokens` 替换为 `.tokens.estimate_tokens`。
- 将 `.config.llm_models` imports 替换为 `.config`。
- 因 Task 3 的 core `get_model_details()` 已返回 3-tuple，5A 允许把旧解包调整为 `_, provider_settings, model_details = get_model_details(model_name)`，但此阶段不保存或对外暴露 `provider_name`；5B 再接入 metadata。
- 从 `LLMClient` 移除 `save_token_usage_report()`。
- 保留 `generate_response()` 的 legacy tuple shape。
- 保留 async context manager、`close()`、rate limiting、retry、cache 和 streaming 的当前行为。
- 本任务不新增 `generate()`、structured output hook 或 metadata API。

- [ ] **Step 4: 运行测试，确认通过**

Run: `uv run pytest ../llm-exec-core/tests/unit/test_client_legacy.py -v`

Expected: PASS.

- [ ] **Step 5: 提交**

```bash
git -C ../llm-exec-core add src/llm_exec_core/client.py src/llm_exec_core/__init__.py tests/unit/test_client_legacy.py
git -C ../llm-exec-core commit -m "feat: extract legacy llm client behavior"
```

### Task 5B: 添加 Structured Result API 和 Metadata

**Files:**
- Modify: `../llm-exec-core/src/llm_exec_core/client.py`
- Modify: `../llm-exec-core/src/llm_exec_core/types.py`
- Create: `../llm-exec-core/tests/unit/test_client_result.py`

**Interfaces:**
- Produces: `LLMClient.generate(...) -> LLMResult`
- Produces: `LLMClient.generate_response(...) -> tuple[str, dict[str, Any]]` via `LLMResult.to_legacy_tuple()`
- Consumes: `TokenUsage`, `ExecutionMetadata`, `LLMResult`

- [ ] **Step 1: 写失败的 structured result 测试**

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
    assert result.metadata.model_name == "test-model"
    assert result.metadata.model_id == "provider-model-id"
    assert result.metadata.duration_seconds > 0
    assert result.metadata.trace_context == {"source": "unit"}
```

- [ ] **Step 2: 写失败的 legacy timing bridge 测试**

```python
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from llm_exec_core.client import LLMClient


@pytest.mark.asyncio
async def test_generate_response_legacy_tuple_preserves_duration(monkeypatch):
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
        "choices": [{"message": {"content": "ok"}}],
        "usage": {"prompt_tokens": 5, "completion_tokens": 6},
    }
    mock_response.raise_for_status = MagicMock()

    with patch("llm_exec_core.client.httpx.AsyncClient") as mock_cls:
        mock_httpx_client = AsyncMock()
        mock_httpx_client.post.return_value = mock_response
        mock_cls.return_value = mock_httpx_client

        client = LLMClient("test-model", config_source=config)
        _, usage = await client.generate_response("Hello")

    assert usage["process_times"]["total_time"] >= 0
    assert usage["metadata"]["provider_name"] == "test-provider"
```

- [ ] **Step 3: 运行测试，确认按预期失败**

Run: `uv run pytest ../llm-exec-core/tests/unit/test_client_result.py -v`

Expected: FAIL because `LLMClient.generate()` is not implemented.

- [ ] **Step 4: 实现 `generate()` 和 metadata bridge**

实现要求：

- `get_model_details()` 必须使用新 3-tuple，显式保存 `provider_name`。
- `generate()` 返回 `LLMResult`，包含 `text`、`TokenUsage`、`ExecutionMetadata` 和 `structured`。
- `structured_output_hook` 只接收最终 text，返回 caller-owned structured data。
- `generate_response()` 改为调用 `generate()`，再返回 `LLMResult.to_legacy_tuple()`。
- legacy tuple 的 `process_times.total_time` 必须来自 `ExecutionMetadata.duration_seconds`，不能写 0。
- cache hit 也必须走 `LLMResult`，再由 `to_legacy_tuple()` 生成旧 shape；其 `process_times.total_time` 可以接近 0，但不得回退到另一套 ad hoc usage dict。

- [ ] **Step 5: 运行测试，确认通过**

Run: `uv run pytest ../llm-exec-core/tests/unit/test_client_result.py ../llm-exec-core/tests/unit/test_client_legacy.py -v`

Expected: PASS.

- [ ] **Step 6: 提交**

```bash
git -C ../llm-exec-core add src/llm_exec_core/client.py src/llm_exec_core/types.py tests/unit/test_client_result.py
git -C ../llm-exec-core commit -m "feat: add llm result metadata api"
```

### Task 5C: 修正 Core Streaming UX 和 Cancellation Boundary

**Files:**
- Modify: `../llm-exec-core/src/llm_exec_core/client.py`
- Create: `../llm-exec-core/tests/unit/test_client_streaming.py`

**Interfaces:**
- Produces: no stdout output from core streaming unless caller provides a callback that writes.
- Produces: `asyncio.CancelledError` re-raised by `generate()` and `generate_response()`.

- [ ] **Step 1: 写失败的 no-stdout streaming 测试**

```python
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from llm_exec_core.client import LLMClient


@pytest.mark.asyncio
async def test_streaming_without_callback_does_not_print(monkeypatch, capsys):
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
    mock_response.raise_for_status = MagicMock()

    async def mock_lines():
        yield 'data: {"choices": [{"delta": {"content": "A"}}]}'
        yield 'data: {"choices": [{"delta": {"content": "B"}}]}'
        yield "data: [DONE]"

    mock_response.aiter_lines = mock_lines

    @asynccontextmanager
    async def mock_stream(*args, **kwargs):
        yield mock_response

    with patch("llm_exec_core.client.httpx.AsyncClient") as mock_cls:
        mock_httpx_client = AsyncMock()
        mock_httpx_client.stream = mock_stream
        mock_cls.return_value = mock_httpx_client

        client = LLMClient("test-model", config_source=config)
        response, _ = await client.generate_response("Hello", stream=True)

    assert response == "AB"
    assert capsys.readouterr().out == ""
```

- [ ] **Step 2: 写失败的 cancellation 测试**

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

- [ ] **Step 3: 运行测试，确认按预期失败**

Run: `uv run pytest ../llm-exec-core/tests/unit/test_client_streaming.py -v`

Expected: FAIL because streaming still prints to stdout or cancellation is swallowed.

- [ ] **Step 4: 实现 streaming/cancellation 边界**

实现要求：

- `stream_callback is None` 时只累积 response text，不 `print()`。
- `editor-assistant` CLI/app 如需用户可见流式输出，必须在 Task 6 明确传 callback。
- `asyncio.CancelledError` 不进入 retry wrapper，不转成 `RuntimeError`，直接重新抛出。

- [ ] **Step 5: 运行测试，确认通过**

Run: `uv run pytest ../llm-exec-core/tests/unit/test_client_streaming.py ../llm-exec-core/tests/unit/test_client_result.py ../llm-exec-core/tests/unit/test_client_legacy.py -v`

Expected: PASS.

- [ ] **Step 6: 提交**

```bash
git -C ../llm-exec-core add src/llm_exec_core/client.py tests/unit/test_client_streaming.py
git -C ../llm-exec-core commit -m "fix: keep core streaming output caller-controlled"
```

### Task 6: 将 Editor Assistant 接到外部 Package

**Files:**
- Modify: `pyproject.toml`
- Delete: `src/editor_assistant/config/llm_config.yml`
- Modify: `src/editor_assistant/llm_client.py`
- Modify: `src/editor_assistant/config/llm_models.py`
- Modify: `src/editor_assistant/config/constants.py`
- Modify: `src/editor_assistant/utils.py`
- Modify: `src/editor_assistant/md_processor.py`
- Modify: `src/editor_assistant/cli.py`
- Modify: `tests/unit/test_md_processor_async.py`

**Interfaces:**
- Consumes: `llm_exec_core.LLMClient`
- Consumes: `llm_exec_core.usage.format_usage_report`
- Produces: 继续可用的旧 import paths
- Produces: 交互式 CLI streaming 由 app-owned callback 写 stdout，不依赖 core 默认输出
- Produces: CLI version `0.6.0`
- Produces: no app-owned duplicate `llm_config.yml`

- [ ] **Step 1: 写失败的 editor-assistant dependency 测试**

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

- [ ] **Step 2: 运行测试，确认按预期失败**

Run: `uv run pytest tests/unit/test_regression_refactor.py -v`

Expected: FAIL because `llm_exec_core` is not installed in `editor-assistant`.

- [ ] **Step 3: 添加可移植 dependency 配置**

本地迁移阶段使用普通 dependency 名称加相对 `[tool.uv.sources]`，不得 commit 机器特定的绝对 local file URL 路径：

```toml
dependencies = [
    "llm-exec-core",
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

[tool.uv.sources]
llm-exec-core = { path = "../llm-exec-core", editable = true }
```

发布消费阶段必须先删除 `[tool.uv.sources]`，再改为 pinned version：

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

如果 CI 在本地协同阶段运行，CI job 必须 checkout `editor-assistant` 和 sibling `llm-exec-core` workspace；否则该阶段不能作为可合并到 `main` 的最终形态。

- [ ] **Step 4: 删除 app catalog 副本并更新 package data**

删除 `src/editor_assistant/config/llm_config.yml`。同时把 `pyproject.toml` 的 package-data 从：

```toml
package-data = { "editor_assistant" = ["config/*.yml", "config/prompts/*.txt"] }
```

改为：

```toml
package-data = { "editor_assistant" = ["config/prompts/*.txt"] }
```

默认 model catalog 只从 `llm_exec_core/llm_config.yml` 加载。若 `editor-assistant` 后续需要 app-specific catalog，必须显式传 `config_source`，不得恢复隐式副本。

- [ ] **Step 5: 添加 compatibility shims**

`src/editor_assistant/llm_client.py` alias core module，让旧路径 monkeypatch 仍能作用到真实实现：

```python
"""Compatibility shim for the extracted LLM client."""

import sys

import llm_exec_core.client as _client

sys.modules[__name__] = _client
```

`src/editor_assistant/config/llm_models.py` 保留旧的 two-item `get_model_details()` 返回形状：

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

`src/editor_assistant/config/constants.py` 从 core package import 并 re-export LLM constants，同时保留 app constants：

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

`src/editor_assistant/utils.py` 保留旧 helper：

```python
"""Utility functions for Editor Assistant."""

from llm_exec_core.tokens import estimate_tokens

__all__ = ["estimate_tokens"]
```

- [ ] **Step 6: 在 app 层恢复 console streaming callback**

Task 5C 会移除 core 在 `stream_callback is None` 时的默认 stdout 输出。Task 6 必须在同一个 app migration commit 中补回 `MDProcessor` 的交互式 CLI 行为，否则 `brief` / `outline` / `translate` 的主路径会 `stream=True` 但静默无输出。

在 `src/editor_assistant/md_processor.py` 当前 `final_callback` 分支中实现：

```python
final_callback = stream_callback
app_prints_stream = self.stream and output_to_console and final_callback is None

if app_prints_stream:

    def print_stream_chunk(content: str) -> None:
        print(content, end="", flush=True)

    final_callback = print_stream_chunk
elif final_callback is None and not output_to_console:

    def suppress_output(_: str) -> None:
        return None

    final_callback = suppress_output

response, usage_stats = await self._make_api_request(...)

if app_prints_stream:
    print(flush=True)
```

Callback ownership rule:

- 外部 caller 传入 `stream_callback` 时，app 不额外 print。
- `output_to_console=True` 且无外部 callback 时，由 app callback 写 stdout。
- `output_to_console=False` 且无外部 callback 时，继续传 suppressor，避免后台 worker 或测试污染 stdout。

在 `tests/unit/test_md_processor_async.py` 添加 app 层回归测试，使用 fake LLM client 在收到 callback 时发送 chunks，并用 `capsys` 验证 console 模式下 stdout 非空：

```python
@pytest.mark.asyncio
async def test_streaming_console_output_uses_app_callback(
    mock_llm_client_async,
    mock_run_repository,
    capsys,
):
    from editor_assistant.data_models import InputType, MDArticle
    from editor_assistant.md_processor import MDProcessor

    async def fake_generate_response(*args, stream_callback=None, **kwargs):
        stream_callback("hello")
        stream_callback(" world")
        return "hello world", {
            "total_input_tokens": 1,
            "total_output_tokens": 2,
            "cost": {"input_cost": 0, "output_cost": 0, "total_cost": 0},
            "process_times": {"total_time": 0.1},
        }

    mock_llm_client_async.generate_response.side_effect = fake_generate_response

    with patch("editor_assistant.md_processor.TaskRegistry") as mock_registry:
        mock_task = MagicMock()
        mock_task.validate.return_value = (True, "")
        mock_task.build_prompt.return_value = "Test Prompt " * 100
        mock_task.post_process.return_value = {"main": "Processed Content"}
        mock_task.get_output_suffix.return_value = "_test"
        mock_task.supports_multi_input = False
        mock_registry.get.return_value.return_value = mock_task

        processor = MDProcessor("test-model", stream=True)
        article = MDArticle(
            type=InputType.PAPER,
            content="content " * 500,
            title="title",
            source_path="test.pdf",
        )

        success, _ = await processor.process_mds(
            [article],
            "test-task",
            save_files=False,
            output_to_console=True,
        )

    assert success is True
    assert "hello world" in capsys.readouterr().out
```

该测试可以按现有 `test_md_processor_async.py` fixture 做最小改写，但断言必须证明 console streaming 不再依赖 core 默认 `print()`。

- [ ] **Step 7: 将 app token report 持久化移到 MDProcessor**

把 `self.llm_client.save_token_usage_report(title, output_dir)` 替换为 app-owned file writing：

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

- [ ] **Step 8: bump editor-assistant version**

把这些值设为 `0.6.0`：

- `pyproject.toml` project version。
- `src/editor_assistant/config/__init__.py` `__version__`。
- `src/editor_assistant/cli.py` `--version` string。
- README 的 English 和 Chinese version badges。

- [ ] **Step 9: 运行测试，确认通过**

Run:

```bash
uv run pytest tests/unit/test_md_processor_async.py -v
uv run pytest tests/unit/ -v
```

Expected: PASS.

- [ ] **Step 10: 提交**

```bash
git add pyproject.toml src/editor_assistant tests/unit tests/stress README.md CHANGELOG.md DEVELOPER_GUIDE.md
git commit -m "refactor: consume extracted llm execution package"
```

### Task 7: 添加 Downstream Readiness 文档

**Files:**
- Create: `docs/design_docs/issue_24_llm_exec_core_contract.md`
- Modify: `README.md`
- Modify: `DEVELOPER_GUIDE.md`
- Modify: `CHANGELOG.md`

**Interfaces:**
- Produces: package name 文档。
- Produces: publish/reference strategy 文档。
- Produces: version pin strategy 文档。
- Produces: worker skeleton 最小 import/API contract。
- Produces: usage/result structure 文档。
- Produces: structured output hook 示例。
- Produces: cancellation 和 execution metadata boundary 文档。

- [ ] **Step 1: 写 contract doc**

`docs/design_docs/issue_24_llm_exec_core_contract.md` should include:

````markdown
# LLM Exec Core Downstream Contract

## Package

- Distribution: `llm-exec-core`
- Import package: `llm_exec_core`
- Initial package version: `0.1.0`
- First editor-assistant consumer version: `0.6.0`

## Reference Strategy

During local migration, `editor-assistant` references the sibling package with relative `[tool.uv.sources]` or a uv workspace.

For release consumption, applications pin `llm-exec-core==0.1.0`.

Final committed `editor-assistant` config must not contain absolute local file URL paths. Local development uses relative `[tool.uv.sources]` or a uv workspace; release consumption uses the pinned package.

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

## Protocol Boundary

`llm-exec-core` initially supports OpenAI-compatible `/chat/completions` APIs. Native Anthropic, Bedrock, Vertex, or provider-specific protocols are out of scope until explicitly designed.

## Rate Limit and Cache Boundary

Built-in rate limiting and response cache are in-process/per-client conveniences. They are not distributed worker coordination. LinkResearcher must use its own shared limiter or durable coordination if attempts run across multiple processes or hosts. Response cache is disabled by default and should stay disabled for idempotent worker accounting unless a caller explicitly opts in.

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

- [ ] **Step 2: 更新 README 和 DEVELOPER_GUIDE**

增加短小章节，说明 Editor Assistant 通过 `llm-exec-core` 做 LLM execution，而文档 workflow 和 task 仍由 app 层拥有。

- [ ] **Step 3: 更新 CHANGELOG**

Add an `Unreleased` entry:

```markdown
### Changed
- Extracted LLM execution infrastructure into `llm-exec-core` and updated Editor Assistant to consume it as an external package.

### Added
- Documented downstream package contract for LinkResearcher and other workers.
```

- [ ] **Step 4: 提交**

```bash
git add docs/design_docs/issue_24_llm_exec_core_contract.md README.md DEVELOPER_GUIDE.md CHANGELOG.md
git commit -m "docs: document llm core downstream contract"
```

### Task 8: Verification and Release Readiness

**Files:**
- 只修改 failed verification commands 明确需要修改的文件。

**Interfaces:**
- Produces: 两个 package 的 unit tests 通过。
- Produces: touched code 的 lint/type checks 通过。
- Produces: clean working trees。

- [ ] **Step 1: 验证外部 package**

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

- [ ] **Step 2: 验证 editor-assistant**

Run:

```bash
cd <editor-assistant-repo>
uv sync
uv run pytest tests/unit/
uv run pytest tests/stress/test_sqlite_concurrency.py tests/stress/test_error_boundaries.py
uv run flake8 src/
uv run mypy src/
uv run black src/ tests/ --check
```

Expected: all commands pass.

`tests/stress/test_real_load.py` uses real API calls when API keys are present. Run it only as an explicit expensive verification:

```bash
uv run pytest tests/stress/test_real_load.py -v
```

- [ ] **Step 3: 验证旧 import paths**

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

- [ ] **Step 4: 验证新 import path**

Run:

```bash
uv run python -c "from llm_exec_core import LLMClient; print(LLMClient.__name__)"
```

Expected:

```text
LLMClient
```

- [ ] **Step 5: 验证 working tree state**

Run:

```bash
git -C ../llm-exec-core status --short
git status --short
```

Expected: both outputs are empty.

## 执行前讨论决策

1. 确认 package name：推荐 distribution `llm-exec-core`、import package `llm_exec_core`。
2. 确认 repo 位置：推荐 sibling repo `<llm-exec-core-repo>`。
3. 确认 model catalog 新 SSOT 为 `llm_exec_core/llm_config.yml`，并删除 `editor-assistant` 的 YAML 副本。
4. 确认协同开发期使用相对 `[tool.uv.sources]` 或 uv workspace，发布前切 `llm-exec-core==0.1.0` pin。
5. 确认 legacy `editor_assistant.config.llm_models.get_model_details()` 是否保留 two-item tuple 一个 release cycle。
6. 确认是否采用 `generate()` 加兼容 `generate_response()` 的 public API shape。
7. 确认 v0.1 scope 只支持 OpenAI-compatible `/chat/completions`，native Anthropic/Bedrock/Vertex 留到后续设计。
8. 确认 rate limiter/cache 只是 in-process/per-client 能力，LinkResearcher distributed limiting 不进入本 package。
9. 确认本 issue 中 LinkResearcher 只需要 documented examples，worker lifecycle implementation 留在其 own issue。

## 自审

- Spec coverage: 本计划覆盖 external package creation、LLM constants、stdlib logging、injectable config、config SSOT、token estimation、pure usage formatting、editor-assistant migration、backward compatibility、version bump、changelog 和 LinkResearcher downstream readiness。
- Scope check: 本计划明确排除 task schemas、prompt semantics、SQLite schema changes、document conversion 和 LinkResearcher durable workflow state。
- Placeholder scan: 本计划包含具体 recommended decisions、file paths、signatures、commands 和 expected results。
- Type consistency: `LLMClient.generate()` 返回 `LLMResult`；`generate_response()` 返回 legacy tuple；`TokenUsage.to_legacy_dict(duration_seconds=...)` 和 `LLMResult.to_legacy_tuple()` 负责桥接旧 usage shape，并保留 legacy `process_times.total_time`。
- Streaming boundary: core streaming 默认不写 stdout；`MDProcessor` 在 `output_to_console=True` 且无外部 callback 时安装 app-owned print callback，并由 `tests/unit/test_md_processor_async.py` 的 `capsys` 回归测试兜住交互式 CLI 输出。
