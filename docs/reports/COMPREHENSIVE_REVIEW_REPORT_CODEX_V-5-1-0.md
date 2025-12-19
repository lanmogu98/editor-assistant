# Comprehensive Review Report (Codex v5.1.0)

Scope: System review of correctness, robustness, extensibility, and performance on branch `review/system-audit-codex` (baseline `origin/main`).

## Findings & Recommendations

1) Documentation drift (config/constants) — Medium  
- Issue: `DEVELOPER_GUIDE.md` still references single `CHAR_TOKEN_RATIO` and lacks the current language-aware token estimation and `OUTPUT_TOKEN_RESERVE` behavior.  
- Impact: New contributors may tune wrong values, mis-estimate context budgets, or reintroduce magic numbers.  
- Recommendation: Update the guide’s Configuration section to match `config/constants.py` and `utils.py`, and document the Chinese/English token heuristic and output reserve logic.

2) Cache correctness & accounting — Medium  
- Issue: `LLMClient.ResponseCache` keys on `prompt+model` only; it ignores `request_overrides` (e.g., thinking_level, temperature) and returns `usage=0`, bypassing cost/token accounting on cache hits.  
- Impact: May serve responses generated under different overrides; stats/DB cost can be understated when caching is enabled.  
- Recommendation: Include overrides in the cache key (e.g., sorted overrides JSON) and record “cached-hit” metadata instead of zeroing usage, or disable caching by default for requests with overrides.

3) Context budgeting is static and model-agnostic — Medium  
- Issue: `check_context_budget` reserves `PROMPT_OVERHEAD_TOKENS` (10k) and `OUTPUT_TOKEN_RESERVE` (min with half of context). For small/context-limited models this can reject valid inputs or leave too little room; not configurable per model/task.  
- Impact: False rejections and inefficient context use on smaller models or shorter prompts.  
- Recommendation: Make reserves model-aware (derive from `provider_settings.max_tokens`/`context_window` and task output expectations), and expose config for overrides; document defaults.

4) Schema versioning unused — Medium  
- Issue: `SCHEMA_VERSION`/`schema_version` table exists, but there is no migration or version check before use.  
- Impact: Future schema changes may silently operate on outdated tables, leading to runtime errors or missing columns.  
- Recommendation: Add a version check on startup and lightweight migrations (DDL `ALTER` steps) or fail fast with an actionable message.

5) Input deduplication collisions on empty/short content — Low  
- Issue: `RunRepository.get_or_create_input` hashes `content`; empty or failed conversions hash to the same value, merging distinct inputs.  
- Impact: Different failing inputs collapse to one record, skewing history and run-input relationships.  
- Recommendation: For empty/None content, fall back to hashing `(source_path + timestamp)` or store a sentinel to avoid cross-input collisions.

## Overall Assessment
- Architecture: Async pipeline and pluggable tasks are in place; storage and CLI wiring are consistent.  
- Robustness: Basic retry/rate-limit guards exist; DB writes are offloaded to threads.  
- Extensibility: Task registry and prompt loaders are clean; storage schema supports multi-input/multi-run, but migrations are missing.  
- Performance: No glaring hotspots, but context budgeting could be more adaptive; cache safety needs tightening before enabling by default.

