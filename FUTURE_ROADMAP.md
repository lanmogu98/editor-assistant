# Future Roadmap

This document outlines remaining architectural improvements that require significant effort but provide substantial value.

---

## 1. Async/Concurrent Processing

**Status:** ✅ Completed (v0.5.0)

**Why it matters:**
- Currently processes documents sequentially (N documents = N × time)
- Network I/O wait time is wasted (LLM API calls take 2-30 seconds each)
- (Solved: Streaming responses are now supported, but processing is still serial)

**Value:** 3-5x speedup for multi-document workflows

**Implementation Plan:**
```
1. Add async HTTP client (aiohttp or httpx)
2. Convert LLMClient.generate_response() to async
3. Add asyncio.gather() for parallel document processing
4. Optional: Add streaming support for real-time output
```

**Estimated effort:** 2-3 days

---

## 2. Configuration File Support

**Status:** ⏸️ Deferred to Phase 3 (与 GUI 一起实现)

> 对非技术用户操作难度较大，在浏览器插件/Web UI 之前实用性有限。

**Why it matters:**
- Users must pass CLI args every time
- No way to set project-specific defaults
- Environment variables are clunky for multiple settings

**Value:** Better UX, reproducible workflows

**Implementation Plan:**
```
1. Create config schema (YAML):
   ~/.editor-assistant/config.yml     # User defaults
   .editor-assistant.yml              # Project overrides

2. Add config loader in config/settings.py
3. Merge priority: CLI args > project > user > defaults
4. Document supported options
```

**Example config:**
```yaml
model: gpt-4
cache_enabled: true
rate_limit_per_minute: 60
output_dir: ./output
blocked_publishers:
  - nytimes.com
```

**Estimated effort:** 1 day

---

## 3. Dependency Injection / Loose Coupling

**Why it matters:**
- Hard to unit test (classes instantiate their dependencies directly)
- Cannot swap implementations (e.g., mock LLM for testing)
- Adding new providers requires modifying existing code

**Value:** Testability, extensibility, cleaner architecture

**Implementation Plan:**
```
1. Define interfaces/protocols for LLMClient, Converter, Validator
2. Pass dependencies via constructor (not self-instantiated)
3. Add simple factory or container for wiring
4. Update tests to use mocks
```

**Example:**
```python
# Before
class MDProcessor:
    def __init__(self, model_name):
        self.llm_client = LLMClient(model_name)  # tight coupling

# After
class MDProcessor:
    def __init__(self, llm_client: LLMClientProtocol):
        self.llm_client = llm_client  # injected
```

**Estimated effort:** 1-2 days

---

## 4. Plugin/Extension System (Partial)

**Status:** ⚠️ Core Registry Pattern implemented (Task Architecture), External loading pending.

**Why it matters:**
- Adding new converters requires modifying core code
- Users cannot add custom prompts without forking
- No way to extend without touching internals

**Value:** User extensibility, cleaner separation

**Implementation Plan:**
```
1. Define plugin interfaces (Converter, Processor, Prompt) ✅ (TaskRegistry implemented)
2. Add registry pattern for dynamic registration ✅
3. Scan plugin directories on startup (Pending)
4. Document plugin development (Pending)
```

**Example:**
```python
# plugins/my_converter.py
@register_converter("my-format")
class MyConverter(ConverterProtocol):
    def convert(self, path: str) -> MDArticle:
        ...
```

**Estimated effort:** 2-3 days

---

## 5. Persistence Layer (Partial)

**Status:** ✅ Core Implemented (Schema + History/Stats CLI), `resume` command pending.

**Why it matters:**

- Token usage only saved to text files
- No historical tracking or analytics
- Cannot resume interrupted processing

**Value:** Cost tracking, audit logs, checkpoint/resume

**Implementation Plan:**
```
1. Add SQLite database (lightweight, no server needed) ✅
2. Schema: sessions, requests, token_usage, cache ✅
3. Add CLI commands: `history`, `stats` ✅, `resume` (Pending)
4. Optional: Export to CSV/JSON (Pending)
```

**Estimated effort:** 2-3 days

---

## Priority Order

