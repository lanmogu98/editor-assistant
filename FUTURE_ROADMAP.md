# Future Roadmap

This document outlines remaining architectural improvements that require significant effort but provide substantial value.

---

## 1. Async/Concurrent Processing

**Why it matters:**
- Currently processes documents sequentially (N documents = N × time)
- Network I/O wait time is wasted (LLM API calls take 2-30 seconds each)
- Cannot support streaming responses for real-time output

**Value:** 3-5x speedup for multi-document workflows

**Implementation Plan:**
```
1. Add async HTTP client (aiohttp or httpx)
2. Convert LLMClient.generate_response() to async
3. Add asyncio.gather() for parallel document processing
4. Optional: Add streaming support for real-time output
```

**Estimated effort:** 2-3 days

---

## 2. Configuration File Support

**Why it matters:**
- Users must pass CLI args every time
- No way to set project-specific defaults
- Environment variables are clunky for multiple settings

**Value:** Better UX, reproducible workflows

**Implementation Plan:**
```
1. Create config schema (YAML):
   ~/.editor-assistant/config.yml     # User defaults
   .editor-assistant.yml              # Project overrides

2. Add config loader in config/settings.py
3. Merge priority: CLI args > project > user > defaults
4. Document supported options
```

**Example config:**
```yaml
model: gpt-4
cache_enabled: true
rate_limit_per_minute: 60
output_dir: ./output
blocked_publishers:
  - nytimes.com
```

**Estimated effort:** 1 day

---

## 3. Dependency Injection / Loose Coupling

**Why it matters:**
- Hard to unit test (classes instantiate their dependencies directly)
- Cannot swap implementations (e.g., mock LLM for testing)
- Adding new providers requires modifying existing code

**Value:** Testability, extensibility, cleaner architecture

**Implementation Plan:**
```
1. Define interfaces/protocols for LLMClient, Converter, Validator
2. Pass dependencies via constructor (not self-instantiated)
3. Add simple factory or container for wiring
4. Update tests to use mocks
```

**Example:**
```python
# Before
class MDProcessor:
    def __init__(self, model_name):
        self.llm_client = LLMClient(model_name)  # tight coupling

# After
class MDProcessor:
    def __init__(self, llm_client: LLMClientProtocol):
        self.llm_client = llm_client  # injected
```

**Estimated effort:** 1-2 days

---

## 4. Plugin/Extension System

**Why it matters:**
- Adding new converters requires modifying core code
- Users cannot add custom prompts without forking
- No way to extend without touching internals

**Value:** User extensibility, cleaner separation

**Implementation Plan:**
```
1. Define plugin interfaces (Converter, Processor, Prompt)
2. Add registry pattern for dynamic registration
3. Scan plugin directories on startup
4. Document plugin development
```

**Example:**
```python
# plugins/my_converter.py
@register_converter("my-format")
class MyConverter(ConverterProtocol):
    def convert(self, path: str) -> MDArticle:
        ...
```

**Estimated effort:** 2-3 days

---

## 5. Persistence Layer

**Why it matters:**
- Token usage only saved to text files
- No historical tracking or analytics
- Cannot resume interrupted processing

**Value:** Cost tracking, audit logs, checkpoint/resume

**Implementation Plan:**
```
1. Add SQLite database (lightweight, no server needed)
2. Schema: sessions, requests, token_usage, cache
3. Add CLI commands: `history`, `stats`, `resume`
4. Optional: Export to CSV/JSON
```

**Estimated effort:** 2-3 days

---

## Priority Order

| Priority | Item | Effort | Impact |
|----------|------|--------|--------|
| 1 | Configuration file support | 1 day | High (UX) |
| 2 | Async processing | 2-3 days | High (Performance) |
| 3 | Dependency injection | 1-2 days | Medium (Testability) |
| 4 | Plugin system | 2-3 days | Medium (Extensibility) |
| 5 | Persistence layer | 2-3 days | Medium (Analytics) |

---

## Completed Items (This Session)

✅ Performance: O(n²) string fix, lazy loading, single-pass extraction
✅ Maintenance: Typos, dead code, error handling, type hints
✅ Scaling: Rate limiting, response caching
✅ Validation: Content validation module
✅ Code quality: Centralized constants, circular import fix

**Total: 15 issues resolved, 48 tests added**
