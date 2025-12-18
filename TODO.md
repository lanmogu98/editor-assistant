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
- [x] 创建 `DEVELOPER.md` 开发者文档
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
- [x] 更新 DEVELOPER.md 相关文档
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
- [x] 添加示例：更新 DEVELOPER.md "Adding a New Task Type" 章节
- [x] 更新 CHANGELOG

### ~~4. 分支: feature/multi-task~~ ✅ 已完成
**优先级: 高 | 预计工作量: 0.5天**

- [x] CLI 添加 `process` 命令，支持 `--tasks` 参数
- [x] 实现串行多任务执行（同一输入执行多个任务）
- [x] 更新 README, DEVELOPER.md, CHANGELOG
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

---

## 📋 用户提出的原始需求（供参考）

1. **Gemini thinking 模式** - ✅ 已完成
2. **OpenRouter 模型测试** - ✅ 已完成
3. **流式输出支持** - ✅ 已完成
4. **代码模块重构** - ✅ 已完成（Task 架构 + 多任务执行）
5. **测试模块重构** - ✅ 已完成（单元测试 + 集成测试）
5. **模型参数完善** - input_max, output_max, context_window 的整合
6. **Rate limit per provider** - 每个模型单独控制
7. **Cache 模块说明** - ✅ 已在 DEVELOPER.md 文档中说明
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

- [DEVELOPER.md](./DEVELOPER.md) - 开发者指南
- [CHANGELOG.md](./CHANGELOG.md) - 变更日志
- [FUTURE_ROADMAP.md](./FUTURE_ROADMAP.md) - 长期路线图
- [ISSUES_REPORT.md](./ISSUES_REPORT.md) - 问题报告