| Priority | Item | Effort | Impact |
|----------|------|--------|--------|
| 1 | Resume capability & Export | 1 day | High (完善 Persistence) |
| 2 | Tiered Pricing System | 1 day | Medium (成本准确性) |
| 3 | Dependency injection | 1-2 days | Medium (Testability) |
| 4 | Plugin system (外部加载) | 2-3 days | Medium (Extensibility) |
| ~~5~~ | ~~Configuration file support~~ | ~~1 day~~ | ~~Deferred to Phase 3~~ |

> **Note**: Configuration file support 对非技术用户操作难度较大，在 GUI（如浏览器插件）之前实用性有限，已推迟至 Phase 3 与前端一起实现。

---

## Completed Items (This Session)

✅ Async/Concurrent Processing: `httpx` + `asyncio` refactor, 5x performance boost (v0.5.0)
✅ Persistence Layer: SQLite storage, Schema, `history`/`stats` commands (Phase 1)
✅ Performance: O(n²) string fix, lazy loading, single-pass extraction
✅ Maintenance: Typos, dead code, error handling, type hints
✅ Scaling: Rate limiting, response caching
✅ Validation: Content validation module
✅ Code quality: Centralized constants, circular import fix

**Total: 16 issues resolved, 48 tests added**

---

## 🔮 Long-Term Vision (Phase 2+)

> 以下为长期产品愿景，在当前 TODO 和基础架构完善后逐步实施。

### 6. Tiered Pricing System

**Why it matters:**
- 许多模型按上下文长度阶梯计费（如 Gemini 3 Pro: <200k vs >200k tokens）
- 当前统一计费方式无法准确估算成本

**Implementation Plan:**
```yaml
# llm_config.yml 扩展
models:
  gemini-3-pro:
    id: "gemini-3-pro-preview"
    pricing_tiers:
      - max_tokens: 200000
        input: 2.00
        output: 12.00
      - max_tokens: null  # unlimited
        input: 4.00
        output: 18.00
```

```python
# LLMClient 计费逻辑
def calculate_cost(self, input_tokens, output_tokens):
    for tier in self.pricing_tiers:
        if tier.max_tokens is None or input_tokens <= tier.max_tokens:
            return (input_tokens * tier.input + output_tokens * tier.output) / 1_000_000
```

**Estimated effort:** 1 day

---

### 7. SciContent Benchmark Module

**Why it matters:**
- 缺乏针对科技内容创作/科研阅读场景的系统化评估框架
- 无法定量比较不同模型在特定任务上的表现

**Core Capabilities:**
1. **任务覆盖**: 写作风格（新闻/学术/科普）、学科（CS/Bio/Physics）、话题
2. **评估维度**:
   - 生成质量（人工 + 自动化指标：BLEU/ROUGE/GPT-as-judge）
   - 生成速度（首 token 时间、总耗时）
   - 成本效率（$/1K tokens、$/task）
   - 一致性（多次生成的方差）
3. **输出格式**: JSON Lines，便于分析和可视化

**Architecture:**
```
benchmark/
├── tasks/                    # 任务定义
│   ├── brief_generation.py
│   ├── outline_generation.py
│   └── translation.py
├── evaluators/               # 评估器
│   ├── quality.py           # GPT-as-judge, BLEU, ROUGE
│   ├── latency.py           # TTFT, total time
│   └── cost.py              # Token-based cost
├── datasets/                 # 测试数据集
│   ├── arxiv_cs/
│   ├── arxiv_bio/
│   └── news_tech/
├── runners/                  # 运行器
│   └── benchmark_runner.py
└── reports/                  # 结果输出
    ├── leaderboard.json
    └── detailed_results.jsonl
```

**CLI:**
```bash
# 运行 benchmark
editor-assistant benchmark --models gemini-3-flash,deepseek-r1 --tasks brief,outline

# 查看结果
editor-assistant benchmark-report --format table
```

**Future Extension - Agentic Tasks:**
- 自主选题（根据用户兴趣/热点趋势）
- 多轮迭代生成（根据评估反馈自我改进）
- 多 agent 协作（研究 agent + 写作 agent + 审核 agent）

**Estimated effort:** 2-3 weeks

---

