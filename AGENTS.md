# AGENTS.md — 任务管理

> 本文件是 agent 的任务入口。每次启动时读此文件，了解项目上下文和当前任务。
> 完成任务后更新状态，归档已完成任务到底部。

## 项目上下文

- **项目**：Editor Assistant — AI-powered CLI + Python library for processing documents with LLMs
- **版本**：0.5.1
- **README**：[README.md](README.md) — 安装、使用方法、支持模型列表
- **技术参考**：[DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) — 架构、模块、配置、测试、常见模式
- **变更日志**：[CHANGELOG.md](CHANGELOG.md) — 版本历史
- **开发环境**：多 agent 环境（Cursor + Claude Code + Codex）

### 双重角色

1. **独立 CLI 工具**：`editor-assistant brief/outline/translate/batch/...`，处理 PDF/DOCX/URL 等多格式文档，生成研究简讯、大纲、翻译
2. **库依赖**：通过 `pip install -e .` 被其他项目引用，提供：
   - `LLMClient` — 异步多模型 API 客户端（Deepseek、Gemini、OpenAI、Anthropic、GLM 等）
   - `config.llm_models.get_model_details()` — 模型配置查询
   - `config.constants` — 可配置常量（超时、速率限制等）

### 核心模块

| 模块 | 职责 |
|------|------|
| `cli.py` | CLI 入口，asyncio.run() |
| `main.py` | 编排层，EditorAssistant 类 |
| `llm_client.py` | 异步 LLM API 客户端（httpx），多 provider 路由 |
| `md_processor.py` | 异步处理（Semaphore 并发控制） |
| `md_converter.py` | 格式转换（PDF/DOCX/HTML → Markdown） |
| `tasks/` | 可插拔任务系统（TaskRegistry + @register） |
| `storage/` | SQLite 持久化（运行历史、统计） |
| `config/` | 模型配置（llm_config.yml）、常量、prompt 模板 |

---

## 当前任务

### TASK-001：Tiered Pricing System

- **状态**：`pending`
- **Phase**：1
- **优先级**：中
- **预计工作量**：1 天
- **目标**：支持阶梯计费模型（如 Gemini 3 Pro: <200k vs >200k tokens）
- **执行步骤**：
  1. 扩展 `llm_config.yml` 支持 `pricing_tiers` 字段
  2. 修改 `LLMClient` 计费逻辑
  3. 更新成本统计显示
  4. 更新文档

### TASK-002：模型参数完善

- **状态**：`pending`
- **Phase**：1
- **优先级**：低
- **预计工作量**：0.5 天
- **目标**：正确计算输入 token 限制
- **执行步骤**：
  1. 在 `llm_config.yml` 添加 `input_max_tokens` 字段（或运行时计算 `context_window - max_tokens`）
  2. 更新验证逻辑使用正确的输入限制
  3. 更新文档说明各参数含义

### TASK-003：Reliability Hardening

- **状态**：`pending`
- **Phase**：1
- **优先级**：中
- **预计工作量**：0.5 天
- **目标**：遗留的可靠性改进
- **执行步骤**：
  1. Make file output optional via CLI flag (default off)
  2. No DB writes for failed inputs
  3. Add targeted tests for reliability features

### TASK-004：Dependency Injection

- **状态**：`backlog`
- **Phase**：2
- **预计工作量**：1–2 天
- **目标**：解耦组件，提升可测试性
- **执行步骤**：
  1. 定义接口/协议 (LLMClientProtocol, ConverterProtocol)
  2. 重构为依赖注入模式
  3. 添加简单的工厂/容器
  4. 更新测试使用 mock

### TASK-005：Plugin System — 外部加载

- **状态**：`backlog`
- **Phase**：2
- **前置**：核心 Registry Pattern 已实现（TaskRegistry）
- **预计工作量**：2–3 天
- **目标**：支持外部插件目录加载
- **执行步骤**：
  1. 实现插件目录扫描 (`~/.editor-assistant/plugins/`)
  2. 启动时动态加载插件
  3. 编写插件开发文档
  4. 添加示例插件

