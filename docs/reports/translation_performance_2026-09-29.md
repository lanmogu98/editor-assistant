# 翻译性能实验报告（2026-09-29）

## 结论

本轮使用 Nobel Prize in Physics 2025 的完整 `press-release`，得到 5 组有效译文。2026-10-05 配置新的 key 后，`gemini-3.8-flash` 补测成功，API 处理时间为 22.51 秒。此前 2026-09-29 的单次实测中，`deepseek-v4-flash-preview-volc` 为 11.98 秒；`deepseek-v4-flash-ga-volc` 为 23.91 秒；`doubao-seed-2.1-lite` 为 64.41 秒；`doubao-seed-2.0-lite` 为 74.79 秒。

五份译文均覆盖到源文末尾，并保留全部 15 个 URL。Doubao 2.1 Lite 把多个 Markdown 空行合并，因而输出行数明显较少，但没有发现正文段落或链接缺失。Gemini 将原文的 particle-like system 译为“准粒子系统”，引入了原文未使用的专业概念，建议改为“类粒子系统”；完成全文不代表译文无需校对。

这些结果只能比较本次调用，不能代表稳定的延迟分布或翻译质量排名。实验没有显式指定 `--thinking`，因此每个模型使用 Provider 默认思考配置；不同模型的输出 token 也可能包含不同口径的思考 token。

## 实验设置

| 项目 | 值 |
| --- | --- |
| 日期 | 火山模型：2026-09-29；Gemini 补测：2026-10-05（Asia/Shanghai） |
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
| `gemini-3.8-flash` | `gemini-3.8-flash` | 22.51 s | 23.09 s | 1,942 | 1,894 | $0.008559 | 3,422 | 15/15 |

成本根据仓库中的静态单价和 API 返回 token 计算，不等同于 Provider 账单。Gemini 以美元计价，火山模型以人民币计价，不能直接比较表中的金额。存在分档价格时，应以控制台账单为准。

### 本次调用的相对表现

- V4 Flash Preview 的 API 时间约为 GA 的 50%，估算成本约低 26%。Preview 已进入迁移范围，生产基线仍应优先使用 GA。
- Doubao 2.1 Lite 比 2.0 Lite 快约 14%，但估算成本高约 15%。
- Doubao 2.0 Lite 是火山成功样本中估算成本最低的模型，也是最慢的模型。
- Gemini 的本次 API 时间接近 V4 Flash GA，但两者测量日期不同，不能据此断定稳定速度差异。
- 未进行盲评或参考译文打分。五份译文都覆盖全文，但人名音译、机构名、术语和排版仍需人工复核。

## 未产生完整译文的候选模型

| 候选模型 | 实测结果 | 解释 |
| --- | --- | --- |
| `deepseek-v3.2-volc` | `404 InvalidEndpointOrModel.NotFound` | `deepseek-v3-2-251201` 已进入迁移/下线范围，当前账号无法调用 |
| `doubao-seed-2.0-pro` | `404 InvalidEndpointOrModel.NotFound` | `doubao-seed-2-0-pro-260215` 不存在或当前账号无权调用 |
| `doubao-seed-2.0-mini` | `404 ModelNotOpen` | 当前账号未开通 `doubao-seed-2-0-mini-260428` |
| Doubao 2.0 Lite/Mini 旧版 | `404 InvalidEndpointOrModel.NotFound` | `*-260215` 旧版不存在或当前账号无权调用 |

火山引擎的迁移文档已把 `deepseek-v3-2-251201` 和 `deepseek-v4-flash-260425` 指向 `deepseek-v4-flash-ga-260731`。因此当前环境无法完成 V3.2 与 V4 的有效实测对比；这不是翻译流程错误。

## Gemini key 验证

2026-09-29，旧环境中的 `GEMINI_API_KEY` 分别通过以下两种调用方式验证，均返回 `400 API_KEY_INVALID`：

1. Gemini OpenAI 兼容接口，使用 `Authorization: Bearer ...`。
2. Gemini 原生 API，使用 `x-goog-api-key: ...`。

2026-10-05，用户重新配置 key 后，当前进程通过 Gemini OpenAI 兼容接口发送最小请求，返回 HTTP 200 和 `OK`。随后现有 CLI 使用同一 Bearer 鉴权完成了全文翻译。因此，新 key 已确认可用，无需修改客户端鉴权方式。之前失败究竟来自旧进程环境还是旧 key 权限，本轮无法追溯确定。

官方参考：

- [Gemini API keys](https://ai.google.dev/gemini-api/docs/api-key)
- [Gemini OpenAI compatibility](https://ai.google.dev/gemini-api/docs/openai)
- [Google Cloud API keys](https://docs.cloud.google.com/docs/authentication/api-keys)
- [火山引擎模型列表](https://docs.volcengine.com/docs/ark/model-list?lang=zh)
- [火山引擎模型迁移指南](https://docs.volcengine.com/docs/ark/model-deprecation-migration-guide?lang=en)

## 有效性限制与下一轮建议

- 每个成功模型只有 1 次样本，不能估计均值、P50、P95 或波动范围。
- Gemini 在 2026-10-05 补测，其余有效样本测于 2026-09-29，服务负载与模型服务状态可能不同。
- Provider 的 tokenizer、思考 token 和计费口径不同，原始 token 数不能直接代表译文长度。
- 本轮只验证内容覆盖和 Markdown 结构，没有独立参考译文或人工盲评。
- Preview 与已迁移模型的可用性会变化，后续实验必须保留 Provider 模型 ID 和日期。

建议在同一时段对每个可用模型串行运行至少 5 次，再报告成功率、P50、P95、实际账单成本和人工盲评结果。
