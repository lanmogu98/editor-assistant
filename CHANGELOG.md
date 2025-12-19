# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- Unit coverage for content validation (blocked publishers, short content warnings).
- Test fixtures now require `DEEPSEEK_API_KEY_VOLC` (DeepSeek via Volcengine); legacy key removed.
- `TODO_codex.md` to track branch-specific tasks (tests vs reliability).
- Batch processing helper script (`scripts/batch_process.py`) for HTML/MD with task/model/preview options.

### Docs
- Developer testing guide notes `deepseek-v3.2` as the cheap default model for integration tests and the env var `DEEPSEEK_API_KEY_VOLC`.

### Fixed
- Language-aware token estimation to improve Chinese/English mixed token counting.

## [0.4.0] - 2025-12-18

Major release with SQLite storage, streaming output, and improved testing.

### Added
- **SQLite Storage Module** - Centralized run history and statistics:
  - New `storage/` module with SQLite database (`~/.editor_assistant/runs.db`)
  - Automatic tracking of all runs, inputs, outputs, and token usage
  - Input deduplication via content hash (same content = same input record)
  - Many-to-many relationship: one input can be used in multiple runs
  - Support for JSON outputs (for future structured tasks like classification)
  
- **New CLI Commands**:
  - `editor-assistant history [-n N] [--search PATTERN]` - List recent runs
  - `editor-assistant stats [-d DAYS]` - Usage statistics
  - `editor-assistant show RUN_ID [--output]` - Run details

- **Streaming Output** - Real-time response display:
  - Default: streaming enabled (content displays as it generates)
  - `--no-stream` flag to disable and wait for complete response
  - Works with all commands: `brief`, `outline`, `translate`, `process`

- **Multi-task Serial Execution**:
  - New `process` command with `--tasks` parameter
  - Support comma-separated task list (e.g., `--tasks brief,outline`)
  - Each task runs serially on the same converted input

- **Pluggable Task System** - Extensible task architecture:
  - New `tasks/` module with `TaskRegistry` for dynamic task registration
  - `Task` base class with `validate()`, `build_prompt()`, `post_process()` methods
  - Existing tasks (`brief`, `outline`, `translate`) refactored as Task subclasses
  - Tasks can now produce multiple outputs (e.g., translate → main + bilingual)
  - Updated `DEVELOPER.md` with simplified "Adding a New Task Type" guide

- **Gemini 3 thinking mode support** - Control reasoning depth for Gemini 3 models:
  - Added `--thinking` CLI parameter (`low`, `medium`, `high`)
  - Default: model decides dynamically (no parameter sent)
  - Maps to `reasoning_effort` in OpenAI-compatible format
  - Priority: CLI argument > config file > model default
  - See: https://ai.google.dev/gemini-api/docs/gemini-3
- **Per-provider rate limiting** - Each provider can now have its own rate limit configuration:
  - Added `RateLimitSettings` model in `set_llm.py`
  - Added optional `rate_limit` field in `ProviderSettings`
  - `LLMClient` reads rate limits from provider config, falls back to global defaults
  - Example configuration added to `anthropic-openrouter` in `llm_config.yml`
- `DEVELOPER.md` - Comprehensive developer guide with:
  - Architecture overview and data flow diagram
  - Module reference table
  - Step-by-step guide for adding new LLM models
  - Step-by-step guide for adding new task types
  - Configuration system documentation
  - Testing guide
  - Common patterns (error handling, validation, caching)

### Changed
- `MDProcessor` now automatically records all runs to SQLite database
- Error tracking: failed runs are recorded with error messages
- Currency symbol now matches model's pricing currency (¥ for CNY, $ for USD)
- Test Module rebuilt from scratch with proper structure:
  - Unit tests: `tests/unit/` - Fast, mocked, no API calls
  - Integration tests: `tests/integration/` - Real API calls
  - Test fixtures: `tests/fixtures/` with sample data
  - New markers: `unit`, `integration`, `slow`, `expensive`

### Fixed
- **CLI:** Fixed `cmd_clean_html()` API mismatch
- **CLI:** Fixed `cmd_convert_to_md()` URL path handling
- **Test/Production Database Isolation**:
  - Two separate environment variables: `EDITOR_ASSISTANT_TEST_DB_DIR` (test) and `EDITOR_ASSISTANT_DB_DIR` (prod)
  - `conftest.py` sets test variable; production never sees it

---

## [0.3.1] - 2025-12-17

