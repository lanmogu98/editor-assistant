# Editor Assistant

[English](#english) | [中文](#chinese)

<a id="english"></a>

# Content Summarization Tool

A powerful tool for automatically summarizing various types of content (research papers, news articles) using LLMs. The system intelligently splits content into manageable chunks, processes each chunk with an LLM, and synthesizes the results into comprehensive summaries with translations.

## Features

- **Content Chunking**: Splits content into chunks while preserving paragraph integrity
- **Context Preservation**: Maintains context between chunks by passing previous summaries forward
- **Multiple Content Types**: Supports research papers and news article summarization
- **Bilingual Summaries**: Automatically translates summaries to Chinese
- **Token Usage Tracking**: Monitors token usage, costs, and processing times
- **Detailed Output**: Generates structured summaries with key points, terminology, and more
- **Full Transparency**: Saves all prompts and responses for inspection

## Prerequisites

- Python 3.6+
- An API key for the Volcengine API (Deepseek models)
- Required Python packages (see requirements.txt)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/editor_assistant.git
   cd editor_assistant
   ```

2. Install the package:
   ```
   pip install -e .
   ```

3. Set up your API key:
   - Set the environment variable: `export VOLC_API_KEY=your_api_key`
   - Or use a `.env` file with `VOLC_API_KEY=your_api_key`

## Usage

### Python API

```python
from editor_assistant.summarize_content import summarize_one

# Summarize a research paper
summarize_one("path/to/paper.md", type="research", model_name="deepseek-r1")

# Summarize multiple research papers
from editor_assistant.summarize_content import summarize_multiple
summarize_multiple(["path/to/paper1.md", "path/to/paper2.md"], 
                  type="research", 
                  model_name="deepseek-r1")

# Summarize a news article
summarize_one("path/to/article.md", type="news", model_name="deepseek-v3")
```

### Command Line

After installation, you'll have access to two command-line tools:

**For research papers:**
```
summarize_research path/to/paper.md [path/to/paper2.md ...] --model deepseek-v3
```

**For news articles:**
```
summarize_news path/to/article.md [path/to/article2.md ...] --model deepseek-r1
```

**Options:**
- `--model`: Model to use (choices: "deepseek-r1", "deepseek-v3", default: "deepseek-v3")

## Output Structure

The summarizer creates the following directory structure for each content file:

```
llm_summaries/
├── file_name_model_name/
│   ├── chunks/
│   │   ├── chunk_1.txt
│   │   └── chunk_2.txt
│   ├── prompts/
│   │   ├── chunk_analysis_1.txt
│   │   ├── chunk_analysis_2.txt
│   │   ├── synthesis.txt
│   │   └── translation.txt
│   └── responses/
│       ├── chunk_analysis_1.md
│       ├── chunk_analysis_2.md
│       ├── synthesis.md
│       └── translation.md
```

## Configuration

The system uses the following default configuration:

- **LLM Models**: Deepseek models (deepseek-r1-250120, deepseek-v3-241226)
- **Chunking**: 8000 characters per chunk (~ 2000 tokens) with 200 character overlap
- **Temperature**: 0.6 for LLM generation
- **Max Tokens**: 4000 for LLM responses

## License

MIT

---

<a id="chinese"></a>

# 内容摘要工具

一种使用大型语言模型（LLM）自动总结各种类型内容（研究论文、科技新闻）的工具。该系统将内容分割成可管理的块，用 LLM 处理每个块，然后将结果合成为全面的总结并提供中文翻译。

## 功能特点

- **内容分块**：在保持段落完整性的同时将内容分块
- **上下文保持**：通过向前传递之前的总结内容来保持块之间的上下文
- **多种内容类型**：支持研究论文和新闻文章摘要
- **双语摘要**：自动将总结翻译成中文
- **令牌使用跟踪**：监控令牌使用情况、成本和处理时间
- **详细输出**：生成包含要点、术语等结构化摘要
- **完全透明**：保存所有提示和响应以供检查

## 先决条件

- Python 3.6+
- 火山引擎 API 密钥（Deepseek 模型）
- 所需的Python包（见 requirements.txt）

## 安装

1. 克隆此仓库：
   ```
   git clone https://github.com/yourusername/editor_assistant.git
   cd editor_assistant
   ```

2. 安装软件包：
   ```
   pip install -e .
   ```

3. 设置您的API密钥：
   - 设置环境变量：`export VOLC_API_KEY=your_api_key`
   - 或使用`.env`文件，内容为`VOLC_API_KEY=your_api_key`

## 使用方法

### Python API

```python

# 总结单篇论文
from editor_assistant.summarize_content import summarize_one
summarize_one("path/to/paper.md", type="research", model_name="deepseek-r1")

# 总结多篇论文
from editor_assistant.summarize_content import summarize_multiple
summarize_multiple(["path/to/paper1.md", "path/to/paper2.md"], 
                  type="research", 
                  model_name="deepseek-r1")

# 总结科技新闻
summarize_one("path/to/article.md", type="news", model_name="deepseek-v3")
```

### 命令行

安装后，您将可以使用两个命令行工具：

**用于研究论文：**
```
summarize_research path/to/paper.md [path/to/paper2.md ...] --model deepseek-v3
```

**用于新闻文章：**
```
summarize_news path/to/article.md [path/to/article2.md ...] --model deepseek-r1
```

**选项：**
- `--model`：要使用的模型（选项："deepseek-r1"、"deepseek-v3"，默认："deepseek-v3"）

## 输出结构

摘要器为每个内容文件创建以下目录结构：

```
llm_summaries/
├── file_name_model_name/
│   ├── chunks/
│   │   ├── chunk_1.txt
│   │   └── chunk_2.txt
│   ├── prompts/
│   │   ├── chunk_analysis_1.txt
│   │   ├── chunk_analysis_2.txt
│   │   ├── synthesis.txt
│   │   └── translation.txt
│   └── responses/
│       ├── chunk_analysis_1.md
│       ├── chunk_analysis_2.md
│       ├── synthesis.md
│       └── translation.md
```

## 配置

系统使用以下默认配置：

- **LLM模型**：Deepseek模型（deepseek-r1-250120、deepseek-v3-241226）
- **分块**：每块8000字符（约2000令牌）与200字符重叠
- **温度**：LLM生成的温度为0.6
- **最大令牌数**：LLM响应的最大令牌数为4000

## 许可证

MIT