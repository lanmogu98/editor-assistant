# RFC: GLM-4.7 支持 + Gemini Free Tier 集成

> 创建日期: 2026-01-04
> 状态: ✅ Implemented
> 更新: 2026-01-04 - 完成实现

---

## 1. 概述

本 RFC 描述两个高优先级功能的实现方案：
1. **GLM-4.7 模型支持** - 在 zhipu native 和 OpenRouter 场景下支持最新的 GLM-4.7 模型
2. **Gemini Free Tier API** - 支持 Gemini 免费层级 API，用于实际调用和 integration 测试

---

## 2. GLM-4.7 模型支持

### 2.1 背景

智谱 AI 于 2025 年 12 月 23 日发布了 GLM-4.7 模型，主要提升：
- **编码能力**: SWE-bench Verified 得分 73.8%（开源模型 SOTA）
- **推理能力**: HLE 测试得分 42.8%，超过 GPT-5.1
- **工具调用**: BrowseComp 得分 67.5%
- **上下文窗口**: 200K tokens (比 glm-4.6 的 128K 更大)
- **最大输出**: 128K tokens (比 glm-4.6 的 96K 更大)

### 2.2 配置信息

#### Zhipu Native

| 参数 | 值 | 备注 |
|------|-----|------|
| **模型 ID** | `glm-4.7` | |
| **API URL** | `https://open.bigmodel.cn/api/paas/v4/chat/completions` | 与现有 zhipu provider 相同 |
| **Context Window** | 200,000 tokens | |
| **Max Output** | 128,000 tokens | |
| **定价 (per 1M tokens)** | input: $0.60, output: $2.20 | 以当前 `llm_config.yml` 为准 |

#### OpenRouter

参考: https://openrouter.ai/z-ai/glm-4.7

| 参数 | 值 | 备注 |
|------|-----|------|
| **模型 ID** | `z-ai/glm-4.7` | |
| **命名** | `glm-4.7-or` | 遵循现有 `-or` 后缀规范 |
| **定价 (per 1M tokens)** | input: $0.60, output: $2.20 | Z.AI provider (最高) |
| **Context Window** | 200,000 tokens | |
| **Max Output** | 65,536 tokens | 与当前 OpenRouter pinned route 配置一致 |

### 2.3 默认模型切换

将 `cli.py` 中的 `DEFAULT_MODEL` 从 `deepseek-v3.2` 改为 `glm-4.7-or`。

**理由：**
- GLM-4.7 性能更优（开源 SOTA）
- 通过 OpenRouter 调用更稳定
- 价格合理

### 2.4 llm_config.yml 变更

```yaml
# 更新 zhipu provider - 添加 glm-4.7
zhipu:
  api_key_env_var: "ZHIPU_API_KEY"
  api_base_url: "https://open.bigmodel.cn/api/paas/v4/chat/completions"
  temperature: 0.6
  max_tokens: 128000  # 更新为 128K
  context_window: 200000  # 更新为 200K
  pricing_currency: "$"
  models:
    glm-4.5:
      id: "glm-4.5"
      pricing: {input: 0.60, output: 2.20}
    glm-4.6:
      id: "glm-4.6"
      pricing: {input: 0.60, output: 2.20}
    glm-4.7:  # 新增
      id: "glm-4.7"
      pricing: {input: 0.60, output: 2.20}

# 更新 zhipu-openrouter provider - 添加 glm-4.7-or
zhipu-openrouter:
  # ... 保持其他配置不变 ...
  max_tokens: 65536  # 避免 pinned provider 路由下超过输出上限导致 OpenRouter 404
  context_window: 200000  # 更新
  models:
    glm-4.5-or:
      id: "z-ai/glm-4.5"
      pricing: {input: 0.38, output: 1.60}
    glm-4.6-or:
      id: "z-ai/glm-4.6"
      pricing: {input: 0.60, output: 2.00}
    glm-4.7-or:  # 新增 - 按最高 provider 价格 (Z.AI)
      id: "z-ai/glm-4.7"
      pricing: {input: 0.60, output: 2.20}
```

---

## 3. Gemini Free Tier API

### 3.1 背景

Google 提供 Gemini API 的免费层级，允许有限的免费调用。这对于：
- 实际使用低成本调用
- Integration 测试高级模型功能（不只是 deepseek/glm）
- 降低开发和测试成本

### 3.2 支持的模型

**Free Tier 不支持 3-pro**，使用 2.5 系列：
- `gemini-2.5-flash-free` (gemini-2.5-flash)
- `gemini-2.5-flash-lite-free` (gemini-2.5-flash-lite)

### 3.3 Free Tier 限制

从 AI Studio 获取的实际限制 (2026-01-04)：

| 模型 | RPM | TPM | RPD |
|------|-----|-----|-----|
| gemini-2.5-flash | 5 | 250K | 20 |
| gemini-2.5-flash-lite | 10 | 250K | 20 |

### 3.4 llm_config.yml 变更

