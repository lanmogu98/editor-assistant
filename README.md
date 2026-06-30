# Editor Assistant

[English](#english) | [中文](#chinese)

## English

Editor Assistant is an AI-powered Python CLI and library for turning research papers, articles, web pages, and converted documents into briefs, outlines, and translations with LLMs. It is built for personal research workflows, but the core client and config modules can also be imported by other Python projects.

**Version: 0.6.0**

### Package Boundary

Editor Assistant now consumes the `llm-exec-core` package for model catalog loading, provider routing, token accounting, and HTTP execution. The app layer owns document workflow, tasks, prompts, SQLite storage, CLI commands, output paths, and app logging.

This branch is a coordinated two-repo/local-migration branch. Keep the current sibling-checkout dependency mode:

```toml
[tool.uv.sources]
llm-exec-core = { path = "../llm-exec-core", editable = true }
```

That relative source is intentional for this PR and for CI/workspace checkouts that test both repos together. Only after `llm-exec-core` is published should the app switch to a release-consumer configuration by removing `[tool.uv.sources]` and pinning `llm-exec-core==0.1.0`.

### Features

- **Async processing**: Uses `asyncio` and `httpx` for concurrent conversion and LLM calls.
- **Unified CLI**: `brief`, `outline`, `translate`, `process`, `batch`, `convert`, `clean`, `history`, `stats`, `show`, `resume`, and `export`.
- **Typed source inputs**: `brief` and `process` accept typed sources such as `paper=...` and `news=...`; multiple supplied inputs are processed independently.
- **SQLite run history**: Runs, inputs, outputs, and token usage are saved to a local database.
- **Optional file outputs**: Add `--save-files` to write generated markdown and token reports to disk.
- **Multi-provider models**: DeepSeek, Gemini, Qwen, GLM/Zhipu, Doubao, OpenAI via OpenRouter, and Anthropic via OpenRouter.

### Requirements

- Python 3.10+
- `uv` for project installation and command execution
- API keys for the model provider(s) you use

### Installation

```bash
git clone https://github.com/lanmogu98/editor-assistant.git
cd editor-assistant
uv sync
```

On this migration branch, `uv sync` expects a sibling checkout at `../llm-exec-core` because `pyproject.toml` uses a relative `[tool.uv.sources]` entry. In CI, use a workspace layout that checks out both repos side by side.

For a runtime-only environment:

```bash
uv sync --no-dev
```

When running from the source checkout, prefer `uv run`:

```bash
uv run editor-assistant --help
```

If you activate the project virtual environment or install the package elsewhere, the primary console scripts are also available directly as `editor-assistant` and `any2md`.

### Configuration

Set only the API keys for providers you plan to use:

```bash
# DeepSeek via Volcengine
export DEEPSEEK_API_KEY_VOLC=your_volcengine_api_key

# DeepSeek official API
export DEEPSEEK_API_KEY=your_deepseek_api_key

# Gemini paid API key
export GEMINI_API_KEY=your_gemini_api_key

# Gemini AI Studio free-tier key
export GEMINI_FT_API_KEY=your_gemini_free_tier_api_key

# Qwen via Alibaba Bailian / DashScope-compatible endpoint
export QWEN_API_KEY=your_qwen_api_key

# GLM via Zhipu AI
export ZHIPU_API_KEY=your_zhipu_api_key

# GLM via OpenRouter
export ZHIPU_API_KEY_OPENROUTER=your_openrouter_api_key

# Doubao via Volcengine
export DOUBAO_API_KEY=your_doubao_api_key

# OpenAI models via OpenRouter
export OPENAI_API_KEY_OPENROUTER=your_openrouter_api_key

# Anthropic models via OpenRouter
export ANTHROPIC_API_KEY_OPENROUTER=your_openrouter_api_key
```

Run history is stored in `~/.editor_assistant/runs.db` by default. Set `EDITOR_ASSISTANT_DB_DIR` to use a different directory.

### CLI Usage

All examples below use `uv run` because this is the recommended source-checkout workflow.

#### Generate Briefs

`brief` supports one or more typed sources. Valid source types are `paper` and `news`. When you pass multiple sources, each source is processed independently; the current CLI does not merge `paper` and `news` into a single prompt.

```bash
uv run editor-assistant brief paper=https://example.com/research-article
uv run editor-assistant brief paper=paper-a.pdf paper=paper-b.pdf --model deepseek-r1 --debug
uv run editor-assistant brief paper=paper.pdf --save-files
```

#### Generate Outlines

`outline` accepts a single input path or URL.

```bash
uv run editor-assistant outline https://arxiv.org/paper.pdf
uv run editor-assistant outline paper.pdf --model deepseek-r1
uv run editor-assistant outline paper.pdf --save-files
```

#### Translate Documents

`translate` accepts a single input path or URL and creates Chinese output. The translation task also stores a bilingual output variant.

```bash
uv run editor-assistant translate https://arxiv.org/paper.pdf
uv run editor-assistant translate document.pdf --model gemini-2.5-flash-free
uv run editor-assistant translate research.md --model deepseek-r1 --debug
uv run editor-assistant translate research.md --save-files
```

#### Run Multiple Tasks

`process` uses the same typed source format as `brief`. It runs the selected tasks serially for each supplied source, so choose tasks that make sense for every source you pass.

```bash
uv run editor-assistant process paper=paper.pdf --tasks brief,outline
uv run editor-assistant process paper=paper-a.pdf paper=paper-b.pdf --tasks brief --no-stream
uv run editor-assistant process paper=paper.pdf --tasks brief,outline --no-stream --save-files
```

#### Batch Processing

`batch` processes files in a directory concurrently with one task.

```bash
uv run editor-assistant batch ./docs/ --ext .md --task translate
uv run editor-assistant batch ./papers/ --ext .pdf --task brief --model deepseek-v3.2
uv run editor-assistant batch ./papers/ --ext .html --task outline --save-files
```

#### Convert and Clean Inputs

```bash
uv run editor-assistant convert document.pdf
uv run editor-assistant convert *.docx
uv run editor-assistant clean "https://example.com/page.html" -o clean.md
uv run editor-assistant clean page.html --stdout

# Utility console scripts are also available through uv:
uv run any2md *.docx -o converted/
```

#### Inspect Run History

```bash
uv run editor-assistant history
uv run editor-assistant history -n 50
uv run editor-assistant history --search "arxiv"
uv run editor-assistant stats
uv run editor-assistant stats -d 30
uv run editor-assistant show 1
uv run editor-assistant show 1 --output
```

#### Resume and Export

```bash
uv run editor-assistant resume --dry-run
uv run editor-assistant resume --save-files
uv run editor-assistant export history.json
uv run editor-assistant export history.csv --limit 100
```

### Common Options

These options are available on generation commands such as `brief`, `outline`, `translate`, `process`, and `batch`:

- `--model`: Choose an LLM model. Default: `glm-4.7-or`.
- `--thinking`: Reasoning level for supported Gemini models: `low`, `medium`, or `high`.
- `--no-stream`: Disable streaming output.
- `--save-files`: Persist generated markdown files and token reports to disk. The SQLite run database is still updated either way.
- `--debug`: Enable detailed debug logging.

Global options:

- `--version`: Show version information.
- `--help`: Show CLI help. Use subcommand help, such as `uv run editor-assistant brief --help`, to see current model choices.

### Supported Models

Model names are loaded from `llm_exec_core/llm_config.yml` in the `llm-exec-core` package. In this repo, `src/editor_assistant/config/llm_models.py` is a compatibility shim that re-exports the core catalog loader for older imports. Use `uv run editor-assistant brief --help` to see the current `--model` choices.

Current default model: `glm-4.7-or`.

#### DeepSeek

- Volcengine (`DEEPSEEK_API_KEY_VOLC`): `deepseek-v3.2`, `deepseek-r1`
- Official API (`DEEPSEEK_API_KEY`): `deepseek-v4-flash`, `deepseek-v4-pro`

#### Gemini

- Paid key (`GEMINI_API_KEY`): `gemini-3-flash`, `gemini-3.1-flash-lite`, `gemini-3.1-pro`
- Free-tier key (`GEMINI_FT_API_KEY`): `gemini-2.5-flash-free`, `gemini-2.5-flash-lite-free`, `gemini-3-flash-free`, `gemini-3.1-flash-lite-free`

#### Qwen

- `qwen-turbo`, `qwen-plus`, `qwen3.5-plus`, `qwen3-max-preview`, `qwen3-max`

#### GLM / Zhipu

- Zhipu API (`ZHIPU_API_KEY`): `glm-4.5`, `glm-4.6`, `glm-4.7`, `glm-5`, `glm-5.1`
- OpenRouter (`ZHIPU_API_KEY_OPENROUTER`): `glm-4.5-or`, `glm-4.6-or`, `glm-4.7-or`, `glm-5-or`, `glm-5.1-or`, `glm-5-turbo-or`

#### Doubao

- `doubao-seed-1.6`

#### OpenAI via OpenRouter

- `gpt-4o-or`, `gpt-4.1-or`, `gpt-5-or`, `gpt-5.2-or`, `gpt-5.4-or`, `gpt-5.5-or`

#### Anthropic via OpenRouter

- `claude-sonnet-4-or`, `claude-opus-4.6-or`, `claude-sonnet-4.6-or`, `claude-opus-4.7-or`, `claude-haiku-4.5-or`

### Python API

```python
import asyncio

from editor_assistant.data_models import Input, InputType, ProcessType
from editor_assistant.main import EditorAssistant


async def main():
    assistant = EditorAssistant("glm-4.7-or", debug_mode=True)

    await assistant.process_multiple(
        [Input(type=InputType.PAPER, path="paper.pdf")],
        ProcessType.OUTLINE,
    )

    await assistant.process_multiple(
        [Input(type=InputType.PAPER, path="paper.pdf")],
        ProcessType.BRIEF,
    )


if __name__ == "__main__":
    asyncio.run(main())
```

### Supported Input Formats

The converter supports common document and web formats through MarkItDown plus local HTML extraction helpers:

- Documents: PDF, DOCX, DOC, PPTX, PPT, XLSX, XLS, EPUB
- Web content: HTML files and URLs
- Text/data: TXT, MD, CSV, JSON, XML, ZIP
- Media formats supported by MarkItDown, such as images and audio, may also work depending on installed extras

### Output and Storage

- Run history, inputs, outputs, and token usage are stored in SQLite.
- Default database: `~/.editor_assistant/runs.db`
- Override database directory: `EDITOR_ASSISTANT_DB_DIR=/path/to/dir`
- With `--save-files`, generated files are written next to the source/converted markdown under `llm_summaries/<model>/`.

```text
llm_summaries/
└── <model>/
    ├── response_<title><task_suffix>_<model>_<timestamp>.md
    ├── response_bilingual_<title>_translate_<model>_<timestamp>.md  # translate only
    └── token_usage_<title><task_suffix>_<model>_<timestamp>.txt
```

### Developer Workflow

```bash
uv sync
uv run pytest tests/unit/
uv run flake8 src/
uv run mypy src/
uv run black src/ tests/
```

See `DEVELOPER_GUIDE.md` for architecture details and `docs/design_docs/`, `docs/decisions/`, and `docs/reports/` for supporting design notes and reports.

<a id="breaking-changes-in-v02"></a>
### Migration Notes

Important current CLI conventions:

- Source checkout commands should generally use `uv run ...`.
- `brief` and `process` require typed source arguments: `paper=...` or `news=...`; multiple supplied inputs are processed independently.
- `outline` and `translate` take a single plain input path or URL.
- Generated responses are saved to SQLite by default; file output is opt-in with `--save-files`.
- The default model is `glm-4.7-or`.

Older v0.1 syntax such as `--article paper:paper.pdf` is no longer supported.

### License

This project is licensed under the MIT License.

### Acknowledgments

- Microsoft MarkItDown for document conversion
- Readabilipy and Trafilatura for web content extraction
- DeepSeek, Google Gemini, Qwen, GLM/Zhipu, Doubao, OpenAI, Anthropic, and OpenRouter for LLM capabilities

---

## Chinese

### 编辑助手 (Editor Assistant)

Editor Assistant 是一个 AI 驱动的 Python CLI 和库，用于把研究论文、文章、网页和转换后的文档处理成简讯、大纲和翻译。它主要服务个人研究工作流，也可以被其他 Python 项目复用其 LLM client 和配置模块。

**版本：0.6.0**

### 包边界

Editor Assistant 现在通过 `llm-exec-core` 包来提供模型目录加载、provider 路由、token 统计和 HTTP 执行能力；应用层仍负责文档工作流、任务、prompt、SQLite 持久化、CLI、输出路径和应用日志。

当前分支是一个双仓协同的本地迁移分支，必须保留 sibling checkout 的依赖方式：

```toml
[tool.uv.sources]
llm-exec-core = { path = "../llm-exec-core", editable = true }
```

这个相对路径是当前 PR 和双仓 CI/workspace checkout 的预期配置。只有在 `llm-exec-core` 正式发布之后，才应移除 `[tool.uv.sources]`，并把依赖改成 `llm-exec-core==0.1.0`。

### 功能特色

- **异步处理**：基于 `asyncio` 和 `httpx`，支持并发转换和 LLM 请求。
- **统一 CLI**：包含 `brief`、`outline`、`translate`、`process`、`batch`、`convert`、`clean`、`history`、`stats`、`show`、`resume`、`export`。
- **带类型输入**：`brief` 和 `process` 支持 `paper=...`、`news=...` 这类带类型的输入；传入多个输入时会逐个独立处理。
- **SQLite 历史记录**：运行记录、输入、输出和 token 用量会写入本地数据库。
- **可选文件输出**：使用 `--save-files` 才会把生成的 Markdown 和 token 报告写到磁盘。
- **多模型提供商**：支持 DeepSeek、Gemini、Qwen、GLM/智谱、Doubao、OpenRouter 上的 OpenAI 和 Anthropic 模型。

### 环境要求

- Python 3.10+
- 使用 `uv` 安装和运行项目
- 至少配置一个要使用的模型提供商 API key

### 安装

```bash
git clone https://github.com/lanmogu98/editor-assistant.git
cd editor-assistant
uv sync
```

在这个迁移分支上，`uv sync` 依赖 `../llm-exec-core` 这个 sibling checkout，因为 `pyproject.toml` 中使用了相对 `[tool.uv.sources]`。CI 也需要采用双仓并排 checkout 的 workspace 布局。

仅安装运行依赖：

```bash
uv sync --no-dev
```

在源码目录运行时，推荐使用 `uv run`：

```bash
uv run editor-assistant --help
```

如果已经激活项目虚拟环境，或把包安装到了其他环境中，也可以直接使用 `editor-assistant` 和 `any2md` 这些主要 console scripts。

### 配置

只需要设置你实际使用的模型提供商 API key：

```bash
# DeepSeek via Volcengine
export DEEPSEEK_API_KEY_VOLC=your_volcengine_api_key

# DeepSeek official API
export DEEPSEEK_API_KEY=your_deepseek_api_key

# Gemini paid API key
export GEMINI_API_KEY=your_gemini_api_key

# Gemini AI Studio free-tier key
export GEMINI_FT_API_KEY=your_gemini_free_tier_api_key

# Qwen via Alibaba Bailian / DashScope-compatible endpoint
export QWEN_API_KEY=your_qwen_api_key

# GLM via Zhipu AI
export ZHIPU_API_KEY=your_zhipu_api_key

# GLM via OpenRouter
export ZHIPU_API_KEY_OPENROUTER=your_openrouter_api_key

# Doubao via Volcengine
export DOUBAO_API_KEY=your_doubao_api_key

# OpenAI models via OpenRouter
export OPENAI_API_KEY_OPENROUTER=your_openrouter_api_key

# Anthropic models via OpenRouter
export ANTHROPIC_API_KEY_OPENROUTER=your_openrouter_api_key
```

运行历史默认保存到 `~/.editor_assistant/runs.db`。如需更换目录，可以设置 `EDITOR_ASSISTANT_DB_DIR`。

### CLI 用法

下面的示例都使用 `uv run`，适用于源码 checkout 中的日常使用。

#### 生成简讯

`brief` 支持一个或多个带类型的来源，类型为 `paper` 或 `news`。传入多个来源时，每个来源会被独立处理；当前 CLI 不会把 `paper` 和 `news` 合并到同一个 prompt。

```bash
uv run editor-assistant brief paper=https://example.com/research-article
uv run editor-assistant brief paper=paper-a.pdf paper=paper-b.pdf --model deepseek-r1 --debug
uv run editor-assistant brief paper=paper.pdf --save-files
```

#### 生成大纲

`outline` 接收单个输入路径或 URL。

```bash
uv run editor-assistant outline https://arxiv.org/paper.pdf
uv run editor-assistant outline paper.pdf --model deepseek-r1
uv run editor-assistant outline paper.pdf --save-files
```

#### 翻译文档

`translate` 接收单个输入路径或 URL，生成中文译文，并同时保存双语对照输出。

```bash
uv run editor-assistant translate https://arxiv.org/paper.pdf
uv run editor-assistant translate document.pdf --model gemini-2.5-flash-free
uv run editor-assistant translate research.md --model deepseek-r1 --debug
uv run editor-assistant translate research.md --save-files
```

#### 多任务处理

`process` 使用与 `brief` 相同的带类型输入格式。它会对每个来源串行执行所选任务，所以请只传入适合这些任务的来源。

```bash
uv run editor-assistant process paper=paper.pdf --tasks brief,outline
uv run editor-assistant process paper=paper-a.pdf paper=paper-b.pdf --tasks brief --no-stream
uv run editor-assistant process paper=paper.pdf --tasks brief,outline --no-stream --save-files
```

#### 批量处理

`batch` 会对目录中的文件并发执行一个指定任务。

```bash
uv run editor-assistant batch ./docs/ --ext .md --task translate
uv run editor-assistant batch ./papers/ --ext .pdf --task brief --model deepseek-v3.2
uv run editor-assistant batch ./papers/ --ext .html --task outline --save-files
```

#### 转换和清理输入

```bash
uv run editor-assistant convert document.pdf
uv run editor-assistant convert *.docx
uv run editor-assistant clean "https://example.com/page.html" -o clean.md
uv run editor-assistant clean page.html --stdout

uv run any2md *.docx -o converted/
```

#### 查看历史和统计

```bash
uv run editor-assistant history
uv run editor-assistant history -n 50
uv run editor-assistant history --search "arxiv"
uv run editor-assistant stats
uv run editor-assistant stats -d 30
uv run editor-assistant show 1
uv run editor-assistant show 1 --output
```

#### 恢复和导出

```bash
uv run editor-assistant resume --dry-run
uv run editor-assistant resume --save-files
uv run editor-assistant export history.json
uv run editor-assistant export history.csv --limit 100
```

### 常用选项

以下选项适用于 `brief`、`outline`、`translate`、`process`、`batch` 等生成命令：

- `--model`：选择 LLM 模型。默认值：`glm-4.7-or`。
- `--thinking`：支持的 Gemini 模型推理强度，可选 `low`、`medium`、`high`。
- `--no-stream`：关闭流式输出。
- `--save-files`：把生成的 Markdown 文件和 token 报告写入磁盘。无论是否启用，SQLite 数据库都会更新。
- `--debug`：启用详细调试日志。

全局选项：

- `--version`：显示版本。
- `--help`：显示帮助。使用子命令帮助，例如 `uv run editor-assistant brief --help`，可以查看当前模型选择列表。

### 支持的模型

模型名称来自 `llm-exec-core` 包内的 `llm_exec_core/llm_config.yml`。本仓库中的 `src/editor_assistant/config/llm_models.py` 只是兼容层，会转发到 core catalog loader；可用 `uv run editor-assistant brief --help` 查看最新 `--model` 选项。

当前默认模型：`glm-4.7-or`。

#### DeepSeek

- 火山引擎 (`DEEPSEEK_API_KEY_VOLC`)：`deepseek-v3.2`、`deepseek-r1`
- 官方 API (`DEEPSEEK_API_KEY`)：`deepseek-v4-flash`、`deepseek-v4-pro`

#### Gemini

- 付费 key (`GEMINI_API_KEY`)：`gemini-3-flash`、`gemini-3.1-flash-lite`、`gemini-3.1-pro`
- 免费层 key (`GEMINI_FT_API_KEY`)：`gemini-2.5-flash-free`、`gemini-2.5-flash-lite-free`、`gemini-3-flash-free`、`gemini-3.1-flash-lite-free`

#### Qwen

- `qwen-turbo`、`qwen-plus`、`qwen3.5-plus`、`qwen3-max-preview`、`qwen3-max`

#### GLM / 智谱

- 智谱 API (`ZHIPU_API_KEY`)：`glm-4.5`、`glm-4.6`、`glm-4.7`、`glm-5`、`glm-5.1`
- OpenRouter (`ZHIPU_API_KEY_OPENROUTER`)：`glm-4.5-or`、`glm-4.6-or`、`glm-4.7-or`、`glm-5-or`、`glm-5.1-or`、`glm-5-turbo-or`

#### Doubao

- `doubao-seed-1.6`

#### OpenAI via OpenRouter

- `gpt-4o-or`、`gpt-4.1-or`、`gpt-5-or`、`gpt-5.2-or`、`gpt-5.4-or`、`gpt-5.5-or`

#### Anthropic via OpenRouter

- `claude-sonnet-4-or`、`claude-opus-4.6-or`、`claude-sonnet-4.6-or`、`claude-opus-4.7-or`、`claude-haiku-4.5-or`

### Python API

```python
import asyncio

from editor_assistant.data_models import Input, InputType, ProcessType
from editor_assistant.main import EditorAssistant


async def main():
    assistant = EditorAssistant("glm-4.7-or", debug_mode=True)

    await assistant.process_multiple(
        [Input(type=InputType.PAPER, path="paper.pdf")],
        ProcessType.OUTLINE,
    )

    await assistant.process_multiple(
        [Input(type=InputType.PAPER, path="paper.pdf")],
        ProcessType.BRIEF,
    )


if __name__ == "__main__":
    asyncio.run(main())
```

### 支持的输入格式

转换功能基于 MarkItDown 和本项目的 HTML 提取工具，支持常见文档和网页格式：

- 文档：PDF、DOCX、DOC、PPTX、PPT、XLSX、XLS、EPUB
- 网页内容：HTML 文件和 URL
- 文本/数据：TXT、MD、CSV、JSON、XML、ZIP
- MarkItDown extras 支持的图片、音频等媒体格式也可能可用

### 输出和存储

- 运行历史、输入、输出和 token 用量会保存到 SQLite。
- 默认数据库：`~/.editor_assistant/runs.db`
- 自定义数据库目录：`EDITOR_ASSISTANT_DB_DIR=/path/to/dir`
- 使用 `--save-files` 时，生成文件会写到输入/转换后的 Markdown 旁边的 `llm_summaries/<model>/`。

```text
llm_summaries/
└── <model>/
    ├── response_<title><task_suffix>_<model>_<timestamp>.md
    ├── response_bilingual_<title>_translate_<model>_<timestamp>.md  # 仅 translate
    └── token_usage_<title><task_suffix>_<model>_<timestamp>.txt
```

### 开发工作流

```bash
uv sync
uv run pytest tests/unit/
uv run flake8 src/
uv run mypy src/
uv run black src/ tests/
```

架构细节见 `DEVELOPER_GUIDE.md`，设计记录和报告见 `docs/design_docs/`、`docs/decisions/`、`docs/reports/`。

### 迁移说明

当前 CLI 约定：

- 源码目录中建议使用 `uv run ...`。
- `brief` 和 `process` 使用 `paper=...` 或 `news=...` 这类带类型输入；传入多个输入时会逐个独立处理。
- `outline` 和 `translate` 接收单个普通路径或 URL。
- 生成结果默认写入 SQLite；文件输出需要显式加 `--save-files`。
- 默认模型为 `glm-4.7-or`。

旧版 v0.1 的 `--article paper:paper.pdf` 语法已经不再支持。

### 许可证

本项目使用 MIT License。

### 致谢

- Microsoft MarkItDown 提供文档转换能力
- Readabilipy 和 Trafilatura 提供网页内容提取
- DeepSeek、Google Gemini、Qwen、GLM/智谱、Doubao、OpenAI、Anthropic、OpenRouter 提供 LLM 能力