### 8. Interactive AI Assistant (SciEditor Assistant)

**Why it matters:**
- 科技内容编辑需要 human-in-the-loop 工作流
- 用户反馈是宝贵的 RLHF 信号

**Core Capabilities:**
1. **自主选题**: 基于 RSS feeds、arXiv、热点趋势自动推荐选题
2. **内容生成**: 根据用户要求生成初稿
3. **反馈收集**:
   - 选题通过率
   - 人工修订 diff
   - 用户评分
4. **反馈闭环**: 反馈数据用于 benchmark 评估或 fine-tuning

**Data Schema:**
```sql
-- 选题记录
CREATE TABLE topics (
    id INTEGER PRIMARY KEY,
    source_url TEXT,
    suggested_at TIMESTAMP,
    status TEXT,  -- 'suggested', 'accepted', 'rejected', 'published'
    rejection_reason TEXT
);

-- 生成记录
CREATE TABLE generations (
    id INTEGER PRIMARY KEY,
    topic_id INTEGER,
    model TEXT,
    prompt TEXT,
    raw_output TEXT,
    edited_output TEXT,  -- 人工修订后
    edit_distance INTEGER,
    user_rating INTEGER,  -- 1-5
    feedback_text TEXT
);
```

**Feedback → Benchmark Integration:**
```python
# 从用户反馈生成 benchmark 数据
def export_feedback_to_benchmark(db_path: str) -> List[BenchmarkSample]:
    """
    Convert user feedback into benchmark evaluation samples.
    - Accepted topics with high ratings → positive examples
    - Large edit distances → areas for improvement
    """
    ...
```

**Estimated effort:** 3-4 weeks

---

### 9. Frontend Forms (Phase 3)

**Why it matters:**
- CLI 对非技术用户不友好
- 交互式编辑需要 GUI

**Implementation Options:**

| 形态 | 技术栈 | 优点 | 缺点 |
|------|--------|------|------|
| **Web UI** | FastAPI + React/Vue | 跨平台、易部署 | 需要服务器 |
| **Browser Extension** | Chrome Extension + Web Components | 无缝集成浏览 | 功能受限 |
| **Desktop App** | Electron / Tauri | 离线使用、全功能 | 包体积大 |
| **RSS Reader** | Tauri + SQLite | 专注阅读场景 | 需要维护订阅源 |

**Recommended Approach:**
1. **Phase 3.1**: Web UI (FastAPI + Vue/React) - 核心功能 MVP
2. **Phase 3.2**: Browser Extension - 复用 Web UI 组件，提供页面内助手
3. **Phase 3.3**: Desktop App (Tauri) - 打包 Web UI，添加离线支持

**Web UI Architecture:**
```
frontend/
├── web/                      # Vue/React SPA
│   ├── components/
│   │   ├── TopicSuggester.vue
│   │   ├── ContentEditor.vue
│   │   ├── FeedbackPanel.vue
│   │   └── BenchmarkDashboard.vue
│   └── pages/
│       ├── Editor.vue
│       ├── Benchmark.vue
│       └── Settings.vue
├── api/                      # FastAPI backend
│   ├── routes/
│   │   ├── topics.py
│   │   ├── generations.py
│   │   └── benchmark.py
│   └── main.py
└── extension/                # Chrome Extension
    ├── popup/
    ├── content-script/
    └── background/
```

**Estimated effort:** 4-6 weeks (Web UI MVP)

---

## Updated Priority Order

| Phase | Item | Effort | Impact |
|-------|------|--------|--------|
| **1 (Current)** | Resume capability & Export | 1 day | High (完善 Persistence) |
| **1** | Tiered pricing | 1 day | Medium (成本准确性) |
| **1** | Dependency injection | 1-2 days | Medium (Testability) |
| **2** | Benchmark module | 2-3 weeks | High (Product) |
| **2** | Interactive assistant (backend) | 3-4 weeks | High (Product) |
| **3** | Configuration file support | 1 day | High (与 GUI 配合) |
| **3** | Web UI | 4-6 weeks | High (Adoption) |
| **3** | Browser extension | 2 weeks | Medium (UX) |
| **3** | Desktop app | 2-3 weeks | Medium (Offline) |
