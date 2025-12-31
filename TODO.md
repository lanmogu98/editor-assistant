# Editor Assistant - TODO

> 最后更新: 2025-12-31
> 
> 此文件是当前待完成任务的执行清单，与 [FUTURE_ROADMAP.md](./FUTURE_ROADMAP.md) 保持同步。

---

## 🔄 Phase 1: 当前待完成

### 1. Resume Capability & Export
**优先级: 高 | 预计工作量: 1天**

> 完善 Persistence Layer，提升可靠性和数据可用性。

- [ ] 实现 `resume` 命令 - 恢复中断的处理任务
  - 从数据库读取 `status='aborted'` 的运行记录
  - 重新执行未完成的输入
- [ ] 实现 Export 功能
  - `editor-assistant export --format csv` 导出历史记录
  - `editor-assistant export --format json` 导出为 JSON
- [ ] 更新文档 (README, DEVELOPER_GUIDE, CHANGELOG)

### 2. Tiered Pricing System
**优先级: 中 | 预计工作量: 1天**

> 支持阶梯计费模型（如 Gemini 3 Pro: <200k vs >200k tokens）。

- [ ] 扩展 `llm_config.yml` 支持 `pricing_tiers` 字段
- [ ] 修改 `LLMClient` 计费逻辑
- [ ] 更新成本统计显示
- [ ] 更新文档

### 3. 模型参数完善
**优先级: 低 | 预计工作量: 0.5天**

- [ ] 在 `llm_config.yml` 添加 `input_max_tokens` 字段
- [ ] 或在运行时计算: `input_max = context_window - max_tokens`
- [ ] 更新验证逻辑使用正确的输入限制
- [ ] 更新文档说明各参数含义

### 4. Reliability Hardening (遗留)
**优先级: 中 | 预计工作量: 0.5天**

- [ ] Make file output optional via CLI flag (default off)
- [ ] No DB writes for failed inputs
- [ ] Add targeted tests for reliability features

---

## 📋 Phase 2: 产品功能

> 在 Phase 1 完成后开始。

### 5. Dependency Injection
**预计工作量: 1-2天**

- [ ] 定义接口/协议 (LLMClientProtocol, ConverterProtocol)
- [ ] 重构为依赖注入模式
- [ ] 添加简单的工厂/容器
- [ ] 更新测试使用 mock

### 6. Plugin System (外部加载)
**预计工作量: 2-3天**

> 核心 Registry Pattern 已实现，需要添加外部插件加载。

- [ ] 实现插件目录扫描 (`~/.editor-assistant/plugins/`)
- [ ] 启动时动态加载插件
- [ ] 编写插件开发文档
- [ ] 添加示例插件

### 7. ClassifyTask 结构化输出
**预计工作量: 1天**

- [ ] 设计分类任务的结构化输出 schema (JSON)
- [ ] 实现 ClassifyTask
- [ ] 添加到 TaskRegistry

### 8. Benchmark Module
**预计工作量: 2-3周**

> 科技内容创作/科研阅读场景的系统化评估框架。

- [ ] 设计任务覆盖和评估维度
- [ ] 实现 benchmark runner
- [ ] CLI: `editor-assistant benchmark`
- [ ] 输出: JSON Lines 格式

---

## ⏸️ Phase 3: 前端 & 用户配置

> 需要 GUI 支持，推迟至前端开发阶段。

### Configuration File Support
- [ ] YAML 配置文件 (`~/.editor-assistant/config.yml`)
- [ ] 项目级配置 (`.editor-assistant.yml`)
- [ ] 合并优先级: CLI > project > user > defaults

### Web UI / Browser Extension
- [ ] FastAPI + Vue/React SPA
- [ ] Chrome Extension
- [ ] 与配置系统集成

---

## ✅ 已完成 (归档)

<details>
<summary>点击展开已完成任务</summary>

### v0.5.x Async Refactor
- [x] Async LLMClient (httpx)
- [x] Async MDProcessor (asyncio.Semaphore)
- [x] Integration (asyncio.gather)
- [x] Batch UI (Rich progress bars)
- [x] 4.46x performance boost

### SQLite Storage
- [x] Schema 设计和实现
- [x] `history`, `stats`, `show` 命令
- [x] 数据库位置: `~/.editor_assistant/runs.db`

### Task Architecture
- [x] TaskRegistry + @register 装饰器
- [x] 重构 brief, outline, translate 任务
- [x] Multi-task execution (`process` 命令)

### Streaming & Thinking
- [x] SSE 流式输出
- [x] Gemini thinking mode (`--thinking`)
- [x] Token 估算

### Rate Limiting & Reliability
- [x] Per-provider rate limit
- [x] Request timeout
- [x] Retry handling
- [x] Content validation

### Documentation
- [x] DEVELOPER_GUIDE.md
- [x] FUTURE_ROADMAP.md
- [x] CHANGELOG.md

### Bug Fixes
- [x] `clean` 命令 API 调用错误
- [x] `convert` 命令 URL 路径处理
- [x] 空 `deepseek` provider 验证错误
- [x] Pydantic v2 migration (ConfigDict)

</details>

---

## 🔗 相关文档

- [DEVELOPER_GUIDE.md](./DEVELOPER_GUIDE.md) - 开发者指南
- [CHANGELOG.md](./CHANGELOG.md) - 变更日志
- [FUTURE_ROADMAP.md](./FUTURE_ROADMAP.md) - 长期路线图

