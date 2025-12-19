# Engineering Guide (General)

This guide captures cross-project norms for humans and LLM agents. Project-specific details live in `DEVELOPER_GUIDE.md`.

## Branch & Commit Workflow

- Main stays green; feature branches per task (`feature/<name>` / `fix/<name>`). Rebase regularly onto main.
- Small, focused commits using `type: summary` (feat/fix/docs/test/chore/refactor).
- Before PR/merge: ensure relevant tests pass; resolve conflicts by rebasing.

## Testing & Reporting

- Run the minimal relevant suite: unit for logic changes; targeted integration for API/IO touches; document skipped cases and why.
- After tests: report what ran, failures/blocks, and fixes/mitigations applied.
- Always check if current tests fully cover a new feature/fix/.. before diving into implementation. If not, update
test coverage before implementing.

## Documentation Expectations

- User-facing changes → `README.md`.
- Project-specific architecture/process → `DEVELOPER_GUIDE.md`.
- Release notes → `CHANGELOG.md` (`Unreleased` during development; move to a version on release).
- Keep CLI flags, defaults, env vars, and costs in sync across docs.

## Documentation Synchronization Protocol

**Context**: LLM Agents often implement code but forget to update the broader documentation context, leading to drift.
**Rule**: Documentation updates are NOT optional "chores". They are part of the "Definition of Done".

### The Sync Web

When you change **X**, you MUST update **Y**:

| If you change... | You MUST update... |
| :--- | :--- |
| **New Feature / Refactor** | 1. `FUTURE_ROADMAP.md` (Status: Pending -> In Progress -> Done) <br> 2. `TODO_<agent>.md` (Mark Complete) <br> 3. `CHANGELOG.md` (Add entry under Unreleased) |
| **CLI / Configuration** | 1. `README.md` (Usage examples) <br> 2. `DEVELOPER_GUIDE.md` (Module ref / Config) |
| **Project Structure** | 1. `DEVELOPER_GUIDE.md` (Architecture Overview) |
| **Dependencies** | 1. `pyproject.toml` <br> 2. `README.md` (Installation if changed) |

### Agent Protocol

1. **Pre-Implementation**: Check `FUTURE_ROADMAP.md` and `TODO_<agent>.md` to confirm scope.
2. **Implementation**: Write code + tests.
3. **Post-Implementation (Before Commit)**: 
   - Update `CHANGELOG.md`.
   - Update `README.md` if user-facing.
   - Update `DEVELOPER_GUIDE.md` if architecture changed.
   - Update `FUTURE_ROADMAP.md` status.
   - **Do not wait for a human to remind you.**

## Secrets & Safety

- No secrets in code or logs. Use env vars; prefer `.env` locally (not committed).
- Be explicit about paid API usage; default to the cheapest safe model for smoke/integration.

## LLM Agent Conduct

- Follow the defined scope; avoid speculative edits.
- Minimize blast radius: touch only necessary files; no drive-by refactors.
- When blocked by environment (network/SSL/quotas), surface the issue and skip gracefully.

## Code & Review Hygiene

- Type hints and small, testable functions.
- Keep failure modes explicit; avoid silent catches.
- Prefer Squash/Merge for clean history; tag releases after version bump + changelog update.

## Refactoring & Reliability Best Practices

When refactoring core logic (especially async/concurrency changes), verify against these high-level reliability patterns:

1.  **Incremental & Test-Driven (TDD)**:
    *   **Principle**: Work incrementally. Spend significantly more time designing sufficient tests (boundary conditions, stress, concurrency) than writing code.
    *   **Check**: Do NOT commit implementation code until the corresponding tests pass.

2.  **State Management & Isolation**:
    *   **Principle**: Long-lived objects (clients, processors) must not accumulate request-specific state (counters, buffers).
    *   **Check**: Verify that return values (e.g., usage stats, costs) reflect *only* the specific operation, not the object's lifetime history.

2.  **Configuration ExplicitNess**:
    *   **Principle**: Do not override user configuration with hidden defaults in code.
    *   **Check**: Explicitly test "negative" cases (e.g., flags set to `False` or omitted) to ensure they aren't forced to `True` by logic like `val = args.flag or True`.

3.  **Graceful Termination**:
    *   **Principle**: Systems must handle interruption signals (SIGINT/Ctrl+C) without leaving data in inconsistent states.
    *   **Check**: Ensure async tasks handle `CancelledError` to clean up resources or update persistence status (e.g., `pending` -> `aborted`) before exiting.

4.  **UX/IO Separation**:
    *   **Principle**: Separately manage structured UI output (TUI/Progress Bars) and unstructured logging.
    *   **Check**: When using rich terminal UIs, suppress or redirect standard INFO logs to prevent visual interference ("scrolling bugs").
