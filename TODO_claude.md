# Editor Assistant - 优化计划 TODO

> 创建日期: 2025-12-18
> 最后更新: 2025-12-18

---

## ✅ 已完成

### 分支: feature/openrouter-test (已合并)
- [x] 测试 OpenRouter 模型调用
- [x] 修复 API key 环境变量名（使用 `*_OPENROUTER` 后缀）
- [x] 验证 `gpt-4.1-or` 正常工作
- [x] 验证 `claude-sonnet-4-or` 正常工作

### 分支: docs/developer-guide (已合并)
- [x] 创建 `DEVELOPER_GUIDE.md` 开发者文档
  - [x] 架构概览和数据流图
  - [x] 模块参考表
  - [x] 添加新模型指南
  - [x] 添加新任务类型指南
  - [x] 配置系统文档
  - [x] 测试指南
  - [x] 常见模式（错误处理、验证、缓存）

### 其他修复 (已合并到 main)
- [x] 修复 `clean` 命令 API 调用错误
- [x] 修复 `convert` 命令 URL 路径处理
- [x] 修复空 `deepseek` provider 导致的验证错误

---

## 🔄 待完成

### ~~1. 分支: feature/rate-limit-per-provider~~ ✅ 已完成
**优先级: 高 | 预计工作量: 1天**

- [x] 修改 `llm_config.yml` 添加 per-provider rate limit 配置
- [x] 修改 `ProviderSettings` Pydantic 模型支持 rate_limit 字段
- [x] 修改 `LLMClient` 从 provider 配置读取 rate limit
- [x] 测试不同 provider 的 rate limit 独立生效
- [x] 更新 DEVELOPER_GUIDE.md 相关文档
- [x] 更新 CHANGELOG

### ~~2. 分支: feature/gemini-thinking~~ ✅ 已完成
**优先级: 中 | 预计工作量: 1-2天**

- [x] 研究 Gemini API 的 thinking 参数
  - OpenAI 兼容层使用 `reasoning_effort` 映射到 `thinking_level`
  - 支持 `low`, `medium`, `high`（`minimal` 仅原生 API 支持）
  - 参考: https://ai.google.dev/gemini-api/docs/gemini-3
- [x] 在 CLI 添加 `--thinking` 参数（`low`, `medium`, `high`）
- [x] 修改 `LLMClient` 支持 thinking 模式（通过 `reasoning_effort`）
- [x] 测试 thinking 模式效果（gemini-3-flash 测试通过）
- [x] 更新 CHANGELOG

### ~~3. 分支: refactor/task-architecture~~ ✅ 已完成
**优先级: 高 | 预计工作量: 2-3天**

- [x] 设计新的任务架构
  - 可插拔的任务注册系统 (`TaskRegistry` + `@register` 装饰器)
  - 支持单输入/多输入任务 (`supports_multi_input` 属性)
  - 支持多任务输出 (`post_process` 返回 `Dict[str, str]`)
- [x] 实现 TaskRegistry 系统 (`tasks/base.py`)
- [x] 重构现有任务（`brief.py`, `outline.py`, `translate.py`）
- [x] 添加示例：更新 DEVELOPER_GUIDE.md "Adding a New Task Type" 章节
- [x] 更新 CHANGELOG

### ~~4. 分支: feature/multi-task~~ ✅ 已完成
**优先级: 高 | 预计工作量: 0.5天**

- [x] CLI 添加 `process` 命令，支持 `--tasks` 参数
- [x] 实现串行多任务执行（同一输入执行多个任务）
- [x] 更新 README, DEVELOPER_GUIDE.md, CHANGELOG
- [ ] 设计 ClassifyTask 结构化输出（Phase 2）

### ~~5. 分支: feature/streaming~~ ✅ 已完成
**优先级: 中 | 预计工作量: 1天**

- [x] 修改 `LLMClient` 支持流式输出
  - 使用 `stream=True` 参数
  - 实现 SSE 响应解析
  - Token 估算（当 API 未返回 usage 时）
- [x] 添加 CLI 参数 `--no-stream`（默认开启流式）
- [x] 处理流式输出的 token 统计
- [x] 测试流式/非流式模式（deepseek-v3.2 通过）
- [x] 更新文档

### 6. 模型参数完善
**优先级: 低 | 预计工作量: 0.5天**

- [ ] 在 `llm_config.yml` 添加 `input_max_tokens` 字段
- [ ] 或在运行时计算: `input_max = context_window - max_tokens`
- [ ] 更新验证逻辑使用正确的输入限制
- [ ] 更新文档说明各参数含义

### 7. 分支: feature/sqlite-storage
**优先级: 高 | 预计工作量: 2-3天**

**问题背景：**
- 当前输出分散在各个输入文件目录中，难以追溯和管理
- 无法查询历史运行记录、聚合统计成本、对比不同模型结果
- 测试结果（程序、模型、产品设计）回顾非常不便