### Fixed
- **Performance:** Fixed O(n²) string concatenation in `_create_bilingual_content()` using `list.append()` + `''.join()` (`md_processor.py`)
- **Performance:** Added lazy-loaded MarkItDown instance reuse to avoid repeated instantiation (`md_converter.py`)
- **Performance:** Fixed trafilatura double-processing by using `bare_extraction()` for single-pass content+metadata extraction (`clean_html_to_md.py`)
- **Typo:** Renamed `md_processesor.py` → `md_processor.py`
- **Typo:** Fixed `MINIMAL_TOKEN_ACCESPTED` → `MINIMAL_TOKEN_ACCEPTED`
- **Version:** Synced CLI version to 0.3.0 to match pyproject.toml
- **Code Style:** Fixed docstrings placed outside method definitions (`md_converter.py`)
- **Code Quality:** Standardized error handling patterns across modules:
  - `md_processor.py`: Replaced `logging.error()` with custom `error()` function for consistent user-facing messages
  - `md_processor.py`: Use specific exceptions (`OSError`, `IOError`, `RuntimeError`) instead of generic `Exception`
  - `md_converter.py`: Replaced generic `Exception` with `ConnectionError` for URL access errors
- **Code Quality:** Consolidated 3 consecutive try/except blocks for bilingual content into single block (`md_processor.py:186-196`)
- **Type Hints:** Fixed `MDArticle.output_path` type from `Optional[str]` to `Optional[Path]` to match actual usage (`data_models.py`)
- **Incomplete Module:** Implemented `content_validation.py` module (was just a stub):
  - Two-stage validation: blocked publisher check (hard stop) + content length check (warning)
  - Blocked publisher list management (add/remove/get)
  - `BlockedPublisherError` and `ContentValidationError` exceptions
  - Configurable via `MIN_CHARS_WARNING_THRESHOLD` constant
- **Circular Import:** Fixed circular import workaround in `llm_client.py` by moving `user_message` to top-level imports

### Removed
- ~40 lines of commented dead code from `md_processor.py`
- ~70 lines of test code from `md_converter.py` (test_md_converter function)
- ~75 lines of test code and commented blocks from `clean_html_to_md.py`
- ~3 lines of commented code from `llm_client.py`
- Unused imports: `datetime` from md_converter.py, `time` and `json` from clean_html_to_md.py

### Added
- New `config/constants.py` module centralizing all magic numbers and configuration values
- **Rate limiting** in LLM client to prevent API bans (`llm_client.py`):
  - Minimum interval between requests (configurable via `MIN_REQUEST_INTERVAL_SECONDS`)
  - Per-minute request limit (configurable via `MAX_REQUESTS_PER_MINUTE`)
  - Warning messages when rate limiting is applied (configurable via `RATE_LIMIT_WARNINGS_ENABLED`)
- **Response caching** for LLM responses to avoid redundant API calls (`llm_client.py`):
  - LRU cache with configurable max size (`RESPONSE_CACHE_MAX_SIZE`)
  - TTL-based expiration (`RESPONSE_CACHE_TTL_SECONDS`)
  - Disabled by default (`RESPONSE_CACHE_ENABLED=False`), enable for repeated prompts
  - Cache statistics via `get_cache_stats()` and `clear_cache()` methods
- Test suite (`tests/test_basic.py`) expanded to 48 unit tests covering imports, models, functionality, rate limiting, caching, type hints, and content validation

### Changed
- Updated imports in `main.py` to use renamed module
- Refactored all modules to import constants from centralized `config/constants.py`:
  - `md_processor.py`: CHAR_TOKEN_RATIO, MINIMAL_TOKEN_ACCEPTED, PROMPT_OVERHEAD_TOKENS, DEBUG_LOGGING_LEVEL
  - `llm_client.py`: MAX_API_RETRIES, INITIAL_RETRY_DELAY_SECONDS
  - `md_converter.py`: DEFAULT_LOGGING_LEVEL, URL_HEAD_TIMEOUT_SECONDS
  - `clean_html_to_md.py`: DEFAULT_USER_AGENT, DEBUG_LOGGING_LEVEL
  - `content_validation.py`: MIN_CHARS_WARNING_THRESHOLD

---

## [0.3.0] - Previous Release

Initial tracked version with:
- Multi-format document processing (PDF, DOCX, images, web URLs, markdown)
- Three main content generation types: Brief News, Research Outlines, Chinese Translations
- Support for 15+ LLM models across 9 providers
- Token usage tracking and cost calculation
