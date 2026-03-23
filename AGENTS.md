# AGENTS.md — Editor Assistant AI Context

## Project Overview

Editor Assistant is an AI-powered CLI tool and Python library for processing documents (PDF, DOCX, HTML, URLs, etc.) with LLMs. It generates research briefs, outlines, and translations using multiple LLM providers.

双重角色：独立 CLI 工具 + 可被其他项目 `pip install -e .` 引用的库依赖（LLMClient、config 模块）。

## Project Shape

- **Project Type**: software (CLI + library)
- **Primary Artifacts**: Python package, CLI commands
- **Language / Runtime**: Python 3.10+
- **Package Manager**: uv (`pyproject.toml`, PEP 621)
- **Project Layout**: `src/editor_assistant/` (src layout)
- **Storage**: SQLite (runtime history, stats)
- **Key Tools / Libraries**: httpx, pydantic, rich, jinja2, markitdown, trafilatura, readabilipy
- **Verification**: pytest (unit + integration), black, flake8, mypy

## Current Implementation Status

> AI agents should read this table first in new sessions.

| Module | Status | Note |
|--------|--------|------|
| `cli.py` | done | CLI 入口，asyncio.run()，8 个子命令 |
| `main.py` | done | 编排层，EditorAssistant 类 |
| `llm_client.py` | done | 异步 LLM API 客户端（httpx），多 provider 路由 |
| `md_processor.py` | done | 异步处理，Semaphore 并发控制 |
| `md_converter.py` | done | 格式转换（PDF/DOCX/HTML → Markdown） |
| `clean_html_to_md.py` | done | HTML 清理工具 |
| `content_validation.py` | done | 输入内容验证 |
| `data_models.py` | done | Pydantic 数据模型 |
| `utils.py` | done | 工具函数 |
| `config/` | done | 模型配置（llm_config.yml）、常量、prompt 模板 |
| `tasks/` | done | 可插拔任务系统（TaskRegistry + @register） |
| `storage/` | done | SQLite 持久化（runs/inputs/outputs/token_usage） |

## Key Design Conventions

### Async Architecture

- All I/O is async (httpx, not requests)
- Semaphore-based concurrency control (default 5 concurrent)
- CLI entry point uses `asyncio.run()`

### Task System

- Tasks register via `@TaskRegistry.register()` decorator
- Each task in `tasks/` is a self-contained module inheriting from `Task` base class
- New tasks: create file in `tasks/`, use `@register`, inherit `Task`

### LLM Client

- Multi-provider routing: Deepseek, Gemini, OpenAI, Anthropic, GLM, OpenRouter
- Model config in `config/llm_config.yml` — single source of truth for all model/provider settings
- Rate limiting and response caching built in
- Adding models: edit `llm_config.yml` only, no Python code changes

### Library API Contract

外部项目通过以下接口引用本项目：
- `LLMClient` — 异步多模型 API 客户端
- `config.llm_models.get_model_details()` — 模型配置查询
- `config.constants` — 可配置常量（超时、速率限制等）

Breaking changes to these APIs require version bump.

## Directory Responsibilities

| Directory | Responsibility | Key Files |
|-----------|---------------|-----------|
| `src/editor_assistant/` | Main package | `cli.py`, `main.py`, `llm_client.py`, `md_processor.py` |
| `src/editor_assistant/config/` | Model config, constants, prompt templates | `llm_config.yml`, `constants.py`, `prompts/` |
| `src/editor_assistant/tasks/` | Pluggable task modules | `base.py`, `brief.py`, `outline.py`, `translate.py` |
| `src/editor_assistant/storage/` | SQLite persistence | `database.py`, `repository.py` |
| `tests/unit/` | Unit tests | 11 test files |
| `tests/integration/` | Integration tests (real API calls) | 6 test files |
| `docs/design_docs/` | RFCs and design proposals | `rfc_async_refactor.md` |
| `docs/decisions/` | Architecture Decision Records | `001-async-architecture.md` |
| `docs/reports/` | Verification reports | `async_verification_report.md` |

## Code Style

- `black` for formatting
- `flake8` for linting
- `mypy` for type checking
- Type hints on all public APIs
- Async/await throughout hot paths

## Entry / Workflow Commands

```bash
# Primary CLI commands
editor-assistant brief <input>       # Generate research brief
editor-assistant outline <input>     # Generate outline
editor-assistant translate <input>   # Translate document
editor-assistant batch <dir>         # Batch process directory
editor-assistant resume <run_id>     # Resume interrupted run
editor-assistant export <run_id>     # Export results (JSON/CSV)
editor-assistant history             # Show run history
editor-assistant stats               # Show usage statistics
editor-assistant show <run_id>       # Show run details

# Utility commands
any2md <file>                        # Convert any format to Markdown
html2md <file>                       # Clean HTML to Markdown
```

## Workflow Commands

- Install: `pip install -e .`
- Install dev: `pip install -e ".[dev]"`
- Test unit: `pytest tests/unit/`
- Test integration: `pytest tests/integration/`
- Lint: `flake8 src/`
- Type check: `mypy src/`
- Format: `black src/ tests/`

## Commit Conventions

Use conventional commits: `<type>: <subject>`

Types: `feat`, `fix`, `refactor`, `docs`, `chore`, `test`

## Task Entry

- **Direction**: See `ROADMAP.md` for milestones and project phases
- **Current work**: `gh issue list --label p1` for high-priority items
- **Pick a task**: `gh issue list --state open --assignee @me` or unassigned p1/p2 issues
- **Deep context**: Check `.agents/projects/` for evolution logs on complex work
- **File new issues**: Use the `file-issue` skill or `gh issue create`
- **Recommended labels**: Priority — `p1` (this week), `p2` (this quarter), `p3` (later). Type — `bug`, `enhancement`, `docs`, `agent-generated`

## Working Memory

- AI agents store project-level memory in `.memory/` (not the default `~/.claude/projects/` path)
- `.memory/MEMORY.md` is the index; individual memories are separate files
- This convention ensures cross-agent availability and survives project path changes

## Security Constraints

- Never commit: `.env`, `*.db`, API keys, tokens
- Test API calls must be mocked (unit tests)
- Logs must not contain full API keys or tokens

## Open Questions

1. Tiered pricing model structure — how to represent variable rates (e.g., Gemini 3 Pro: <200k vs >200k tokens) in `llm_config.yml`
2. Plugin system external loading architecture — how to discover and load plugins from `~/.editor-assistant/plugins/`
3. Web UI framework choice: FastAPI + Vue vs FastAPI + React

## Technical Reference

Full architecture documentation: `DEVELOPER_GUIDE.md`
