# Matrix Review Fix Report

## Findings fixed

### editor-assistant docs/catalog drift
- Updated `README.md` to state that the shared model catalog now lives in `llm_exec_core/llm_config.yml` inside the `llm-exec-core` package.
- Updated `README.md` to explain that this branch intentionally uses the sibling checkout plus relative `[tool.uv.sources]` entry, and that release consumers should switch to `llm-exec-core==0.1.0` only after publish.
- Updated `DEVELOPER_GUIDE.md` to move LLM transport/config ownership to `llm-exec-core`, describe `editor_assistant.llm_client` and `editor_assistant.config.llm_models` as compatibility shims, and remove the deleted app-local YAML as the source of truth.

### llm-exec-core tests
- Tightened legacy bridge coverage so `generate_response()` must preserve `process_times.total_time` from `ExecutionMetadata.duration_seconds`; a hardcoded zero would now fail.
- Added streaming callback coverage to assert `stream_callback` receives chunks in order during streaming responses.

### llm-exec-core packaging/docs/artifact verification
- Added package-facing `README.md` and `CHANGELOG.md`.
- Wired `readme = "README.md"` into `pyproject.toml`.
- Built wheel and sdist, inspected contents, and verified artifact import with packaged `llm_config.yml`.

## Files changed per repo

### llm-exec-core
- `README.md`
  - Added short package overview and migration context.
- `CHANGELOG.md`
  - Added initial `0.1.0` changelog entry.
- `pyproject.toml`
  - Added `readme = "README.md"`.
- `tests/unit/test_client_result.py`
  - Pinned legacy duration mapping to an exact non-zero value.
- `tests/unit/test_client_streaming.py`
  - Added ordered streaming callback regression test.

### editor-assistant
- `README.md`
  - Corrected catalog/source-of-truth docs and documented current branch dependency mode.
- `DEVELOPER_GUIDE.md`
  - Corrected architecture ownership, config location, and legacy shim guidance.
- `.superpowers/sdd/matrix-review-fix-report.md`
  - Added this fix report.

## Verification outputs

### llm-exec-core
- `UV_CACHE_DIR=<tmp-uv-cache> uv run pytest tests/unit/`
  - Passed: `23 passed in 0.15s`
- `UV_CACHE_DIR=<tmp-uv-cache> uv run flake8 src/`
  - Passed
- `UV_CACHE_DIR=<tmp-uv-cache> uv run mypy src/`
  - Passed: `Success: no issues found in 7 source files`
- `UV_CACHE_DIR=<tmp-uv-cache> uv run black src/ tests/ --check`
  - Passed: `14 files would be left unchanged`
  - Note: Black emitted a Python 3.13 safety-check warning because the code targets newer grammar, but the command exited successfully.

### editor-assistant
- `UV_CACHE_DIR=<tmp-uv-cache> uv sync`
  - Passed: `Resolved 122 packages in 3ms`
  - Installed sibling source from the configured relative editable source.
- `UV_CACHE_DIR=<tmp-uv-cache> uv run pytest tests/unit/`
  - Passed: `155 passed in 0.70s`
- `UV_CACHE_DIR=<tmp-uv-cache> uv run pytest tests/stress/test_sqlite_concurrency.py tests/stress/test_error_boundaries.py`
  - Passed: `5 passed in 0.65s`
- `UV_CACHE_DIR=<tmp-uv-cache> uv run flake8 src/`
  - Passed
- `UV_CACHE_DIR=<tmp-uv-cache> uv run mypy src/`
  - Passed: `Success: no issues found in 24 source files`
- `UV_CACHE_DIR=<tmp-uv-cache> uv run black src/ tests/ --check`
  - Passed: `51 files would be left unchanged`
  - Note: Black emitted the same Python-version safety warning here, but exited successfully.

## Artifact verification details

### Build commands
- `rm -rf <tmp-dist> && mkdir -p <tmp-dist> && UV_CACHE_DIR=<tmp-uv-cache> uv build --sdist --wheel --out-dir <tmp-dist>`
  - Passed
  - Produced:
    - `<tmp-dist>/llm_exec_core-0.1.0-py3-none-any.whl`
    - `<tmp-dist>/llm_exec_core-0.1.0.tar.gz`

### Artifact content inspection
- `python3 -m zipfile -l <tmp-dist>/llm_exec_core-0.1.0-py3-none-any.whl`
  - Confirmed wheel contains:
    - `llm_exec_core/llm_config.yml`
    - `llm_exec_core/py.typed`
- `tar -tzf <tmp-dist>/llm_exec_core-0.1.0.tar.gz`
  - Confirmed sdist contains:
    - `llm_exec_core-0.1.0/src/llm_exec_core/llm_config.yml`
    - `llm_exec_core-0.1.0/src/llm_exec_core/py.typed`
    - `llm_exec_core-0.1.0/README.md`

### Artifact import proof
- Initial no-deps wheel install succeeded but top-level import failed on missing runtime dependency `httpx`, which is expected for a bare `--no-deps` install.
- Final proof command:
  - `python3 -m venv <tmp-wheel-venv> && <tmp-wheel-venv>/bin/pip install <tmp-dist>/llm_exec_core-0.1.0-py3-none-any.whl && <tmp-wheel-venv>/bin/python -c 'import llm_exec_core; from llm_exec_core.config import _get_default_config_path; p=_get_default_config_path(); print(llm_exec_core.__version__); print(p.name); print(p.exists())'`
  - Passed with output:
    - `0.1.0`
    - `llm_config.yml`
    - `True`

## Commits created

### llm-exec-core
- `test: cover streaming callbacks and package artifacts` (`8a21e68`)

### editor-assistant
- `docs: align llm core migration guidance`

## Final status outputs

- `git -C <llm-exec-core-repo> status --short`
  - Clean after commit
- `git -C <editor-assistant-repo> status --short`
  - Clean after commit

## Deviations

- `uv run ...` inside the sandbox initially failed because local build requirements could not be resolved without network access; the required verification was rerun unsandboxed.