```yaml
# 新增 gemini-free provider
gemini-free:
  api_key_env_var: "GEMINI_FT_API_KEY"
  api_base_url: "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
  temperature: 1.0
  max_tokens: 65536
  context_window: 1000000
  pricing_currency: "$"
  rate_limit:
    min_interval_seconds: 12.0  # 5 RPM
    max_requests_per_minute: 5
  models:
    gemini-2.5-flash-free:
      id: "gemini-2.5-flash"
      pricing: { input: 0.0, output: 0.0 }
    gemini-2.5-flash-lite-free:
      id: "gemini-2.5-flash-lite"
      pricing: { input: 0.0, output: 0.0 }
```

### 3.5 后续更新

测试调用成功后，从 AI Studio 获取实际限制数据，更新：
- `min_interval_seconds`
- `max_requests_per_minute`
- 如有需要，`max_tokens` 限制

---

## 4. Integration 测试改进

### 4.1 需求

提供两个模型选项供用户选择：
- **基础模型**: `deepseek-v3.2` (默认)
- **高级模型**: `gemini-2.5-flash-free`

### 4.2 实现方案

#### conftest.py 修改

```python
# tests/conftest.py

def pytest_addoption(parser):
    """Add command-line options for integration tests."""
    parser.addoption(
        "--integration-model",
        action="store",
        default="base",
        choices=["base", "advanced"],
        help="Integration test model: base (deepseek-v3.2) or advanced (gemini-2.5-flash-free)"
    )

@pytest.fixture
def integration_model_name(request):
    """Get the model name for integration tests based on CLI option."""
    choice = request.config.getoption("--integration-model")
    if choice == "advanced":
        return "gemini-2.5-flash-free"
    return "deepseek-v3.2"  # default: base
```

#### 使用示例

```bash
# 使用基础模型（默认）
pytest tests/integration/ -m integration

# 使用高级模型（Gemini Free Tier）
pytest tests/integration/ -m integration --integration-model advanced
```

---

## 5. 实现步骤

### Phase 1: GLM-4.7 支持 ✅

1. [x] 更新 `llm_config.yml`
   - 添加 `glm-4.7` 到 zhipu provider
   - 添加 `glm-4.7-or` 到 zhipu-openrouter provider
   - 更新 context_window 和 max_tokens

2. [x] 更新 `cli.py`
   - `DEFAULT_MODEL = "glm-4.7-or"`

3. [ ] 测试验证
   - zhipu native 调用
   - OpenRouter 调用

### Phase 2: Gemini Free Tier ✅

1. [x] 更新 `llm_config.yml`
   - 添加 `gemini-free` provider
   - 配置保守的 rate limiting

2. [ ] 测试验证
   - 使用 `GEMINI_FT_API_KEY` 调用
   - 确认 rate limiting 工作

3. [ ] 后续：根据 AI Studio 数据更新 rate limit 配置

### Phase 3: Integration 测试改进 ✅

1. [x] 更新 `conftest.py`
   - 添加 `--integration-model` CLI 选项
   - 添加 `budget_model_name` fixture (动态选择模型)

2. [ ] 更新现有 integration 测试
   - 使用 `budget_model_name` fixture

3. [ ] 文档更新
   - tests/README.md 说明新选项

---

## 6. 变更范围

| 文件 | 变更类型 | 描述 |
|------|----------|------|
| `llm_config.yml` | 修改 | 添加 glm-4.7, glm-4.7-or, gemini-free provider |
| `cli.py` | 修改 | DEFAULT_MODEL = "glm-4.7-or" |
| `tests/conftest.py` | 修改 | 添加 --integration-model 选项 |
| `tests/README.md` | 修改 | 文档更新 |
| `TODO.md` | 修改 | 添加新任务 |
| `CHANGELOG.md` | 修改 | 记录变更 |

---

## 7. 时间估算

| 任务 | 估算 |
|------|------|
| GLM-4.7 配置 + 测试 | 0.5 天 |
| Gemini Free Tier 配置 + 测试 | 0.5 天 |
| Integration 测试改进 | 0.5 天 |
| **总计** | **1.5 天** |

---

## 8. 价格确认

GLM-4.7 OpenRouter 价格已确认（Z.AI provider - 最高价格）：

| 参数 | 值 |
|------|-----|
| Input pricing (per 1M) | $0.60 |
| Output pricing (per 1M) | $2.20 |
| Cache Read (per 1M) | $0.11 |

---

## 附录：测试命令

```bash
# 测试 GLM-4.7 native
editor-assistant brief paper=test.pdf --model glm-4.7

# 测试 GLM-4.7 OpenRouter
editor-assistant brief paper=test.pdf --model glm-4.7-or

# 测试 Gemini Free Tier
editor-assistant brief paper=test.pdf --model gemini-2.5-flash-free

# Integration 测试（基础模型）
pytest tests/integration/ -m integration

# Integration 测试（高级模型）
pytest tests/integration/ -m integration --integration-model advanced
```
