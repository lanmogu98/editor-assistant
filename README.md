# Editor Assistant

[English](#english) | [中文](#chinese)

## English

A simple AI-powered Python CLI tool for processing research papers and generating content using Large Language Models (LLMs). Designed for personal research workflow automation.

**Version: 0.2** | [See Breaking Changes](#-breaking-changes-in-v02)

### 🚀 Features

- **Simple CLI Interface**: Command-line tool with 5 main commands
- **Multi-format Input**: Processes PDFs, DOCs, web pages, URLs, and markdown files
- **Three Content Types**:
  - **Brief News**: Convert research papers into short news articles
  - **Research Outlines**: Generate detailed outlines with Chinese translation
  - **Translation**: Standalone Chinese translation with bilingual output
- **Multiple LLM Support**: Works with Deepseek, Gemini, and other providers
- **Debug Logging**: Optional detailed logging for troubleshooting

### 📋 Prerequisites

- Python 3.8+
- API keys for supported LLM providers:
  - **Deepseek**: `DEEPSEEK_API_KEY` environment variable (via Volcengine)
  - **Gemini**: `GEMINI_API_KEY` environment variable
  - **Kimi**: `KIMI_API_KEY` environment variable (via Volcengine)
  - **Doubao**: `DOUBAO_API_KEY` environment variable (via Volcengine)
  - **Qwen**: `QWEN_API_KEY` environment variable (via Alibaba Cloud)
  - **GLM**: `ZHIPU_API_KEY` environment variable (via Zhipu AI)
  - **GLM (OpenRouter)**: `ZHIPU_API_KEY_OPENROUTER` environment variable (via OpenRouter)
  - **OpenAI (OpenRouter)**: `OPENAI_API_KEY` environment variable (via OpenRouter)
  - **Anthropic (OpenRouter)**: `ANTHROPIC_API_KEY` environment variable (via OpenRouter)

## 🛠️ Installation

### From Source

```bash
git clone https://github.com/yourusername/editor_assistant.git
cd editor_assistant
pip install -e .
```

### Dependencies

The package automatically installs these dependencies:

- `markitdown` - Microsoft's document conversion library
- `requests` - HTTP library for API calls
- `pydantic` - Data validation and settings management
- `trafilatura` - Web content extraction
- `readabilipy` - Clean HTML content extraction
- `html2text` - HTML to markdown conversion
- `pyyaml` - YAML configuration parsing
- `jinja2` - Template rendering for prompts

## 🔧 Configuration

Set up your API keys:

```bash
# For Deepseek models (via Volcengine)
export DEEPSEEK_API_KEY=your_volcengine_api_key

# For Gemini models
export GEMINI_API_KEY=your_gemini_api_key

# For Kimi models (via Volcengine)
export KIMI_API_KEY=your_kimi_api_key

# For Doubao models (via Volcengine)
export DOUBAO_API_KEY=your_doubao_api_key

# For Qwen models (via Alibaba Cloud)
export QWEN_API_KEY=your_qwen_api_key

# For GLM models (via Zhipu AI)
export ZHIPU_API_KEY=your_zhipu_api_key

# For GLM models (via OpenRouter)
export ZHIPU_API_KEY_OPENROUTER=your_openrouter_api_key

# For OpenAI models (via OpenRouter)
export OPENAI_API_KEY=your_openrouter_api_key

# For Anthropic models (via OpenRouter)
export ANTHROPIC_API_KEY=your_openrouter_api_key
```

Or create a `.env` file:

```env
DEEPSEEK_API_KEY=your_volcengine_api_key
GEMINI_API_KEY=your_gemini_api_key
KIMI_API_KEY=your_kimi_api_key
DOUBAO_API_KEY=your_doubao_api_key
QWEN_API_KEY=your_qwen_api_key
ZHIPU_API_KEY=your_zhipu_api_key
ZHIPU_API_KEY_OPENROUTER=your_openrouter_api_key
OPENAI_API_KEY=your_openrouter_api_key
ANTHROPIC_API_KEY=your_openrouter_api_key
```

## 🎯 Usage

### Unified CLI Interface

**Generate Brief News (multi-source supported):**

```bash
editor-assistant brief paper=https://example.com/research-article
editor-assistant brief paper=paper.pdf news=https://example.com/related-news news=context.md --model deepseek-r1 --debug
```

**Generate Research Outlines (single source):**

```bash
editor-assistant outline https://arxiv.org/paper.pdf
editor-assistant outline paper.pdf --model deepseek-r1
```

**Generate Chinese Translations with Bilingual Output (single source):**

```bash
editor-assistant translate https://arxiv.org/paper.pdf
editor-assistant translate document.pdf --model gemini-2.5-pro
editor-assistant translate research.md --model deepseek-r1 --debug
```

*Note: Translation generates both Chinese-only and bilingual side-by-side versions*

**Convert Files to Markdown:**

```bash
editor-assistant convert document.pdf
editor-assistant convert *.docx -o converted/
```

**Clean HTML to Markdown:**

```bash
editor-assistant clean "https://example.com/page.html" -o clean.md
editor-assistant clean page.html --stdout
```

**Multi-task Processing (serial execution):**

```bash
editor-assistant process paper=paper.pdf --tasks "brief,outline"
editor-assistant process paper=paper.pdf news=news.md --tasks "brief,outline,translate"
```

### Global Options

- `--model`: Choose LLM model (default: deepseek-v3.2)
- `--thinking`: Reasoning level for Gemini 3+ models (`low`, `medium`, `high`). Default: model decides dynamically
- `--no-stream`: Disable streaming output (default: streaming enabled)
- `--debug`: Enable detailed debug logging with file output
- `--version`: Show version information

### Python API

```python
from editor_assistant.main import EditorAssistant
from editor_assistant.data_models import ProcessType, InputType, Input

# Initialize with your preferred model
assistant = EditorAssistant("deepseek-r1", debug_mode=True)

# Generate research outline (single paper)
assistant.process_multiple(
    [Input(type=InputType.PAPER, path="path/to/paper.pdf")],
    ProcessType.OUTLINE
)

# Generate multi-source brief (paper + news)
assistant.process_multiple(
    [
        Input(type=InputType.PAPER, path="paper.pdf"),
        Input(type=InputType.NEWS, path="https://example.com/news"),
        Input(type=InputType.NEWS, path="context.md"),
    ],
    ProcessType.BRIEF
)
```

### 🤖 Supported Models

#### Deepseek Models (via Volcengine)

- `deepseek-v3.2` - Latest general-purpose model (2025 release)
- `deepseek-r1` - Advanced reasoning model

#### Gemini Models

- `gemini-3-flash` - Balanced performance model
- `gemini-3-pro` - High-performance model

#### Kimi Models (via Volcengine)

- `kimi-k2` - Advanced reasoning model

#### Doubao Models (via Volcengine)

- `doubao-seed-1.6` - Advanced language model with 256k context window

#### Qwen Models (via Alibaba Cloud)

- `qwen-plus` - General-purpose model with thinking capabilities
- `qwen3-max` - Latest general model with enhanced reasoning
- `qwen3-max-preview` - Preview version of Qwen3-Max

#### GLM Models

- `glm-4.5` - High-performance model (via Zhipu AI)
- `glm-4.6` - High-performance model (via Zhipu AI)
- `glm-4.5-or` - High-performance model (via OpenRouter)
- `glm-4.6-or` - Latest model (via OpenRouter)

#### OpenAI Models (via OpenRouter)

- `gpt-4o-or` - GPT-4 Omni model with vision capabilities
- `gpt-4.1-or` - Latest GPT-4 Turbo model
- `gpt-5-or` - Next-generation GPT-5 model

#### Anthropic Models (via OpenRouter)

- `claude-sonnet-4-or` - Latest Claude Sonnet 4 model with 200k context

### 📁 Supported Input Formats

- **Documents**: PDF, DOCX, DOC, PPTX, PPT, XLSX, XLS, EPUB
- **Web Content**: HTML pages, URLs
- **Media**: JPG, PNG, GIF, MP3, WAV, M4A
- **Data**: CSV, JSON, XML, TXT, MD, ZIP

### 📊 Output Structure

The tool creates organized output for each processed document:

```text
llm_summaries/
├── document_name_model_name/
│   ├── prompts/
│   │   ├── document_name_brief.md
│   │   ├── document_name_outline.md
│   │   └── document_name_translate.md
│   ├── responses/
│   │   ├── document_name_brief.md
│   │   ├── document_name_outline.md
│   │   ├── document_name_translate_model.md
│   │   └── bilingual_document_name_translate_model.md  # Bilingual side-by-side
│   └── token_usage/
│       ├── token_usage.json
│       └── token_usage.txt
```

### ⚠️ Breaking Changes in v0.2

**Important**: Version 0.2 introduces breaking changes. Please review before upgrading.

#### CLI Syntax Changes

**Old syntax (v0.1):**
```bash
editor-assistant brief --article paper:paper.pdf --article news:article.md
editor-assistant outline --article paper:research.pdf
```

**New syntax (v0.2):**
```bash
editor-assistant brief paper=paper.pdf news=article.md
editor-assistant outline research.pdf
```

**Why the change?** The new syntax is cleaner, more intuitive, and follows common CLI conventions like `key=value` pairs used in tools like `git` and `docker`.

#### Model Name Changes

Several model names have been updated or removed:

| Old Name (v0.1) | New Name (v0.2) | Status |
|----------------|----------------|--------|
| `deepseek-r1-latest` | `deepseek-r1` | ✅ Use `deepseek-r1` |
| `deepseek-v3-latest` | `deepseek-v3` | ✅ Use `deepseek-v3` |
| `qwen-plus-latest` | `qwen3-max` or `qwen3-max-preview` | ✅ Use `qwen3-max` |
| `gemini-2.5-flash-lite` | Removed | ❌ Use `gemini-2.5-flash` instead |
| `glm-4.5-openrouter` | `glm-4.5-or` | ✅ Renamed for consistency |

**New additions:**
- `deepseek-v3.2` - Native Deepseek API support
- `gpt-4o-or`, `gpt-4.1-or`, `gpt-5-or` - OpenAI models via OpenRouter
- `claude-sonnet-4-or` - Anthropic Claude via OpenRouter

#### Default Model Change

- **Old default**: `glm-4.5-or`
- **New default**: `glm-4.6-or`

**Why?** Better balance of performance, cost, and reliability across different use cases.

#### Migration Guide

1. **Update CLI commands**: Replace `--article type:path` with `type=path`
2. **Update model names**: Check the table above and update your scripts
3. **Set new environment variables** (if using new providers):
   ```bash
   export OPENAI_API_KEY=your_openrouter_key
   export ANTHROPIC_API_KEY=your_openrouter_key
   ```
4. **Test your workflow** with `--debug` flag to verify everything works

### 🛡️ Error Handling

- **Robust Processing**: Continues even if individual documents fail
- **Content Size Validation**: Checks content against model context windows
- **Graceful Degradation**: Provides meaningful error messages
- **Process Time Safety**: Prevents division by zero errors in reporting

### 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### 🙏 Acknowledgments

- **Microsoft MarkItDown** for document conversion capabilities
- **Readabilipy** and **Trafilatura** for web content extraction
- **Deepseek**, **Google Gemini**, **Qwen**, **GLM**, **Kimi**, **Doubao** for LLM capabilities

### 📞 Support

For support, please open an issue on GitHub or contact the maintainers.

---

**Note**: This tool is designed for research and educational purposes. Please ensure you have the necessary rights to process and summarize the content you're working with, and be mindful of API usage costs when processing large volumes of content.

---

## Chinese

### 编辑助手 (Editor Assistant)

一个简单的AI驱动的Python命令行工具，用于处理研究论文并使用大型语言模型（LLM）生成内容。专为个人研究工作流程自动化设计。

### 🚀 功能特色

- **简单CLI界面**：包含5个主要命令的命令行工具
- **多格式输入**：处理PDF、DOC、网页、URL和markdown文件
- **三种内容类型**：
  - **简讯**：将研究论文转换为短新闻文章
  - **研究大纲**：生成详细大纲并提供中文翻译
  - **翻译**：独立的中文翻译，支持双语输出
- **多LLM支持**：兼容Deepseek、Gemini等提供商
- **调试日志**：可选的详细日志记录用于故障排除

### 📋 依赖条件

- Python 3.8+
- 支持的LLM提供商的API密钥：
  - **Deepseek**：`DEEPSEEK_API_KEY`环境变量（通过火山引擎）
  - **Gemini**：`GEMINI_API_KEY`环境变量
  - **Kimi**：`KIMI_API_KEY`环境变量（通过火山引擎）
  - **Doubao**：`DOUBAO_API_KEY`环境变量（通过火山引擎）
  - **Qwen**：`QWEN_API_KEY`环境变量（通过阿里云）
  - **GLM**：`ZHIPU_API_KEY`环境变量（通过智谱AI）
  - **GLM (OpenRouter)**：`ZHIPU_API_KEY_OPENROUTER`环境变量（通过OpenRouter）
  - **OpenAI (OpenRouter)**：`OPENAI_API_KEY`环境变量（通过OpenRouter）
  - **Anthropic (OpenRouter)**：`ANTHROPIC_API_KEY`环境变量（通过OpenRouter）

### 🛠️ 安装

#### 从源码安装

```bash
git clone https://github.com/yourusername/editor_assistant.git
cd editor_assistant
pip install -e .
```

### 🔧 配置

设置您的API密钥：

```bash
# 对于Deepseek模型（通过火山引擎）
export DEEPSEEK_API_KEY=your_volcengine_api_key

# 对于Gemini模型
export GEMINI_API_KEY=your_gemini_api_key

# 对于Kimi模型（通过火山引擎）
export KIMI_API_KEY=your_kimi_api_key

# 对于Doubao模型（通过火山引擎）
export DOUBAO_API_KEY=your_doubao_api_key
```

### 🎯 使用方法

#### 统一CLI界面

**生成简讯（支持多来源）：**

```bash
editor-assistant brief paper=https://example.com/research-article
editor-assistant brief \
  paper=paper.pdf \
  news=https://example.com/related-news \
  news=context.md \
  --model deepseek-r1 --debug
```

**生成研究大纲（仅单来源，paper）：**

```bash
editor-assistant outline https://arxiv.org/paper.pdf
editor-assistant outline paper.pdf --model deepseek-r1
```

**生成双语对照中文翻译（仅单来源，paper）：**

```bash
editor-assistant translate https://arxiv.org/paper.pdf
editor-assistant translate document.pdf --model gemini-2.5-pro
editor-assistant translate research.md --model deepseek-r1 --debug
```

*注意：翻译功能同时生成纯中文版本和双语对照版本*

**转换文件为Markdown：**

```bash
editor-assistant convert document.pdf
editor-assistant convert *.docx -o converted/
```

**将HTML转换为格式干净的Markdown：**

```bash
editor-assistant clean "https://example.com/page.html" -o clean.md
editor-assistant clean page.html --stdout
```


### 🤖 支持的模型

#### 由火山引擎提供

##### Deepseek模型
- `deepseek-v3.1` - 最新混合通用模型（2025年发布）
- `deepseek-r1` - 推理模型
- `deepseek-v3` - 基础模型

##### Doubao模型
- `doubao-seed-1.6` - 高级语言模型，支持256k上下文窗口

##### Kimi模型
- `kimi-k2` - 高级推理模型

#### 由阿里云提供

##### Qwen模型（阿里云）
- `qwen-plus` - 具有思考能力的通用模型
- `qwen3-max` - 最新的增强推理通用模型
- `qwen3-max-preview` - Qwen3-Max预览版

#### 由谷歌云提供

##### Gemini模型 （google cloud）
- `gemini-2.5-flash` - 平衡性能模型
- `gemini-2.5-pro` - 高性能模型

#### 由智谱提供

##### GLM模型
- `glm-4.5` - 高性能模型（智谱AI）
- `glm-4.6` - 最新模型（智谱AI）

#### 由openrouter提供

##### GLM模型
- `glm-4.5-or` - 高性能模型（智谱，通过OpenRouter）
- `glm-4.6-or` - 最新模型（智谱，通过OpenRouter）

##### OpenAI模型
- `gpt-4o-or` - GPT-4 Omni模型，支持视觉功能
- `gpt-4.1-or` - 最新GPT-4 Turbo模型
- `gpt-5-or` - 下一代GPT-5模型

##### Anthropic模型
- `claude-sonnet-4-or` - Claude Sonnet 4模型，支持200k上下文





### 📝 许可证

该项目根据MIT许可证授权 - 有关详细信息，请参阅[LICENSE](LICENSE)文件。

### 🙏 致谢

- **Microsoft MarkItDown** 提供文档转换功能
- **Readabilipy** 和 **Trafilatura** 提供网页内容提取
- **Deepseek**, **Google Gemini**, **Qwen**, **GLM**, **Kimi**, **Doubao** 提供LLM功能

---

**注意**：该工具专为研究和教育目的而设计。请确保您有必要的权利来处理和总结您正在使用的内容，并在处理大量内容时注意API使用成本。
