# Matrix Review Round 2 Fix Report

Date: 2026-06-30

## Findings Fixed

### editor-assistant
- Updated `DEVELOPER_GUIDE.md` to point schema enforcement and model/provider loading to `llm_exec_core.config`, with `editor_assistant.config.llm_models` called out as a legacy shim.
- Updated the `pyproject.toml` package-data comment so it matches current prompt-only package data.
- Moved the 0.6.0 release notes out of `Unreleased` and into a dated `0.6.0` changelog section.
- Corrected the historical note in `tests/issue_report.md` so it references the shared core catalog without rewriting the original context inaccurately.

### llm-exec-core
- Isolated default catalog cache reads in `load_all_settings()` by returning deep-copied provider settings from the cached default catalog.
- Added a regression test proving mutation of one default settings return value does not affect later default loads or a new `LLMClient` instance.
- Added a streaming cancellation regression test proving `asyncio.CancelledError` propagates during streamed line iteration.
- Added package metadata: description, proprietary license expression, and author.
- Updated the README to lead with published-package usage and keep coordinated sibling-checkout development as secondary context.

## Files Changed

### editor-assistant
- `CHANGELOG.md`
- `DEVELOPER_GUIDE.md`
- `pyproject.toml`
- `tests/issue_report.md`

### llm-exec-core
- `README.md`
- `pyproject.toml`
- `src/llm_exec_core/config.py`
- `tests/unit/test_client_streaming.py`
- `tests/unit/test_config.py`

## Verification Outputs

### llm-exec-core
- `UV_CACHE_DIR=<tmp-uv-cache> uv run pytest tests/unit/` -> `25 passed in 0.14s`
- `UV_CACHE_DIR=<tmp-uv-cache> uv run flake8 src/` -> passed
- `UV_CACHE_DIR=<tmp-uv-cache> uv run mypy src/` -> `Success: no issues found in 7 source files`
- `UV_CACHE_DIR=<tmp-uv-cache> uv run black src/ tests/ --check` -> passed (`14 files would be left unchanged`; Black emitted its known Python-version safety warning only)

### editor-assistant
- `UV_CACHE_DIR=<tmp-uv-cache> uv sync` -> passed
- `UV_CACHE_DIR=<tmp-uv-cache> uv run pytest tests/unit/` -> `155 passed in 0.85s`
- `UV_CACHE_DIR=<tmp-uv-cache> uv run pytest tests/stress/test_sqlite_concurrency.py tests/stress/test_error_boundaries.py` -> `5 passed in 0.89s`
- `UV_CACHE_DIR=<tmp-uv-cache> uv run flake8 src/` -> passed
- `UV_CACHE_DIR=<tmp-uv-cache> uv run mypy src/` -> `Success: no issues found in 24 source files`
- `UV_CACHE_DIR=<tmp-uv-cache> uv run black src/ tests/ --check` -> passed (`51 files would be left unchanged`; Black emitted its known Python-version safety warning only)

## Artifact Verification Details

- Rebuilt `llm-exec-core` with `UV_CACHE_DIR=<tmp-uv-cache> uv build`.
- Inspected wheel `METADATA` and sdist `PKG-INFO`; both contained:
  - `Name: llm-exec-core`
  - `Version: 0.1.0`
  - `Summary: Provider-agnostic async LLM execution core with a shared model catalog.`
  - `Author: mogu`
  - `License-Expression: LicenseRef-Proprietary`
- Verified built-wheel import with:
  - `UV_CACHE_DIR=<tmp-uv-cache> uv run --no-project --with <llm-exec-core-wheel> python -c "import llm_exec_core; print(llm_exec_core.__version__); print(hasattr(llm_exec_core, 'LLMClient'))"`
  - Output:
    - `0.1.0`
    - `True`

## Commits Created

### llm-exec-core
- `d6c4f34` `fix: isolate catalog cache and enrich package metadata`

### editor-assistant
- editor-assistant follow-up commit `docs: clean remaining llm catalog references`

## Final Statuses

### llm-exec-core
- clean (`git status --short` produced no output)

### editor-assistant
- clean (`git status --short` produced no output)

## Deviations

- The user-provided report path did not exist at session start, so this report file was created at the requested location before final commit.
