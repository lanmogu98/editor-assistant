# Issue #31 Qwen/Bailian Catalog Decision

## Status and scope

This record implements the maintainer-approved minimal, non-thinking refresh on
2026-07-22. Editor Assistant adds no Qwen models and retains only the existing
logical key `qwen3.6-flash`. Public documentation mentioning a model is evidence
to consider, not authorization to add it.

Editor Assistant issue
[20](https://github.com/lanmogu98/editor-assistant/issues/20) and
`llm-exec-core` issue
[23](https://github.com/lanmogu98/llm-exec-core/issues/23) are related-only.
Neither is a prerequisite, blocker, parent, or child of Issue #31.

## Release provenance

| Evidence | Verified value |
|---|---|
| Core release | https://github.com/lanmogu98/llm-exec-core/releases/tag/0.4.1 |
| Annotated tag | `refs/tags/0.4.1` -> tag `8e8e0a0813dccd068158cbe05bc22d3298f935f9` -> commit `3014b4b09f2f40db9820fac1f39e6f7c308fb654` |
| Wheel | https://github.com/lanmogu98/llm-exec-core/releases/download/0.4.1/llm_exec_core-0.4.1-py3-none-any.whl — 24,243 bytes; SHA-256 `30dbc41afa29cf1e74d572703a93111f65ab7581eae4d69d739fe292d007e6f7` |
| Source distribution | https://github.com/lanmogu98/llm-exec-core/releases/download/0.4.1/llm_exec_core-0.4.1.tar.gz — 26,059 bytes; SHA-256 `4a9f253fc7dae692358e958a7c5bf032d741d4f3afb135a147aa0f229df37662` |
| Installed artifacts | Wheel and sdist independently install offline as `llm-exec-core==0.4.1` on Python 3.13 and declare `Requires-Python >=3.10`. |
| Released core catalog | Public source, wheel, sdist, and isolated installations contain byte-identical `llm_config.yml`, SHA-256 `490c5df6988c43b65badf28f75a8507e09c11505a2d4f47ecb2bda42984abfd4`. |
| Refreshed editor catalog | Editor Assistant owns its complete 21-model catalog; the post-refresh `llm_config.yml` SHA-256 is `65b97a4b5c9fa6f25b58b99e3f7919c5a14e7fb1a858f1a18fa92b7c56c421b7`. |

The annotated tag and GitHub Release assets are the publication provenance; no
PyPI publication is assumed. Local development intentionally keeps the sibling
editable source while the built editor distribution declares
`llm-exec-core>=0.4.1,<0.5.0`.

## Accepted runtime policy

| Dimension | Decision |
|---|---|
| Logical/outbound model | `qwen3.6-flash` -> `qwen3.6-flash` |
| Model set | Exactly one Qwen key; no add, remove, alias, or remap |
| Context/output | `1000000` context; `65536` maximum output |
| Token field | `max_tokens`; accepted by the current Chat API but marked for future deprecation in favor of `max_completion_tokens` |
| Thinking | Always send `enable_thinking: false`; no `reasoning_effort` mapping; `reasoning_controls: []` |
| Credentials | `QWEN_API_KEY` first, then `DASHSCOPE_API_KEY` |
| Endpoint | `QWEN_API_BASE_URL` accepts an SDK `/v1` base or complete `/chat/completions`; the legacy complete Beijing endpoint remains the fallback |
| Structured output | JSON object supported; strict JSON-schema enforcement not claimed |
| Tools | Tools, streaming tool output, tool choice, and parallel tool calls supported in the selected non-thinking mode |

## Post-publication evidence and candidate decisions

All sources were re-fetched on 2026-07-22 (Asia/Shanghai). No page
representation hash or authenticated console evidence is used.

| Candidate | Official source | Date | Supported fact | Disposition | Compatibility note and evidence limitation |
|---|---|---|---|---|---|
| `qwen3.6-flash` | https://help.aliyun.com/en/model-studio/text-generation-model/ and https://help.aliyun.com/en/model-studio/vision-model/ | 2026-07-22 | Current lightweight alias; maps to `qwen3.6-flash-2026-04-16`; 1M context and 64K maximum output; not listed for retirement | **Retain with limitation** | Keep the stable logical ID and force non-thinking. Flat pricing is not authoritative. |
| `qwen3.6-flash-2026-04-16` | https://help.aliyun.com/en/model-studio/text-generation-model/ | 2026-07-22 | Dated snapshot behind the retained alias | **Omit** | Adding a snapshot would expand the public catalog without an accepted compatibility need. |
| Qwen3.8 aliases, previews, and dated variants (`qwen3.8-*`) | https://help.aliyun.com/en/model-studio/text-generation-model/ | 2026-07-22 | Refreshed sources surface newer Qwen candidates | **Omit** | Newness does not override the accepted one-model scope; complete flat pricing is not representable. |
| Qwen3.7 Max/Plus aliases, previews, and dated variants (`qwen3.7-*`) | https://help.aliyun.com/en/model-studio/text-generation-model/ and https://help.aliyun.com/zh/model-studio/model-pricing | 2026-07-22 | Official current/dated candidates with differing thinking and pricing characteristics | **Omit** | Promotions, modes, snapshots, and pricing dimensions cannot be represented as one universal flat rate. |
| Qwen3.6 Plus/Max aliases and snapshots (`qwen3.6-plus*`, `qwen3.6-max*`) | https://help.aliyun.com/en/model-studio/text-generation-model/ and https://help.aliyun.com/zh/model-studio/model-pricing | 2026-07-22 | Official family candidates | **Omit** | Not current app keys; adding them would broaden scope and their pricing is dimensioned. |
| Qwen3.5 candidates (`qwen3.5-*`) | https://help.aliyun.com/en/model-studio/text-generation-model/ and https://help.aliyun.com/en/model-studio/vision-model/ | 2026-07-22 | Legacy aliases and snapshots remain documented | **Omit** | Documentation presence alone is not an add decision; tiered pricing remains unrepresentable. |
| `qwen3-max`, previews, `latest`, and dated variants | https://help.aliyun.com/en/model-studio/text-generation-model/ and https://www.alibabacloud.com/help/en/model-studio/model-depreciation | 2026-07-22 | Legacy family with lifecycle constraints | **Omit** | Do not reintroduce absent legacy keys or encode lifecycle-sensitive aliases. |
| `qwen-max`, `latest`, and dated variants | https://help.aliyun.com/en/model-studio/text-generation-model/ | 2026-07-22 | Legacy family; thinking behavior differs from retained Qwen3.6 policy | **Omit** | No current app key and no verified need to restore one. |
| `qwen-plus`, `latest`, and dated variants | https://help.aliyun.com/en/model-studio/text-generation-model/ and https://help.aliyun.com/zh/model-studio/model-pricing | 2026-07-22 | Legacy family with tier- and mode-dependent pricing | **Omit** | No alias remap is inferred; flat schema cannot represent current billing. |
| `qwen-turbo`, `latest`, and dated variants | https://help.aliyun.com/en/model-studio/text-generation-model/ and https://help.aliyun.com/en/model-studio/deep-thinking | 2026-07-22 | Legacy family with mode-dependent behavior and pricing | **Omit** | No evidence requires `qwen-turbo` -> `qwen-turbo-latest`; do not restore or remap it. |

Capability-specific sources:

- Non-thinking and explicit `enable_thinking: false`:
  https://help.aliyun.com/en/model-studio/deep-thinking
- JSON-object output without strict schema:
  https://help.aliyun.com/en/model-studio/qwen-structured-output
- Function Calling, tool choice, parallel calls, and streaming tool output:
  https://help.aliyun.com/en/model-studio/qwen-function-calling
- OpenAI-compatible Chat fields, including the `max_tokens` lifecycle note:
  https://help.aliyun.com/en/model-studio/qwen-api-via-openai-chat-completions
- Key and endpoint compatibility:
  https://help.aliyun.com/zh/model-studio/compatibility-of-openai-with-dashscope
- Batch scope and limitations:
  https://help.aliyun.com/en/model-studio/batch-inference
- English pricing cross-check:
  https://www.alibabacloud.com/help/en/model-studio/model-pricing
- General text-generation behavior:
  https://help.aliyun.com/en/model-studio/text-generation

## Pricing limitation

The retained `¥0.30` input and `¥0.60` output values are historical,
non-authoritative compatibility placeholders. They are not current Qwen3.6
Flash rates and must not be used as a billing quote. Official billing varies by
region/deployment, input-token tier, cache behavior, Batch eligibility, and
thinking mode. The shared flat `input`/`output` schema cannot encode those
dimensions. No currency conversion or single tier is promoted to a universal
rate; schema work remains related-only `llm-exec-core` issue 23.

## Compatibility, risk, and rollback

- `QWEN_API_KEY` and the legacy complete endpoint remain backward-compatible.
  `DASHSCOPE_API_KEY` and `QWEN_API_BASE_URL` are additive fallbacks.
- Explicit `enable_thinking: false` intentionally changes request semantics for
  this model from provider-default thinking to deterministic non-thinking.
- The dependency moves to the compatible 0.4 line and excludes 0.5. Public app
  import paths remain unchanged.
- Historical flat prices can produce inaccurate cost estimates; callers must
  treat them as non-authoritative until the related pricing schema lands.

### Rollback

Use a focused revert PR restoring the dependency/lock, Qwen block, tests, and
documentation together from editor base
`841c8efa07ba3434f5e5b726d0847be28c567ae5`. Keep app catalog ownership intact.
If official evidence becomes stale or contradictory before merge, return Issue
#31 to research rather than guessing.
