# Editor Assistant

[English](#english) | [中文](#chinese)

## English

A powerful AI-powered Python tool for automatically converting, processing, and generating content from research papers, news articles, PDFs, and web pages using Large Language Models (LLMs). The system provides intelligent content processing with specialized workflows for research summaries and news generation.

### 🚀 Features

- **Unified CLI Interface**: Professional command-line tool with subcommands (`editor-assistant news`, `editor-assistant outline`)
- **Multi-format Content Conversion**: Converts PDFs, DOCs, web pages, and other formats to markdown
- **Intelligent Content Processing**: Single-context processing for documents up to 128k+ tokens
- **Dual Content Types**: 
  - **Research Outlines**: Detailed analysis and Chinese translation of research papers
  - **News Generation**: Convert research content into news articles for researcher audiences
- **Advanced Logging System**: Clean console output with optional debug mode and file logging
- **Comprehensive Analytics**: Token usage tracking, cost calculation, and processing time analysis
- **Multiple LLM Providers**: Supports Deepseek R1/V3 and Gemini models
- **Full Transparency**: Saves all prompts, responses, and processing reports

### 📋 Prerequisites

- Python 3.8+
- API keys for supported LLM providers:
  - **Deepseek**: `VOLC_API_KEY` environment variable (via Volcengine)
  - **Gemini**: `GEMINI_API_KEY` environment variable

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
export VOLC_API_KEY=your_volcengine_api_key

# For Gemini models
export GEMINI_API_KEY=your_gemini_api_key
```

Or create a `.env` file:

```env
VOLC_API_KEY=your_volcengine_api_key
GEMINI_API_KEY=your_gemini_api_key
```

## 🎯 Usage

### New Unified CLI Interface

**Generate News Articles:**

```bash
editor-assistant news "https://example.com/research-article"
editor-assistant news paper.pdf --model deepseek-r1-latest --debug
```

**Generate Research Outlines:**

```bash
editor-assistant outline "https://arxiv.org/paper.pdf"
editor-assistant outline paper.pdf --model deepseek-r1-latest
```

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

### Legacy Commands (Backward Compatible)

```bash
generate_news "https://example.com/article"    # Same as: editor-assistant news
generate_outline paper.pdf                     # Same as: editor-assistant outline
any2md document.pdf                           # Same as: editor-assistant convert  
html2md page.html                             # Same as: editor-assistant clean
```

### Global Options

- `--model`: Choose LLM model (default: deepseek-r1-latest)
- `--debug`: Enable detailed debug logging with file output
- `--version`: Show version information

### Python API

```python
from editor_assistant.main import EditorAssistant
from editor_assistant.md_processesor import ArticleType

# Initialize with your preferred model
assistant = EditorAssistant("deepseek-r1-latest", debug_mode=True)

# Generate research outlines with Chinese translation
assistant.summarize_multiple(
    ["path/to/paper1.pdf", "path/to/paper2.md"], 
    ArticleType.research
)

# Generate news articles
assistant.summarize_multiple(
    ["https://example.com/article", "path/to/article.md"], 
    ArticleType.news
)
```

### 🤖 Supported Models

#### Deepseek Models (via Volcengine)

- `deepseek-r1` - Advanced reasoning model
- `deepseek-r1-latest` - Latest reasoning model (recommended)
- `deepseek-v3` - General-purpose model
- `deepseek-v3-latest` - Latest general model

#### Gemini Models

- `gemini-2.5-flash-lite` - Fast, lightweight model
- `gemini-2.5-flash` - Balanced performance model
- `gemini-2.5-pro` - High-performance model

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
│   ├── r/  (research) or n/ (news)
│   │   ├── prompts/
│   │   │   ├── analysis.md
│   │   │   └── translation.md  (research only)
│   │   ├── responses/
│   │   │   ├── analysis.md
│   │   │   └── translation.md  (research only)
│   │   ├── process_times/
│   │   │   ├── process_times.json
│   │   │   └── process_times.txt
│   │   └── token_usage/
│   │       ├── token_usage.json
│   │       └── token_usage.txt
```

### 🔍 Content Processing Workflow

#### Research Papers (Outline Generation)
1. **Content Conversion**: Convert input to clean markdown
2. **Research Analysis**: Generate comprehensive outline with methodology, findings, and significance
3. **Chinese Translation**: Translate the outline to Chinese
4. **Reporting**: Generate token usage and processing time reports

#### News Generation
1. **Content Conversion**: Convert input to clean markdown
2. **News Generation**: Create 400-word news articles tailored for researcher audiences
3. **Scientific Focus**: Emphasize methodology, data, and research significance
4. **Reporting**: Generate processing analytics

### 📈 Analytics & Monitoring

- **Clean Console Output**: Professional logging with colored symbols (•, ⚠, ✗)
- **Token Usage Tracking**: Concise summary with detailed file reports
- **Cost Calculation**: Automatic cost calculation in Chinese Yuan (¥)
- **Processing Time Analysis**: Total time and step-by-step breakdown
- **Debug Mode**: Comprehensive file logging when `--debug` flag is used

### 🔧 Advanced Features

#### User-Customizable Configuration
All user-editable files are stored outside the source code in `~/.editor_assistant/`:

```bash
# Show configuration location and available options
editor-assistant config show

# Initialize user configuration (done automatically on first run)
editor-assistant config init

# View available models
editor-assistant config models
```

**Configuration Structure:**
```text
~/.editor_assistant/
├── user_prompts/               # Customizable prompt templates
│   ├── news_generator.txt      # Edit to customize news generation
│   ├── research_outliner.txt   # Edit to customize research outlines
│   └── translator.txt          # Edit to customize translation
└── user_llm_config.yml         # Add custom models and providers
```

#### Customizable Prompt Templates
Prompts are stored as `.txt` files for easy editing:

```bash
# Edit news generation prompt
nano ~/.editor_assistant/user_prompts/news_generator.txt

# Edit research outline prompt  
nano ~/.editor_assistant/user_prompts/research_outliner.txt

# Changes take effect immediately
```

**Benefits:**
- **No source code modification**: Safe customization without breaking the system
- **Jinja2 templating**: Support for variables and logic in prompts
- **Immediate effect**: Changes apply to next generation without restart
- **Version control friendly**: Keep your custom prompts in git

#### Add Custom Models
Easily add new LLM models and providers:

```bash
# Add a custom OpenAI model
editor-assistant config add-model \
  --provider openai \
  --model-name gpt-4-custom \
  --model-id gpt-4-0125-preview \
  --input-price 30.0 \
  --output-price 60.0 \
  --max-tokens 4000 \
  --context-window 128000

# Add a custom local model
editor-assistant config add-model \
  --provider ollama \
  --model-name llama3-local \
  --model-id llama3:70b \
  --input-price 0.0 \
  --output-price 0.0
```

**Model Configuration Example:**
```yaml
# ~/.editor_assistant/user_llm_config.yml
openai:
  api_key_env_var: "OPENAI_API_KEY"
  api_base_url: "https://api.openai.com/v1/chat/completions"
  temperature: 0.5
  max_tokens: 4000
  context_window: 128000
  models:
    gpt-4-custom:
      id: "gpt-4-0125-preview"
      pricing: { input: 30.0, output: 60.0 }
```

#### Centralized Logging System
```bash
# Normal mode: Clean console output
editor-assistant news paper.pdf

# Debug mode: Detailed logging to files
editor-assistant news paper.pdf --debug
# Creates logs/editor_assistant_TIMESTAMP.log
```

#### Scientific News Generation
The news generation is specifically designed for researcher audiences:
- Preserves technical details and methodology
- Emphasizes scientific significance
- Includes proper citations and publication information
- Maintains academic rigor while improving readability

#### Professional CLI Design
- Git-like subcommand structure
- Consistent argument patterns
- Comprehensive help system
- Backward compatibility with old commands

### 🛡️ Error Handling

- **Robust Processing**: Continues even if individual documents fail
- **Content Size Validation**: Checks content against model context windows
- **Graceful Degradation**: Provides meaningful error messages
- **Process Time Safety**: Prevents division by zero errors in reporting

### 🔧 Configuration Files

The system uses YAML configuration for model settings:

```yaml
# config/llm_config.yml
deepseek:
  api_key_env_var: "VOLC_API_KEY"
  api_base_url: "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
  temperature: 0.5
  max_tokens: 16000
  context_window: 128000
  models:
    deepseek-r1-latest:
      id: "deepseek-r1-250528"
      pricing: { input: 4.00, output: 16.00 }
```

### 📚 Documentation

- [`docs/cli_usage.md`](docs/cli_usage.md) - Comprehensive CLI usage guide
- [`docs/argparse_and_cli_reference.md`](docs/argparse_and_cli_reference.md) - CLI architecture reference
- [`docs/logging_system_manual.md`](docs/logging_system_manual.md) - Logging system documentation
- [`docs/python_logging_basics.md`](docs/python_logging_basics.md) - Python logging fundamentals

### 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### 🙏 Acknowledgments

- **Microsoft MarkItDown** for document conversion capabilities
- **Readabilipy** and **Trafilatura** for web content extraction
- **Deepseek** and **Google Gemini** for LLM capabilities

### 📞 Support

For support, please open an issue on GitHub or contact the maintainers.

---

**Note**: This tool is designed for research and educational purposes. Please ensure you have the necessary rights to process and summarize the content you're working with, and be mindful of API usage costs when processing large volumes of content.

---

## Chinese

### 编辑助手 (Editor Assistant)

一个强大的AI驱动的Python工具，使用大型语言模型（LLM）自动转换、处理和生成研究论文、新闻文章、PDF和网页内容。该系统为研究摘要和新闻生成提供智能内容处理和专门工作流程。

### 🚀 功能特色

- **统一CLI界面**：专业的命令行工具，带有子命令（`editor-assistant news`、`editor-assistant outline`）
- **多格式内容转换**：将PDF、DOC、网页和其他格式转换为markdown
- **智能内容处理**：支持高达128k+令牌的单一上下文文档处理
- **双重内容类型**：
  - **研究大纲**：研究论文的详细分析(提供中英双语版本)
  - **新闻生成**：将研究内容转换为面向研究人员受众的新闻文章
- **高级日志系统**：清洁的控制台输出，带有可选的调试模式和文件日志
- **全面分析**：令牌使用跟踪、成本计算和处理时间分析
- **多个LLM提供商**：支持Deepseek R1/V3和Gemini模型
- **完全透明**：保存所有提示、响应和处理报告

### 📋 依赖条件

- Python 3.8+
- 支持的LLM提供商的API密钥：
  - **Deepseek**：`DEEPSEEK_API_KEY`环境变量（通过火山引擎）
  - **Gemini**：`GEMINI_API_KEY`环境变量

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
```

### 🎯 使用方法

#### 统一CLI界面

**生成新闻文章：**

```bash
editor-assistant news "https://example.com/research-article"
editor-assistant news paper.pdf --model deepseek-r1-latest --debug
```

**生成研究大纲：**

```bash
editor-assistant outline "https://arxiv.org/paper.pdf"
editor-assistant outline paper.pdf --model deepseek-r1-latest
```

**转换文件为Markdown：**

```bash
editor-assistant convert document.pdf
editor-assistant convert *.docx -o converted/
```

**清理HTML为Markdown：**

```bash
editor-assistant clean "https://example.com/page.html" -o clean.md
editor-assistant clean page.html --stdout
```

#### 传统命令（向后兼容）

```bash
generate_news "https://example.com/article"    # 等同于：editor-assistant news
generate_outline paper.pdf                     # 等同于：editor-assistant outline
any2md document.pdf                           # 等同于：editor-assistant convert  
html2md page.html                             # 等同于：editor-assistant clean
```

### 🤖 支持的模型

#### Deepseek模型（通过火山引擎）
- `deepseek-r1` - 高级推理模型
- `deepseek-r1-latest` - 最新推理模型（推荐）
- `deepseek-v3` - 通用模型
- `deepseek-v3-latest` - 最新通用模型

#### Gemini模型
- `gemini-2.5-flash-lite` - 快速、轻量级模型
- `gemini-2.5-flash` - 平衡性能模型
- `gemini-2.5-pro` - 高性能模型

### 🔍 内容处理工作流程

#### 研究论文（大纲生成）
1. **内容转换**：将输入转换为清洁的markdown
2. **研究分析**：生成包含方法论、发现和意义的综合大纲
3. **中文翻译**：将大纲翻译成中文
4. **报告**：生成令牌使用和处理时间报告

#### 新闻生成
1. **内容转换**：将输入转换为清洁的markdown
2. **新闻生成**：创建面向研究人员受众的400字新闻文章
3. **科学重点**：强调方法论、数据和研究意义
4. **报告**：生成处理分析

### 📈 分析与监控

- **清洁控制台输出**：带有彩色符号的专业日志记录（•、⚠、✗）
- **令牌使用跟踪**：简洁摘要与详细文件报告
- **成本计算**：自动计算人民币（¥）成本
- **处理时间分析**：总时间和逐步分解
- **调试模式**：使用`--debug`标志时的综合文件日志记录

### 🔧 高级功能

#### 集中化日志系统
```bash
# 普通模式：清洁控制台输出
editor-assistant news paper.pdf

# 调试模式：详细的文件日志记录
editor-assistant news paper.pdf --debug
# 创建logs/editor_assistant_TIMESTAMP.log
```

#### 科学新闻生成
新闻生成专门为研究人员受众设计：
- 保留技术细节和方法论
- 强调科学意义
- 包含适当的引用和发表信息
- 在提高可读性的同时保持学术严谨性

### 📚 文档

- [`docs/cli_usage.md`](docs/cli_usage.md) - 综合CLI使用指南
- [`docs/logging_system_manual.md`](docs/logging_system_manual.md) - 日志系统文档
- [`docs/python_logging_basics.md`](docs/python_logging_basics.md) - Python日志基础

### 📝 许可证

该项目根据MIT许可证授权 - 有关详细信息，请参阅[LICENSE](LICENSE)文件。

### 🙏 致谢

- **Microsoft MarkItDown** 提供文档转换功能
- **Readabilipy** 和 **Trafilatura** 提供网页内容提取
- **Deepseek** 和 **Google Gemini** 提供LLM功能

---

**注意**：该工具专为研究和教育目的而设计。请确保您有必要的权利来处理和总结您正在使用的内容，并在处理大量内容时注意API使用成本。