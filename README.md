# Editor Assistant

[English](#english) | [中文](#chinese)

## English

A powerful Python tool for automatically converting, processing, and summarizing various types of content (research papers, news articles, PDFs, web pages) using Large Language Models (LLMs). The system intelligently processes content through chunking, LLM analysis, synthesis, and translation workflows.

### 🚀 Features

- **Multi-format Content Conversion**: Converts PDFs, DOCs, web pages, and other formats to markdown
- **Intelligent Content Chunking**: Splits large documents while preserving paragraph integrity and context
- **LLM-Powered Summarization**: Processes content with state-of-the-art language models
- **Dual Content Types**: Specialized workflows for research papers and news articles
- **Bilingual Output**: Automatically translates summaries to Chinese
- **Comprehensive Analytics**: Tracks token usage, costs, and processing times
- **Full Transparency**: Saves all prompts, responses, and intermediate results
- **Multiple LLM Providers**: Supports Deepseek and Gemini models

### 📋 Prerequisites

- Python 3.8+
- API keys for supported LLM providers:
  - **Deepseek**: `VOLC_API_KEY` environment variable
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
- `python-dotenv` - Environment variable management

## 🔧 Configuration

Set up your API keys (highly recommended):

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

### Command Line Interface

**Summarize Research Papers:**

```bash
summarize_research path/to/paper.pdf --model deepseek-r1-latest
summarize_research path/to/paper.md path/to/another.pdf --model deepseek-v3-latest
```

**Summarize News Articles:**

```bash
summarize_news path/to/article.md --model deepseek-v3-latest
summarize_news https://example.com/news-article --model gemini-2.5-flash
```

**Convert Documents to Markdown:**

```bash
any2md path/to/document.pdf -o output_directory/
html2md https://example.com/webpage.html -o webpage.md
```

#### Python API

```python
from editor_assistant.main import EditorAssistant
from editor_assistant.md_summarizer import ArticleType

# Initialize with your preferred model
assistant = EditorAssistant("deepseek-r1-latest")

# Summarize research papers
assistant.summarize_multiple(
    ["path/to/paper1.pdf", "path/to/paper2.md"], 
    ArticleType.research
)

# Summarize news articles
assistant.summarize_multiple(
    ["https://example.com/article", "path/to/article.md"], 
    ArticleType.news
)
```

#### Individual Components

```python
# Content conversion only
from editor_assistant.md_converter import MarkdownConverter

converter = MarkdownConverter()
md_article = converter.convert_content("path/to/document.pdf")
print(md_article.markdown_content)

# Summarization only (for existing markdown)
from editor_assistant.md_summarizer import MDSummarizer, ArticleType

summarizer = MDSummarizer("deepseek-v3-latest")
success = summarizer.summarize_md("path/to/content.md", ArticleType.research)
```

### 🤖 Supported Models

#### Deepseek Models (via Volcengine)

- `deepseek-r1` - Reasoning-focused model
- `deepseek-r1-latest` - Latest reasoning model
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

The tool creates a comprehensive directory structure for each processed document:

```text
llm_summaries/
├── document_name_model_name/
│   ├── chunks/
│   │   ├── chunk_1.md
│   │   └── chunk_2.md
│   ├── prompts/
│   │   ├── chunk_analysis_1.md
│   │   ├── chunk_analysis_2.md
│   │   ├── synthesis.md
│   │   └── translation.md
│   ├── responses/
│   │   ├── chunk_analysis_1.md
│   │   ├── chunk_analysis_2.md
│   │   ├── synthesis.md
│   │   └── translation.md
│   ├── process_times/
│   │   ├── process_times.json
│   │   └── process_times.txt
│   └── token_usage/
│       ├── token_usage.json
│       └── token_usage.txt
```

### 🔍 Content Processing Workflow

1. **Content Conversion**: Converts input files/URLs to clean markdown
2. **Intelligent Chunking**: Splits content into manageable chunks (~2000 tokens each)
3. **Chunk Analysis**: Each chunk is analyzed by the LLM with context from previous chunks
4. **Synthesis**: Multiple chunk analyses are combined into a comprehensive summary
5. **Translation**: The final summary is translated to Chinese
6. **Reporting**: Generates detailed reports on token usage, costs, and processing times

### 📈 Analytics & Monitoring

- **Token Usage Tracking**: Input/output tokens per request
- **Cost Calculation**: Automatic cost calculation based on model pricing
- **Processing Time Analysis**: Detailed timing for each processing step
- **Comprehensive Logging**: Full audit trail of all operations

### 🛡️ Error Handling

- **Retry Logic**: Automatic retry with exponential backoff for API failures
- **Format Fallbacks**: Multiple conversion methods for robust content extraction
- **Graceful Degradation**: Continues processing even if individual documents fail

### 🔧 Advanced Configuration

The system uses YAML configuration files for model settings:

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

一个强大的 Python 工具，用于自动转换、处理和总结各种类型的内容（研究论文、新闻文章、PDF、网页），使用大型语言模型（LLM）。系统通过分块、LLM 分析、综合和翻译工作流程智能地处理内容。

### 🚀 功能特色

- **多格式内容转换**：将 PDF、DOC、网页和其他格式转换为 markdown
- **智能内容分块**：在保持段落完整性和上下文的同时拆分大型文档
- **LLM 驱动的摘要**：使用最先进的语言模型处理内容
- **双重内容类型**：为研究论文和新闻文章提供专门的工作流程
- **双语输出**：自动将摘要翻译成中文
- **全面分析**：跟踪令牌使用情况、成本和处理时间
- **完全透明**：保存所有提示、响应和中间结果
- **多个 LLM 提供商**：支持 Deepseek 和 Gemini 模型

### 📋 依赖条件

- Python 3.8+
- 支持的 LLM 提供商的 API 密钥：
  - **Deepseek**：`VOLC_API_KEY` 环境变量
  - **Gemini**：`GEMINI_API_KEY` 环境变量

### 🛠️ 安装

#### 从源码安装

```bash
git clone https://github.com/yourusername/editor_assistant.git
cd editor_assistant
pip install -e .
```

#### 依赖项

该包会自动安装以下依赖项：

- `markitdown` - Microsoft 的文档转换库
- `requests` - 用于 API 调用的 HTTP 库
- `pydantic` - 数据验证和设置管理
- `trafilatura` - 网页内容提取
- `readabilipy` - 清洁 HTML 内容提取
- `html2text` - HTML 到 markdown 转换
- `pyyaml` - YAML 配置解析
- `python-dotenv` - 环境变量管理

### 🔧 配置 (Configuration)

设置您的 API 密钥（强烈推荐）：

```bash
# 对于 Deepseek 模型（通过火山引擎）
export VOLC_API_KEY=your_volcengine_api_key

# 对于 Gemini 模型
export GEMINI_API_KEY=your_gemini_api_key
```

或创建 `.env` 文件：

```env
VOLC_API_KEY=your_volcengine_api_key
GEMINI_API_KEY=your_gemini_api_key
```

### 🎯 使用方法

#### 命令行界面

**总结研究论文：**

```bash
summarize_research path/to/paper.pdf --model deepseek-r1-latest
summarize_research path/to/paper.md path/to/another.pdf --model deepseek-v3-latest
```

**总结新闻文章：**

```bash
summarize_news path/to/article.md --model deepseek-v3-latest
summarize_news https://example.com/news-article --model gemini-2.5-flash
```

**将文档转换为 Markdown：**

```bash
any2md path/to/document.pdf -o output_directory/
html2md https://example.com/webpage.html -o webpage.md
```

#### Python API

```python
from editor_assistant.main import EditorAssistant
from editor_assistant.md_summarizer import ArticleType

# 使用您首选的模型初始化
assistant = EditorAssistant("deepseek-r1-latest")

# 总结研究论文
assistant.summarize_multiple(
    ["path/to/paper1.pdf", "path/to/paper2.md"], 
    ArticleType.research
)

# 总结新闻文章
assistant.summarize_multiple(
    ["https://example.com/article", "path/to/article.md"], 
    ArticleType.news
)
```

#### 独立组件

```python
# 仅内容转换
from editor_assistant.md_converter import MarkdownConverter

converter = MarkdownConverter()
md_article = converter.convert_content("path/to/document.pdf")
print(md_article.markdown_content)

# 仅摘要（对于现有的 markdown）
from editor_assistant.md_summarizer import MDSummarizer, ArticleType

summarizer = MDSummarizer("deepseek-v3-latest")
success = summarizer.summarize_md("path/to/content.md", ArticleType.research)
```

### 🤖 支持的模型

#### Deepseek 模型（通过火山引擎）
- `deepseek-r1` - 推理导向模型
- `deepseek-r1-latest` - 最新推理模型
- `deepseek-v3` - 通用模型
- `deepseek-v3-latest` - 最新通用模型

#### Gemini 模型
- `gemini-2.5-flash-lite` - 快速、轻量级模型
- `gemini-2.5-flash` - 平衡性能模型
- `gemini-2.5-pro` - 高性能模型

### 📁 支持的输入格式

- **文档**：PDF、DOCX、DOC、PPTX、PPT、XLSX、XLS、EPUB
- **网页内容**：HTML 页面、URL
- **媒体**：JPG、PNG、GIF、MP3、WAV、M4A
- **数据**：CSV、JSON、XML、TXT、MD、ZIP

### 📊 输出结构

该工具为每个处理的文档创建全面的目录结构：

```text
llm_summaries/
├── document_name_model_name/
│   ├── chunks/
│   │   ├── chunk_1.md
│   │   └── chunk_2.md
│   ├── prompts/
│   │   ├── chunk_analysis_1.md
│   │   ├── chunk_analysis_2.md
│   │   ├── synthesis.md
│   │   └── translation.md
│   ├── responses/
│   │   ├── chunk_analysis_1.md
│   │   ├── chunk_analysis_2.md
│   │   ├── synthesis.md
│   │   └── translation.md
│   ├── process_times/
│   │   ├── process_times.json
│   │   └── process_times.txt
│   └── token_usage/
│       ├── token_usage.json
│       └── token_usage.txt
```

### 🔍 内容处理工作流程

1. **内容转换**：将输入文件/URL 转换为清洁的 markdown
2. **智能分块**：将内容拆分为可管理的块（每个约 2000 个令牌）
3. **块分析**：每个块都由 LLM 分析，并包含来自之前块的上下文
4. **综合**：将多个块分析合并为全面的摘要
5. **翻译**：将最终摘要翻译成中文
6. **报告**：生成有关令牌使用情况、成本和处理时间的详细报告

### 📈 分析与监控

- **Token使用跟踪**：每个请求的输入/输出令牌
- **成本计算**：基于模型定价的自动成本计算
- **处理时间分析**：每个处理步骤的详细计时
- **全面日志记录**：所有操作的完整审计跟踪

### 🛡️ 错误处理

- **重试逻辑**：API 失败时的自动重试与指数退避
- **格式回退**：多种转换方法确保强大的内容提取
- **优雅降级**：即使个别文档失败也继续处理

### 🔧 高级配置 (Advanced Configuration)

系统使用 YAML 配置文件进行模型设置：

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

### 🤝 贡献

1. Fork 仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开 Pull Request

### 📝 许可证

该项目根据 MIT 许可证授权 - 有关详细信息，请参阅 [LICENSE](LICENSE) 文件。

### 🙏 致谢

- **Microsoft MarkItDown** 提供文档转换功能
- **Readabilipy** 和 **Trafilatura** 提供网页内容提取
- **Deepseek** 和 **Google Gemini** 提供 LLM 功能

### 📞 支持

如需支持，请在 GitHub 上开启问题或联系维护者。

---

**注意**：该工具专为研究和教育目的而设计。请确保您有必要的权利来处理和总结您正在使用的内容，并在处理大量内容时注意 API 使用成本。