# `auto_nobel_release.py`

`scripts/auto_nobel_release.py` 是用于收集诺贝尔奖网页、生成中文译文，并把多个模型译文合并为横向对照 Markdown 的本地实验模块。

仓库会忽略整个 `scripts/` 目录，因为其中包含本地实验和生成数据。因此，当前受支持的翻译入口是 `editor-assistant translate` CLI；准备好模块预期的本地目录后，仍可使用它的对照文件聚合功能。

## 模块内容

- `Field`：支持 `physics`、`chemistry`、`medicine` 三个奖项领域。
- `MediaCategory`：支持 summary、press release、popular information 和 advanced information 四类页面。
- `get_nobel_sources(year, prize_field)`：生成某年度、某领域的诺贝尔奖页面 URL。
- `translate_nobel_release(...)`：旧版批量翻译入口。它仍依赖已移除的同步 `process_batch` 接口，不能直接用于当前异步版本。
- `benchmark_nobel_release(year)`：读取本地原文及多个模型的译文，生成逐段横向对照文件。

## 翻译实验

所有模型必须使用同一份本地输入，才能比较延迟、token 用量和译文完整性。本轮使用完整 `press-release`，候选模型为：

| CLI 模型名 | Provider 模型 ID | 说明 |
| --- | --- | --- |
| `gemini-3.8-flash` | `gemini-3.8-flash` | Gemini 付费 API |
| `deepseek-v4-flash-preview-volc` | `deepseek-v4-flash-260425` | 火山引擎 V4 Flash Preview |
| `deepseek-v4-flash-ga-volc` | `deepseek-v4-flash-ga-260731` | 火山引擎 V4 Flash 正式版 |
| `deepseek-v3.2-volc` | `deepseek-v3-2-251201` | 火山引擎 V3.2，已进入迁移/下线范围 |
| `doubao-seed-2.1-lite` | `doubao-seed-2-1-lite-260915` | Doubao Seed 2.1 Lite |
| `doubao-seed-2.0-pro` | `doubao-seed-2-0-pro-260215` | Doubao Seed 2.0 Pro |
| `doubao-seed-2.0-lite` | `doubao-seed-2-0-lite-260428` | Doubao Seed 2.0 系列的 Lite 版本 |
| `doubao-seed-2.0-mini` | `doubao-seed-2-0-mini-260428` | Doubao Seed 2.0 Mini |

配置所需环境变量：

```bash
export GEMINI_API_KEY=...
export DEEPSEEK_API_KEY_VOLC=...
export DOUBAO_API_KEY=...
```

对可用模型分别执行翻译。`--no-stream` 避免控制台流式渲染干扰耗时比较，`--save-files` 保留译文和 token 报告。

```bash
uv run editor-assistant translate SOURCE --model gemini-3.8-flash --no-stream --save-files
uv run editor-assistant translate SOURCE --model deepseek-v4-flash-preview-volc --no-stream --save-files
uv run editor-assistant translate SOURCE --model deepseek-v4-flash-ga-volc --no-stream --save-files
uv run editor-assistant translate SOURCE --model deepseek-v3.2-volc --no-stream --save-files
uv run editor-assistant translate SOURCE --model doubao-seed-2.1-lite --no-stream --save-files
uv run editor-assistant translate SOURCE --model doubao-seed-2.0-pro --no-stream --save-files
uv run editor-assistant translate SOURCE --model doubao-seed-2.0-lite --no-stream --save-files
uv run editor-assistant translate SOURCE --model doubao-seed-2.0-mini --no-stream --save-files
```

CLI 会把 token 用量和模型处理时间写入 SQLite 历史记录：

```bash
uv run editor-assistant history -n 8
uv run editor-assistant show RUN_ID --output
```

2026-09-29 的实测输入、方法和结果见 [翻译性能实验报告](reports/translation_performance_2026-09-29.md)。V4 Preview、V4 GA、Doubao 2.1 Lite 和 Doubao 2.0 Lite 成功；2026-10-05 配置新 key 后 Gemini 3.8 Flash 补测成功。V3.2 迁移状态和未开通模型的失败结果也记录在报告中。

## 生成横向对照文件

`benchmark_nobel_release(year)` 需要以下本地目录结构：

```text
scripts/webpage/www.nobelprize.org/prizes/
├── chemistry/<year>/
│   ├── <original>.md
│   └── llm_generations/response_<original>_translate_<model>_<timestamp>.md
├── medicine/<year>/
└── physics/<year>/
```

然后运行：

```bash
uv run python scripts/auto_nobel_release.py
```

运行前需要在模块中同步以下两处固定配置：

- `__main__` 中的年度。
- `benchmark_nobel_release()` 中的 `selected_models` 和原文文件名映射。

## 结果解释限制

- 单次调用只能反映一次端到端延迟。稳定的延迟分布需要每个模型重复运行多次。
- Provider 的 tokenizer 不同，原始 token 数不能完全等价比较。
- 翻译质量仍需人工复核，至少检查遗漏、术语、数字、人名、Markdown 结构和段落对齐。
- 模型路由和价格可能变化。发布结果时应记录日期及 Provider 实际返回的模型标识。
