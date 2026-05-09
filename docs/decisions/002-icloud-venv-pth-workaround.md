# ADR 002: Move Project Off iCloud Drive to Fix Python venv

## Status

Accepted (2026-03-27)

## Context

After migrating to uv-managed Python (commit `6ee1a11`), the project
was completely non-functional: all imports, tests, and CLI entry points
failed with `ModuleNotFoundError`.

**Root cause**: The project lived on iCloud Drive
(`~/Library/Mobile Documents/com~apple~CloudDocs/`). macOS sets the
`UF_HIDDEN` file flag on iCloud-synced files. Python 3.13's `site.py`
(lines 177-180) skips `.pth` files that have this flag:

```python
if ((getattr(st, 'st_flags', 0) & stat.UF_HIDDEN) or
    (getattr(st, 'st_file_attributes', 0) & stat.FILE_ATTRIBUTE_HIDDEN)):
    _trace(f"Skipping hidden .pth file: {fullname!r}")
    return
```

This meant the editable install's `.pth` file (which adds `src/` to
`sys.path`) was never processed. The `chflags nohidden` workaround was
ineffective because iCloud re-applies the flag.

A secondary issue: `src/editor_assistant/__init__.py` had never existed,
so even when the path was manually added, `import editor_assistant`
yielded a namespace package without `__version__`.

## Decision

1. **Move the project** from iCloud Drive to `~/Projects/tools/editor-assistant/`.
2. **Create `src/editor_assistant/__init__.py`** to make it a proper
   package with `__version__` re-exported from `config/__init__.py`.

## Consequences

- Python venvs created by uv work correctly (no hidden flag interference).
- The project is no longer auto-synced via iCloud; use git for backup.
- CI environments (Linux) were never affected.
- Future Python projects should avoid iCloud Drive for the same reason.