**方案：使用 SQLite 本地数据库统一存储**

**数据模型设计（多对多关系）：**

```sql
-- 输入表（独立存储，支持去重和复用）
CREATE TABLE inputs (
    id INTEGER PRIMARY KEY,
    type TEXT,                  -- paper, news
    source_path TEXT,
    title TEXT,
    content_hash TEXT UNIQUE,   -- MD5 用于去重
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 运行记录
CREATE TABLE runs (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    task TEXT,                  -- brief, outline, translate
    model TEXT,                 -- deepseek-v3.2, gemini-3-flash
    thinking_level TEXT,        -- low, medium, high, null
    stream BOOLEAN,
    status TEXT,                -- success, failed
    error_message TEXT
);

-- 关联表（多对多：同一输入可以跑多次，一次可以有多个输入）
CREATE TABLE run_inputs (
    run_id INTEGER REFERENCES runs(id),
    input_id INTEGER REFERENCES inputs(id),
    PRIMARY KEY (run_id, input_id)
);

-- 输出结果
CREATE TABLE outputs (
    id INTEGER PRIMARY KEY,
    run_id INTEGER REFERENCES runs(id),
    output_type TEXT,           -- main, bilingual, classification
    content_type TEXT,          -- text, json
    content TEXT
);

-- Token 使用和成本
CREATE TABLE token_usage (
    id INTEGER PRIMARY KEY,
    run_id INTEGER REFERENCES runs(id),
    input_tokens INTEGER,
    output_tokens INTEGER,
    cost_input REAL,
    cost_output REAL,
    process_time REAL
);
```

**实现步骤：**
- [x] 创建 `storage/` 模块
  - `database.py` - 数据库初始化和连接管理
  - `repository.py` - CRUD 操作封装
- [x] 数据库位置：`~/.editor_assistant/runs.db`
- [x] 修改 `MDProcessor` 在处理完成后写入数据库
- [x] 添加 CLI 查询命令
  - `editor-assistant history` - 列出历史运行
  - `editor-assistant stats` - 统计信息（按模型/任务/时间）
  - `editor-assistant show <run_id>` - 查看特定运行详情
- [x] 更新文档（DEVELOPER_GUIDE.md, README.md）

**预期查询能力：**
```sql
-- 这篇论文被测试过几次？用了哪些模型？
SELECT i.title, COUNT(DISTINCT r.id) as runs, GROUP_CONCAT(DISTINCT r.model) as models
FROM inputs i JOIN run_inputs ri ON i.id = ri.input_id JOIN runs r ON ri.run_id = r.id
WHERE i.content_hash = 'xxx' GROUP BY i.id;

-- 统计本周各模型成本
SELECT r.model, SUM(t.cost_input + t.cost_output) as total_cost
FROM runs r JOIN token_usage t ON r.id = t.run_id
WHERE r.timestamp > date('now', '-7 days') GROUP BY r.model;

-- 对比同一论文不同模型的输出
SELECT r.model, r.timestamp, o.content
FROM runs r JOIN run_inputs ri ON r.id = ri.run_id JOIN inputs i ON ri.input_id = i.id
JOIN outputs o ON r.id = o.run_id
WHERE i.title = 'XXX' AND o.output_type = 'main';
```

**可视化工具：**
- 推荐：DB Browser for SQLite、TablePlus
- 或：`pip install datasette && datasette ~/.editor_assistant/runs.db`

---

## 📋 用户提出的原始需求（供参考）

1. **Gemini thinking 模式** - ✅ 已完成
2. **OpenRouter 模型测试** - ✅ 已完成
3. **流式输出支持** - ✅ 已完成
4. **代码模块重构** - ✅ 已完成（Task 架构 + 多任务执行）
5. **测试模块重构** - ✅ 已完成（单元测试 + 集成测试）
5. **模型参数完善** - input_max, output_max, context_window 的整合
6. **Rate limit per provider** - 每个模型单独控制
7. **Cache 模块说明** - ✅ 已在 DEVELOPER_GUIDE.md 文档中说明
8. **开发者文档** - ✅ 已完成

---

## 📝 注意事项

- 每个分支完成后：
  1. 更新 CHANGELOG.md
  2. 合并到 main
  3. Push 到远程
  4. 更新此 TODO.md

- 大型重构（如 task-architecture）建议：
  - 先写设计文档
  - 分阶段实施
  - 保持向后兼容

---

## 🔗 相关文档

- [DEVELOPER_GUIDE.md](./DEVELOPER_GUIDE.md) - 开发者指南
- [CHANGELOG.md](./CHANGELOG.md) - 变更日志
- [FUTURE_ROADMAP.md](./FUTURE_ROADMAP.md) - 长期路线图
- [ISSUES_REPORT.md](./ISSUES_REPORT.md) - 问题报告

