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

### Removed
- ~40 lines of commented dead code from `md_processor.py`
- ~70 lines of test code from `md_converter.py` (test_md_converter function)
- ~75 lines of test code and commented blocks from `clean_html_to_md.py`
- ~3 lines of commented code from `llm_client.py`
- Unused imports: `datetime` from md_converter.py, `time` and `json` from clean_html_to_md.py

### Changed
- Updated imports in `main.py` to use renamed module

---

## [0.3.0] - Previous Release

Initial tracked version with:
- Multi-format document processing (PDF, DOCX, images, web URLs, markdown)
- Three main content generation types: Brief News, Research Outlines, Chinese Translations
- Support for 15+ LLM models across 9 providers
- Token usage tracking and cost calculation
