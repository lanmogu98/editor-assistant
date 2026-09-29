# 翻译性能实验报告（2026-09-29）

## 结论

本轮三模型实验只得到一组有效性能数据：`deepseek-v4-flash` 成功完成翻译；`gemini-3.8-flash` 被无效 API key 阻塞；`doubao-seed-2.0-lite` 被方舟账户未开通该模型阻塞。因此，本轮不能形成有效的三模型性能排名。

DeepSeek 的成功结果保持了 49 行输入对应 49 行输出，保留了标题、链接、图片、引用和奖项份额等 Markdown 结构。关键获奖理由译为“发现电路中的宏观量子力学隧穿和能量量子化”，未发现内容遗漏。人名音译仍建议按正式中文资料人工复核。

## 实验设置

| 项目 | 值 |
| --- | --- |
| 日期 | 2026-09-29（Asia/Shanghai） |
| 输入 | Nobel Prize in Physics 2025 summary |
| 来源 | <https://www.nobelprize.org/prizes/physics/2025/summary/> |
| 本地输入 | `scratch/translation-benchmark-2026-09-29/nobel-physics-2025-summary.md` |
| 输入规模 | 1,506 字符，49 行 |
| 任务 | 英文到中文，保留 Markdown 结构 |
| 调用方式 | 串行、非流式、同一份本地输入 |
| 独立数据库 | `scratch/translation-benchmark-2026-09-29/db/runs.db` |

所有调用均使用：

```bash
uv run editor-assistant translate SOURCE --model MODEL --no-stream --save-files
```

## 结果

| 模型 | 状态 | API 处理时间 | 墙钟时间 | 输入 token | 输出 token | 输出字符 | 结构完整性 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `gemini-3.8-flash` | 失败：API key 无效 | — | 6.08 s | — | — | — | 无输出 |
| `deepseek-v4-flash` | 成功 | 15.58 s | 16.04 s | 604 | 3,499 | 1,011 | 49/49 行 |
| `doubao-seed-2.0-lite` | 失败：模型未开通 | — | 3.91 s | — | — | — | 无输出 |

DeepSeek 的本地 token 报告给出 `¥0.007602` 估算值，但该值来自仓库内的静态兼容价格，不能作为本轮 Provider 实际账单。DeepSeek 官方说明 `deepseek-v4-flash` 已成为兼容别名，请求实际由 V4.1 Flash 提供服务，且当前价格按峰谷时段变化。

## 失败原因与复测条件

### Gemini

API 连续三次返回 `400 INVALID_ARGUMENT`，消息为 `Please pass a valid API key`。复测前需要替换当前 `GEMINI_API_KEY`，无需修改模型目录或命令。

### Doubao

API 连续三次返回 `404 ModelNotOpen`。当前方舟账户尚未开通 `doubao-seed-2-0-lite-260428`。复测前需要在方舟控制台开通该模型，或由用户明确选择已开通的 Doubao Seed 2.x 具体版本。

## 有效性限制

- 当前只有一次 DeepSeek 成功样本，不能估计均值、P50、P95 或波动范围。
- 三个 Provider 的 token 统计口径可能不同。
- 输入是较短的网页 summary，不能代表长文档吞吐和上下文稳定性。
- 本轮只检查完整性和明显语义错误，没有独立参考译文，也没有盲评。

完成凭据和模型开通后，建议每个模型至少串行运行 5 次，再报告成功率、延迟中位数、P95、token 用量、实际账单成本及人工盲评结果。
