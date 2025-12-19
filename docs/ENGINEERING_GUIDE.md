# Engineering Guide (General)

This guide captures cross-project norms for humans and LLM agents. Project-specific details live in `DEVELOPER_GUIDE.md`.

## Branch & Commit Workflow
- Main stays green; feature branches per task (`feature/<name>` / `fix/<name>`). Rebase regularly onto main.
- Small, focused commits using `type: summary` (feat/fix/docs/test/chore/refactor).
- Before PR/merge: ensure relevant tests pass; resolve conflicts by rebasing.

## Testing & Reporting
- Run the minimal relevant suite: unit for logic changes; targeted integration for API/IO touches; document skipped cases and why.
- After tests: report what ran, failures/blocks, and fixes/mitigations applied.

## Documentation Expectations
- User-facing changes → `README.md`.
- Project-specific architecture/process → `DEVELOPER.md`.
- Release notes → `CHANGELOG.md` (`Unreleased` during development; move to a version on release).
- Keep CLI flags, defaults, env vars, and costs in sync across docs.

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

