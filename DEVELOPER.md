# Developer Guide

This document provides technical documentation for developers contributing to Editor Assistant.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Module Reference](#module-reference)
3. [Adding a New LLM Model](#adding-a-new-llm-model)
4. [Adding a New Task Type](#adding-a-new-task-type)
5. [Configuration System](#configuration-system)
6. [Testing Guide](#testing-guide)
7. [Common Patterns](#common-patterns)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                           CLI Layer                              │
│                          (cli.py)                                │
│  Commands: brief, outline, translate, convert, clean            │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Orchestration Layer                         │
│                         (main.py)                                │
│                     EditorAssistant class                        │
└───────────────┬─────────────────────────────┬───────────────────┘
                │                             │
                ▼                             ▼
┌───────────────────────────┐   ┌─────────────────────────────────┐
│    Content Conversion      │   │       Content Processing         │
│    (md_converter.py)       │   │       (md_processor.py)          │
│    - PDF, DOCX, HTML       │   │       - Prompt building          │
│    - URL fetching          │   │       - LLM interaction          │
│    - Format detection      │   │       - Output formatting        │
└───────────────┬────────────┘   └───────────────┬─────────────────┘
                │                                 │
                ▼                                 ▼
┌───────────────────────────┐   ┌─────────────────────────────────┐
│   HTML Cleaning            │   │         LLM Client               │
│   (clean_html_to_md.py)    │   │       (llm_client.py)            │
│   - Readabilipy            │   │       - API calls                │
│   - Trafilatura            │   │       - Rate limiting            │
│                            │   │       - Response caching         │
└────────────────────────────┘   │       - Token tracking           │
                                 └───────────────┬─────────────────┘
                                                 │
                                                 ▼
                                 ┌─────────────────────────────────┐
                                 │        Config Layer              │
                                 │        (config/)                 │
                                 │  - llm_config.yml (models)       │
                                 │  - constants.py (settings)       │
                                 │  - prompts/ (templates)          │
                                 └─────────────────────────────────┘
```

### Data Flow

```
Input (URL/PDF/MD) 
    → MarkdownConverter.convert_content() 
    → MDArticle (normalized content)
    → MDProcessor.process() 
    → Prompt + LLMClient.generate_response()
    → Output (MD files + token report)
```

---

## Module Reference

### Core Modules

| Module | Purpose | Key Classes/Functions |
|--------|---------|----------------------|
| `cli.py` | Command-line interface | `main()`, `cmd_generate_brief()`, `cmd_generate_outline()` |
| `main.py` | Orchestration | `EditorAssistant` |
| `md_converter.py` | Format conversion | `MarkdownConverter` |
| `md_processor.py` | LLM processing | `MDProcessor` |
| `llm_client.py` | API interaction | `LLMClient`, `ResponseCache` |
| `clean_html_to_md.py` | HTML extraction | `CleanHTML2Markdown` |
| `content_validation.py` | Input validation | `validate_content()`, `BlockedPublisherError` |
| `data_models.py` | Data structures | `MDArticle`, `Input`, `ProcessType`, `InputType` |

### Config Modules

| Module | Purpose |
|--------|---------|
| `config/llm_config.yml` | LLM provider settings (API URLs, models, pricing) |
| `config/set_llm.py` | Model/Provider enums and YAML loader |
| `config/constants.py` | All configurable constants |
| `config/load_prompt.py` | Prompt template loader |
| `config/logging_config.py` | Logging utilities |
| `config/prompts/*.txt` | Jinja2 prompt templates |

---

## Adding a New LLM Model

### Step 1: Add to `LLMModel` Enum

Edit `config/set_llm.py`:

```python
class LLMModel(str, Enum):
    # existing models...
    
    # Add your new model
    your_new_model = "your-model-name"  # The CLI-facing name
```

### Step 2: Add Provider (if new)

If using a new provider, add to `ServiceProvider` enum:

```python
class ServiceProvider(str, Enum):
    # existing providers...
    
    your_provider = "your-provider"
```

### Step 3: Configure in YAML

Edit `config/llm_config.yml`:

```yaml
your-provider:
  api_key_env_var: "YOUR_API_KEY"
  api_base_url: "https://api.yourprovider.com/v1/chat/completions"
  temperature: 0.6
  max_tokens: 32000
  context_window: 128000
  pricing_currency: "$"
  models:
    your-model-name:
      id: "actual-api-model-id"
      pricing: {input: 1.00, output: 2.00}  # per 1M tokens
```

### Step 4: Set Environment Variable

```bash
export YOUR_API_KEY="your-api-key-here"
```

### Step 5: Test

```bash
editor-assistant brief paper=test.pdf --model your-model-name
```

---

## Adding a New Task Type

Adding a new task type requires changes in 4 files:

### Step 1: Add ProcessType Enum

Edit `data_models.py`:

```python
class ProcessType(str, Enum):
    OUTLINE = 'outline'
    BRIEF = 'brief'
    TRANSLATE = 'translate'
    YOUR_NEW_TYPE = 'your_new_type'  # Add this
```

### Step 2: Create Prompt Template

Create `config/prompts/your_new_type.txt`:

```jinja2
You are an expert at {{ task_description }}.

## Input Content
{{ content }}

## Instructions
{{ specific_instructions }}
```

### Step 3: Add Prompt Loader

Edit `config/load_prompt.py`:

```python
def load_your_new_type_prompt(md_article: MDArticle) -> str:
    template = _load_template("your_new_type.txt")
    return template.render(
        content=md_article.content,
        title=md_article.title,
        # ... other variables
    )
```

### Step 4: Add Processing Logic

Edit `md_processor.py` in `process()` method:

```python
match process_type:
    case ProcessType.YOUR_NEW_TYPE:
        prompt = load_your_new_type_prompt(md_article)
        response = self.llm_client.generate_response(prompt, "your_new_type")
        self._save_response(response, md_article, "your_new_type")
```

### Step 5: Add CLI Command

Edit `cli.py`:

```python
def cmd_your_new_type(args):
    """Your new command description."""
    assistant = EditorAssistant(args.model, debug_mode=args.debug)
    input_obj = Input(type=InputType.PAPER, path=args.input_file)
    assistant.process_multiple([input_obj], ProcessType.YOUR_NEW_TYPE)

# In create_parser():
your_parser = subparsers.add_parser(
    "your-command",
    help="Description for help"
)
your_parser.add_argument("input_file", help="Input file path")
add_common_arguments(your_parser)
your_parser.set_defaults(func=cmd_your_new_type)
```

---

## Configuration System

### Constants (`config/constants.py`)

All magic numbers are centralized here:

```python
# Token estimation
CHAR_TOKEN_RATIO = 3.5
MINIMAL_TOKEN_ACCEPTED = 100
PROMPT_OVERHEAD_TOKENS = 10000

# API retry
MAX_API_RETRIES = 3
INITIAL_RETRY_DELAY_SECONDS = 1

# Rate limiting
MIN_REQUEST_INTERVAL_SECONDS = 0.5
MAX_REQUESTS_PER_MINUTE = 60

# Caching
RESPONSE_CACHE_ENABLED = False
RESPONSE_CACHE_MAX_SIZE = 100
RESPONSE_CACHE_TTL_SECONDS = 3600
```

### Model Configuration (`config/llm_config.yml`)

Structure:
```yaml
provider-name:
  api_key_env_var: "ENV_VAR_NAME"
  api_base_url: "https://..."
  temperature: 0.6
  max_tokens: 32000
  context_window: 128000
  pricing_currency: "$"
  request_overrides: {}  # Optional: extra API params
  models:
    model-name:
      id: "actual-api-id"
      pricing: {input: X, output: Y}
```

---

## Testing Guide

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/unit/test_md_processor.py

# With coverage
pytest --cov=src/editor_assistant

# Verbose output
pytest -v
```

### Test Structure

```
tests/
├── conftest.py          # Shared fixtures
├── fixtures/            # Test data
│   ├── sample_data/     # Sample input files
│   └── *.py             # Python fixtures
├── unit/                # Unit tests
│   ├── test_md_converter.py
│   ├── test_md_processor.py
│   └── test_prompt_loader.py
└── integration/         # Integration tests
    ├── test_gemini_api.py
    └── test_multi_source_processing.py
```

### Writing Tests

```python
import pytest
from editor_assistant.data_models import ProcessType, InputType

def test_your_feature():
    """Test description."""
    # Arrange
    input_data = ...
    
    # Act
    result = your_function(input_data)
    
    # Assert
    assert result == expected
```

---

## Common Patterns

### Error Handling

Use the logging helpers from `config/logging_config.py`:

```python
from .config.logging_config import error, warning, progress, user_message

# User-facing error (red ✗)
error(f"Failed to process: {reason}")

# Warning (yellow ⚠)
warning(f"Content may be incomplete")

# Progress update (green •)
progress(f"Processing document...")

# Important info (blue •)
user_message(f"Output saved to: {path}")
```

### Content Validation

```python
from .content_validation import validate_content, BlockedPublisherError

try:
    validate_content(md_article)
except BlockedPublisherError as e:
    error(f"Blocked publisher: {e}")
    return None
```

### Rate Limiting

The `LLMClient` handles rate limiting automatically. 

**Per-provider configuration** (in `llm_config.yml`):

```yaml
your-provider:
  # ... other settings ...
  rate_limit:
    min_interval_seconds: 1.0  # Min time between requests
    max_requests_per_minute: 30  # Max requests per minute (0 = unlimited)
```

**Global defaults** (in `constants.py`, used when provider doesn't specify):

```python
MIN_REQUEST_INTERVAL_SECONDS = 0.5  # Default min interval
MAX_REQUESTS_PER_MINUTE = 60        # Default max RPM
```

### Response Caching

Enable for repeated prompts:

```python
# In constants.py
RESPONSE_CACHE_ENABLED = True
RESPONSE_CACHE_MAX_SIZE = 100
RESPONSE_CACHE_TTL_SECONDS = 3600

# Usage
client = LLMClient("model-name")
response = client.generate_response(prompt)  # May return cached response

# Check stats
print(client.get_cache_stats())
# {'hits': 5, 'misses': 10, 'hit_rate': '33.3%', 'size': 10, 'max_size': 100}
```

---

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes with tests
3. Update CHANGELOG.md
4. Submit PR to main

### Code Style

- Follow PEP 8
- Use type hints
- Document public functions with docstrings
- Keep functions focused and small

### Commit Messages

```
type: short description

- feat: new feature
- fix: bug fix
- docs: documentation
- refactor: code restructuring
- test: adding tests
- chore: maintenance
```