### TASK-006：ClassifyTask 结构化输出

- **状态**：`backlog`
- **Phase**：2
- **预计工作量**：1 天
- **目标**：新增分类任务，输出结构化 JSON

### TASK-007：SciContent Benchmark Module

- **状态**：`backlog`
- **Phase**：2
- **预计工作量**：2–3 周
- **目标**：科技内容创作/科研阅读场景的系统化评估框架
- **说明**：
  - 任务覆盖：写作风格（新闻/学术/科普）、学科、话题
  - 评估维度：生成质量、速度、成本效率、一致性
  - CLI: `editor-assistant benchmark`
  - 输出: JSON Lines

### TASK-008：Interactive AI Assistant

- **状态**：`backlog`
- **Phase**：2+
- **预计工作量**：3–4 周
- **目标**：自主选题 + 内容生成 + 反馈收集闭环

### TASK-009：Configuration File Support

- **状态**：`backlog`
- **Phase**：3（与 GUI 一起实现）
- **预计工作量**：1 天
- **目标**：YAML 配置文件支持（`~/.editor-assistant/config.yml` + 项目级 `.editor-assistant.yml`）
- **说明**：CLI 对非技术用户操作难度较大，在 Web UI 之前实用性有限

### TASK-010：Web UI / Browser Extension

- **状态**：`backlog`
- **Phase**：3
- **预计工作量**：4–6 周（Web UI MVP）
- **目标**：FastAPI + Vue/React SPA，Chrome Extension

### TASK-011：Persistence Layer 优化

- **状态**：`backlog`
- **Phase**：远期
- **目标**：
  - Resume semantics / DB record consistency（原始 run 与 resumed run 的关联）
  - Resume/Export query efficiency（避免 N+1 查询）

---

## 已完成任务

### GLM-4.7 + Gemini Free Tier ✓

- **完成日期**：2026-01-04
- **产出**：
  - GLM-4.7 模型支持（zhipu native + OpenRouter），设为默认模型
  - Gemini Free Tier 支持（gemini-2.5-flash-free, gemini-2.5-flash-lite-free）
  - Integration 测试 `--integration-model base/advanced` 选项

### GPT-5.2 / Claude 4.6 / Gemini 3.1 Pro 模型更新 ✓

- **完成日期**：2026-01（commit 73be695）
- **产出**：新增 GPT-5.2、Claude Opus 4.6、Claude Sonnet 4.6、Gemini 3.1 Pro；修复 OpenRouter max_tokens

### Resume & Export ✓

- **完成日期**：2025-12
- **产出**：
  - `editor-assistant resume` 命令（恢复中断任务）
  - `editor-assistant export` 命令（JSON/CSV 导出）

### v0.5.x Async Refactor ✓

- **完成日期**：2025-12-19
- **产出**：
  - 全异步架构（asyncio + httpx），4.46x 性能提升
  - Semaphore 并发控制（默认 5 并发）
  - Rich batch UI 进度条
  - 147 个测试

### SQLite Storage + CLI ✓

- **完成日期**：2025-12-18
- **产出**：
  - SQLite 持久化（runs/inputs/outputs/token_usage）
  - `history`、`stats`、`show` 命令

### Task Architecture ✓

- **完成日期**：2025-12-18
- **产出**：TaskRegistry + @register 装饰器，brief/outline/translate 重构

### v0.3.1 代码质量大修 ✓

- **完成日期**：2025-12-17
- **产出**：
  - 修复 17 个代码质量问题（O(n²)、typo、dead code、error handling 等）
  - 新增：centralized constants、rate limiting、response caching、content validation

---

## 任务状态说明

| 状态 | 含义 |
|------|------|
| `active` | 当前正在执行，agent 看到后直接开始 |
| `pending` | 已就绪，等待人工确认后改为 active |
| `blocked` | 有外部依赖，无法执行 |
| `backlog` | 远期规划，非当前优先级 |
| `done` | 已完成并验收，归档到"已完成任务"区 |
