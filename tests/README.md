# Tests README

This folder contains the automated test suite for **Editor Assistant**.

If you are new to pytest and testing principles, start with the sections:

- “How pytest finds tests”
- “Markers: unit vs integration vs slow/expensive”
- “Fixtures and `conftest.py`”

---

## How to run tests

From the project root:

```bash
# Run everything (integration tests will typically be skipped if no API keys are set)
pytest

# Run only fast unit tests
pytest -m unit

# Run everything except slow tests
pytest -m "not slow"

# Run integration tests (may require real API keys; may cost money)
pytest -m integration
```

Markers are defined in `pytest.ini`.

---

## How pytest finds tests

This repo configures pytest to auto-discover:
- Files: `test_*.py`
- Classes: `Test*`
- Functions: `test_*`

See `pytest.ini`.

---

## Markers (very important)

We use markers to control *what kind of test* something is:

- **`unit`**:
  - Fast
  - No real network calls
  - No real paid API usage
  - Preferably no real database I/O (mock it unless the DB layer is what you test)

- **`integration`**:
  - Uses real components (e.g., subprocess, CLI, filesystem, database)
  - May call real external APIs (if so, it should also be marked `slow` and often `expensive`)

- **`slow`**:
  - Takes more than a few seconds
  - Used for stress tests, large inputs, concurrency tests, etc.

- **`expensive`**:
  - Costs money (real LLM calls)

- **`asyncio`**:
  - The test is async and must be awaited (uses `pytest-asyncio`)

Practical tip:
- When you add a new test, decide whether it’s **unit** or **integration** first, then add `slow/expensive` if applicable.

---

## Fixtures and `conftest.py`

### What is a fixture?

A fixture is a reusable setup function. Instead of writing setup code inside every test, you write a fixture and then “inject” it into tests by adding it as a function argument.

Example:

```python
def test_something(temp_dir):
    # pytest automatically calls the temp_dir fixture and passes it in
    assert temp_dir.exists()
```

### Why `conftest.py` is special

`tests/conftest.py` is auto-loaded by pytest. You do **not** import it.

It defines shared fixtures used across many tests.

### Database isolation (critical safety)

This repo has a session-scoped autouse fixture that ensures tests never touch the production DB.
It sets:
- `EDITOR_ASSISTANT_TEST_DB_DIR` to a temporary directory for the test session.

This is designed to prevent accidental writes to `~/.editor_assistant/`.

---

## API keys and unit tests

Important: `LLMClient.__init__()` requires the relevant API key environment variable to exist **at construction time** (even if you never call the network).

Therefore:
- **Unit tests** that construct `LLMClient` or `MDProcessor` must either:
  - Patch those constructors, or
  - Set a **dummy** env var inside the test/module (using `monkeypatch`)
- **Integration tests** that do real API calls should:
  - Use `pytest.mark.skipif(...)` when keys are not set
  - Also be marked `slow` and often `expensive`

We intentionally avoid setting dummy API keys globally in `conftest.py`, because that could unintentionally enable expensive integration tests.

---

## Common patterns used in this test suite

### 1) Patching (mocking) imports “where they are used”

When you patch something, patch the name in the module under test.

Example:
- `MDProcessor` imports `LLMClient` as `from .llm_client import LLMClient`
- Therefore tests patch `editor_assistant.md_processor.LLMClient` (not `editor_assistant.llm_client.LLMClient`)

### 2) Async mocks

If production code does `await client.generate_response(...)`, your mock must be awaitable:
- Use `AsyncMock(...)`

### 3) CLI tests: prefer `python -m ...`

Instead of relying on an installed console script, integration tests run:

```bash
python -m editor_assistant.cli --help
```

This works even if `editor-assistant` is not installed as a command.

---

## Where to add new tests

- Add **unit tests** to `tests/unit/`
- Add **integration tests** to `tests/integration/`
- Add **stress / concurrency tests** to `tests/stress/` and mark them `slow`

When adding a new module test, try to:
- Cover the “happy path”
- Add at least 1 boundary/edge case (empty input, invalid input, exception path)
- Make the test deterministic (avoid sleeping/timeouts unless the test is about timing)


