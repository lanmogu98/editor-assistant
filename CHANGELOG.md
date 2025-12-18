# Changelog

All notable changes to this project will be documented in this file.

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
- Test suite (`tests/test_basic.py`) expanded to 40 unit tests covering imports, models, functionality, rate limiting, and caching

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
