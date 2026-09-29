# 翻译性能实验报告（2026-09-29）

## 结论

本轮使用 Nobel Prize in Physics 2025 的完整 `press-release`，得到 4 组有效译文。单次实测中，`deepseek-v4-flash-preview-volc` 最快，API 处理时间为 11.98 秒；`deepseek-v4-flash-ga-volc` 为 23.91 秒；`doubao-seed-2.1-lite` 为 64.41 秒；`doubao-seed-2.0-lite` 为 74.79 秒。

四份译文均覆盖到源文末尾，并保留全部 15 个 URL。Doubao 2.1 Lite 把多个 Markdown 空行合并，因而输出行数明显较少，但没有发现正文段落或链接缺失。

这些结果只能比较本次调用，不能代表稳定的延迟分布或翻译质量排名。实验没有显式指定 `--thinking`，因此每个模型使用 Provider 默认思考配置；不同模型的输出 token 也可能包含不同口径的思考 token。

## 实验设置

| 项目 | 值 |
| --- | --- |
| 日期 | 2026-09-29（Asia/Shanghai） |
| 输入 | Nobel Prize in Physics 2025 press release |
| 来源 | <https://www.nobelprize.org/prizes/physics/2025/press-release/> |
| 本地输入 | `scratch/translation-benchmark-2026-09-29/nobel-physics-2025-press-release.md` |
| 输入规模 | 6,732 字符，837 个英文词，103 行 |
| CLI 处理内容 | 7,508 字符（包含标题和来源元数据） |
| 任务 | 英文到中文，保留 Markdown 结构 |
| 调用方式 | 串行、非流式、每个模型 1 次、Provider 默认思考配置 |
| 独立数据库 | `scratch/translation-benchmark-2026-09-29/press-release-db/runs.db` |

成功样本均使用同一条命令，仅替换模型名：

```bash
uv run editor-assistant translate SOURCE --model MODEL --no-stream --save-files
```

## 有效样本

| CLI 模型名 | Provider 模型 ID | API 时间 | 墙钟时间 | 输入 token | 输出 token | 估算成本 | 输出字符 | URL |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `deepseek-v4-flash-preview-volc` | `deepseek-v4-flash-260425` | 11.98 s | 12.49 s | 1,736 | 1,532 | ¥0.009498 | 3,328 | 15/15 |
| `deepseek-v4-flash-ga-volc` | `deepseek-v4-flash-ga-260731` | 23.91 s | 24.41 s | 1,815 | 2,242 | ¥0.012811 | 3,105 | 15/15 |
| `doubao-seed-2.1-lite` | `doubao-seed-2-1-lite-260915` | 64.41 s | 64.84 s | 1,929 | 5,085 | ¥0.007636 | 3,223 | 15/15 |
| `doubao-seed-2.0-lite` | `doubao-seed-2-0-lite-260428` | 74.79 s | 75.32 s | 1,932 | 3,378 | ¥0.006660 | 3,297 | 15/15 |

成本根据仓库中的静态单价和 API 返回 token 计算，不等同于火山引擎账单。火山模型存在分档价格时，应以控制台账单为准。

### 本次调用的相对表现

- V4 Flash Preview 的 API 时间约为 GA 的 50%，估算成本约低 26%。Preview 已进入迁移范围，生产基线仍应优先使用 GA。
- Doubao 2.1 Lite 比 2.0 Lite 快约 14%，但估算成本高约 15%。
- Doubao 2.0 Lite 是本轮估算成本最低的成功模型，也是最慢的模型。
- 未进行盲评或参考译文打分。四份译文都完整，但人名音译、机构名、术语和排版仍需人工复核。

## 未产生完整译文的候选模型

| 候选模型 | 实测结果 | 解释 |
| --- | --- | --- |
| `gemini-3.8-flash` | `400 API_KEY_INVALID` | OpenAI 兼容接口和原生 `x-goog-api-key` 请求均拒绝当前进程读取到的 key |
| `deepseek-v3.2-volc` | `404 InvalidEndpointOrModel.NotFound` | `deepseek-v3-2-251201` 已进入迁移/下线范围，当前账号无法调用 |
| `doubao-seed-2.0-pro` | `404 InvalidEndpointOrModel.NotFound` | `doubao-seed-2-0-pro-260215` 不存在或当前账号无权调用 |
| `doubao-seed-2.0-mini` | `404 ModelNotOpen` | 当前账号未开通 `doubao-seed-2-0-mini-260428` |
| Doubao 2.0 Lite/Mini 旧版 | `404 InvalidEndpointOrModel.NotFound` | `*-260215` 旧版不存在或当前账号无权调用 |

火山引擎的迁移文档已把 `deepseek-v3-2-251201` 和 `deepseek-v4-flash-260425` 指向 `deepseek-v4-flash-ga-260731`。因此当前环境无法完成 V3.2 与 V4 的有效实测对比；这不是翻译流程错误。

## Gemini key 验证

当前进程中的 `GEMINI_API_KEY` 已分别通过以下两种官方调用方式验证：

1. Gemini OpenAI 兼容接口，使用 `Authorization: Bearer ...`。
2. Gemini 原生 API，使用 `x-goog-api-key: ...`。

两种方式均返回 `400 API_KEY_INVALID`。这说明问题不在 Editor Assistant 当前使用的 Bearer header；更可能是 Codex 进程仍持有轮换前的环境变量，或新 key 尚不能用于该 Gemini API。轮换环境变量后需要重启或重新载入当前 Codex 进程，再做同一最小请求复测。

官方参考：

- [Gemini API keys](https://ai.google.dev/gemini-api/docs/api-key)
- [Gemini OpenAI compatibility](https://ai.google.dev/gemini-api/docs/openai)
- [Google Cloud API keys](https://docs.cloud.google.com/docs/authentication/api-keys)
- [火山引擎模型列表](https://docs.volcengine.com/docs/ark/model-list?lang=zh)
- [火山引擎模型迁移指南](https://docs.volcengine.com/docs/ark/model-deprecation-migration-guide?lang=en)

## 有效性限制与下一轮建议

- 每个成功模型只有 1 次样本，不能估计均值、P50、P95 或波动范围。
- Provider 的 tokenizer、思考 token 和计费口径不同，原始 token 数不能直接代表译文长度。
- 本轮只验证内容覆盖和 Markdown 结构，没有独立参考译文或人工盲评。
- Preview 与已迁移模型的可用性会变化，后续实验必须保留 Provider 模型 ID 和日期。

Gemini key 在新进程中验证通过后，建议把 Gemini 加入同一输入，并对每个可用模型串行运行至少 5 次，再报告成功率、P50、P95、实际账单成本和人工盲评结果。
