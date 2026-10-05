# Doubao fast 真实翻译实验验证报告

## 结论

2026-10-05 使用真实方舟 Chat API，经 Editor Assistant 的 CLI 参数解析与 translate handler 完成 6 次指定 Nobel 页面全文翻译。3 次请求 fast 的所有 SSE 档位字段均为 fast；3 次未指定档位的响应均为 default。所有请求 HTTP 200、单次成功、finish_reason=stop，收到 [DONE]，未出现重试或降级。

本组样本的 API 总耗时中位数：默认 107.769 秒，fast 73.652 秒，减少 31.66%。这是样本观测结果。每档仅 3 次，且后两次 fast 的输入缓存命中与默认组不同，不能将全部差异严格归因于服务档位，也不能作为其他负载的延迟承诺。

首组两个请求的缓存命中均为 0：默认 109.356 秒、fast 73.111 秒，减少 33.14%；fast 此次生成的 token 更多。因此，至少在这个无缓存的直接对照中，fast 确实触发且完成更快。

## 实验对象、版本与执行环境

- 原页面：https://www.nobelprize.org/prizes/medicine/2025/popular-information/
- 抓取时间：2026-10-05T07:58:15.223768+00:00；HTTP 200。
- 模型：doubao-seed-2.1-lite → `doubao-seed-2-1-lite-260915`。
- 实际 API：`https://ark.cn-beijing.volces.com/api/v3/chat/completions`。
- Python 3.13.12；平台：macOS-27.0.1-arm64-arm-64bit-Mach-O。
- 应用执行版本：`2c7fe5af23c0f5de5752f5b20d1a7fbde2fdda1b`。
- core 执行版本：0.4.2，`e30ba2afb462089850c05614bbd62ab154dd5e10`；配套 PR：https://github.com/lanmogu98/llm-exec-core/pull/52。
- core 分支已重基到当前 main；未包含之前那份无关架构设计文档。
- 实验后仅将 RunRepository.create_run 的 currency 类型声明扩宽为 Optional[str]，匹配当前 core 对未知币种的表示；数据库本就允许 NULL。此兼容修正不改变实验请求或运行逻辑。

## 冻结输入与对照方法

使用包内 CleanHTML2Markdown 的 readabilipy 提取器从下载的 HTML 获取正文，冻结为本地 Markdown。下载、提取一次完成，六次翻译读取完全相同的文件，避免网页网络耗时和正文漂移影响 API 对照。未使用短节选或缩短任务。

输入含 19174 字符、2971 个按正则统计的英文词、172 行、13 个标题。正文包含研究背景、人物、实验、技术术语、参考文献与署名；检查 FOXP3、CD25、Key publications 等定位锚点。

冻结 Markdown SHA-256：`a2bd522645d170a980aba451e37b4470c7e03bb99bd718b3db7e878806eea75a`。

- 顺序：default → fast → fast → default → default → fast，组成 3 组对照。
- 模型与翻译 prompt 相同；temperature=0.6、max_tokens=32000、reasoning_effort=low（CLI --thinking low）、stream=true、include_usage=true。
- 默认组不传 service_tier；fast 组使用 CLI --service-tier fast。
- 六个发送 JSON 去掉 service_tier 后的指纹完全一致，已由离线脚本核对。
- 串行执行，无并发请求；每次独立子进程与 HTTP client，无客户端连接复用。
- 标准 CLI parser 和 translate handler 调用真实 core/httpx。实验只通过 event_hooks 添加观察器，没有 MockTransport、伪造响应或改写请求。
- 每次独立 scratch 数据库，分别核对 CLI 保存的 requested tier 与 API 实际返回的 served tier；二者不是同一字段。

## 指标定义

所有网络指标用 perf_counter，从 httpx request hook 到对应响应事件计时。它们包含实际网络、TLS、排队及推理，不是服务端 GPU 内部计时。

| 指标 | 定义 |
|---|---|
| first_token_s | 首个非空 reasoning_content 或 content 到达 |
| first_content_s | 首个正文 content 到达，用户开始看到译文 |
| api_s | 请求发出至接收到 [DONE] |
| handler_s | CLI parser/handler 到关闭 client、持久化完成；不含进程导入启动 |
| decode_tokens_s | completion_tokens ÷ (api_s − first_token_s)，包含思考 token |
| visible_chars_s | 正文字数 ÷ (末个正文片段时间 − 首个正文片段时间) |

速率是网络观测的有效吞吐，首个片段的长度与 chunk 粒度会造成小偏差。服务端返回的 token 数用于统计，未使用客户端估算 token。

## 六次完整结果

| 顺序 | 实际档位 | 首 token 秒 | 正文首字秒 | API 秒 | 输入/缓存 token | 输出/思考 token | 正文字数 |
|---|---|---:|---:|---:|---:|---:|---:|
| 01-default | default | 0.875 | 66.576 | 109.356 | 5607/0 | 9564/5159 | 8276 |
| 02-fast | fast | 0.709 | 45.434 | 73.111 | 5607/0 | 10531/5919 | 8871 |
| 03-fast | fast | 0.391 | 46.499 | 73.652 | 5607/5607 | 10685/6133 | 8113 |
| 04-default | default | 0.838 | 65.285 | 103.251 | 5607/0 | 10472/5933 | 8009 |
| 05-default | default | 0.746 | 67.381 | 107.769 | 5607/0 | 10849/6350 | 7891 |
| 06-fast | fast | 0.264 | 59.968 | 85.528 | 5607/5607 | 12398/7857 | 7902 |

## 汇总与缓存影响

| 中位数指标 | 默认 | fast | 变化 |
|---|---:|---:|---:|
| 首 token | 0.838 秒 | 0.391 秒 | 减少 53.30% |
| 正文首字 | 66.576 秒 | 46.499 秒 | 减少 30.16% |
| API 总耗时 | 107.769 秒 | 73.652 秒 | 减少 31.66% |
| CLI handler 耗时 | 107.880 秒 | 73.771 秒 | 减少 31.62% |
| 含思考的有效吞吐 | 101.37 token/s | 145.45 token/s | 增加 43.48% |
| 正文输出速率 | 195.38 字符/s | 309.15 字符/s | 增加 58.23% |

fast 总耗时范围 73.111–85.528 秒；默认 103.251–109.356 秒。三组 fast 均比对应默认请求快。fast 的输出 token 中位数 10685，默认 10472，fast 的思考 token 中位数也更高，不能以生成更少来解释这组耗时差异。

03-fast 与 06-fast 返回 cached_tokens=5607，其余请求为 0。客户端streaming 路径不使用本地 response cache；这个命中来自服务端。不能假设缓存完全无影响，也未尝试修改账号缓存配置。无缓存首组单独支持触发与更快的结论；要精确隔离档位本身的收益，还需控制服务端缓存的更大样本实验。

fast 组有思考 token 的波动，06-fast 的 7857 个思考 token 拉长正文首字和总耗时。首 token 与首正文必须分别看：首 token 小于 1 秒不表示正文已开始翻译。这次参数 low 仍产生长思考；未验证 disabled thinking 的性能。

总输入 token 33642，总输出 token 64499（包含思考）。已有 app 平面估价不能证明 fast 的真实费用，本报告不以该估价作为账单。

## 输出与证据核对

verify_recordings.py 已逐次从原始 SSE 重建正文，并与 CLI 写入数据库、导出的 main.md 做全文相等校验。档位集合、首 token、首正文、末正文、[DONE] 时间和最后 usage 均与逐次 JSON 完全一致。response-evidence.json 保留服务端事件的 ID、模型、实际档位和 usage，不包含请求鉴权头。

六份译文均有 13 个标题、89 个非空行，保留 FOXP3、CD4、CD25、IPEX，没有输出截断。这个结构检查不等同于人工逐句翻译质量评审。

| 请求 | 总行数 | 非空行 | 标题 | 中文字符 |
|---|---:|---:|---:|---:|
| 01-default | 159 | 89 | 13 | 4280 |
| 02-fast | 171 | 89 | 13 | 4398 |
| 03-fast | 171 | 89 | 13 | 4628 |
| 04-default | 172 | 89 | 13 | 4560 |
| 05-default | 171 | 89 | 13 | 4536 |
| 06-fast | 171 | 89 | 13 | 4658 |

原文 172 行。01-default 的 159 行主要反映空行数量差异；其他译文为 171 或 172 行。现有 bilingual 后处理按行位置配对，空行差异会影响双语对应，不能据非空行相同宣称双语格式严格对齐。这属于翻译输出格式限制，本实验未扩大范围修改后处理。

## 局限与适用范围

只有一个账号、模型版本、文章、地区与时间窗口，每档 3 个样本。未做显著性检验、p95/p99 或高峰期压测，也未宣称其他模型已有实测结果。观察器会写本地 trace，开销同样作用于两组；没有测量其绝对开销。

证据支持：实际命中了 fast；本任务的这组 fast 请求均更快。证据不支持：任何负载固定减少 31.66%、账号永不降级、定价准确或翻译质量完全一致。服务是否开通、quota 和未来降级仍由方舟决定。

## 文件、复跑与交付

全部实验位于 scratch/2026-10-05-doubao-fast-translate/。

| 文件 | 用途 |
|---|---|
| experiment.py | 下载冻结输入，执行实际 CLI handler，汇总指标 |
| verify_recordings.py | 不调用 API，核对本地原始记录与保存输出 |
| manifest.json | 输入、环境、版本与固定参数 |
| 01-default.json、02-fast.json、03-fast.json | 前三次请求的完整指标 |
| 04-default.json、05-default.json、06-fast.json | 后三次请求的完整指标 |
| metrics.csv、summary.json | 六次指标表与汇总 |
| response-evidence.json、quality.json | 服务端脱敏证据与结构核对结果 |
| REPORT.md | 本报告 |
| runtime/source.html、runtime/nobel-medicine-2025.md | 本地下载与冻结正文 |
| runtime/<请求编号>/ | 完整请求 JSON、SSE、CLI 日志、译文和 runs.db |

脚本、逐次指标、服务端脱敏证据和报告纳入应用 PR。runtime/ 保留本机完整运行材料；SQLite、网页全文与完整原始流未纳入 Git。请求头和 API key 从未记录；key 只从环境读取。

### 当前本机验证

```bash
cd /Users/mogu/.codex/worktrees/service-tier-fast/editor-assistant
uv sync --locked
EDITOR_ASSISTANT_TEST_DB_DIR="$PWD/scratch/manual-fast" uv run --frozen editor-assistant translate scratch/2026-10-05-doubao-fast-translate/runtime/nobel-medicine-2025.md --model doubao-seed-2.1-lite --thinking low --service-tier fast --save-files
```

当前目录已在 codex/service-tier-fast，邻接 llm-exec-core symlink 指向配套独立 worktree，因此直接 cd 即可，不必在原主 checkout 切换分支。要求当前 shell 已配置 DOUBAO_API_KEY。数据库与输入旁的输出均在 scratch。

### 新的一组实验

在应用 worktree 内新建 scratch/fast-translate-rerun，将两个 Python 脚本复制进去，以保留本次冻结结果，然后执行：

```bash
uv run --frozen python scratch/fast-translate-rerun/experiment.py prepare
uv run --frozen python scratch/fast-translate-rerun/experiment.py run --label 01-default --tier default
uv run --frozen python scratch/fast-translate-rerun/experiment.py run --label 02-fast --tier fast
uv run --frozen python scratch/fast-translate-rerun/experiment.py run --label 03-fast --tier fast
uv run --frozen python scratch/fast-translate-rerun/experiment.py run --label 04-default --tier default
uv run --frozen python scratch/fast-translate-rerun/experiment.py run --label 05-default --tier default
uv run --frozen python scratch/fast-translate-rerun/experiment.py run --label 06-fast --tier fast
uv run --frozen python scratch/fast-translate-rerun/experiment.py analyze
uv run --frozen python scratch/fast-translate-rerun/verify_recordings.py
```

已有同名 run 目录时脚本拒绝覆盖。重新 prepare 可能获得变化后的网页；应以新 manifest 的输入和参数为准。离线核对 analyze、verify_recordings 不发起模型请求；prepare 下载网页，run 会产生真实 API 用量。

应用离线验证：230 passed，3 个真实 integration 测试未运行；另由本次独立脚本完成 6 次真实请求。应用 Black、flake8、mypy 通过；scratch 脚本 Black、flake8 通过。core 在 Python 3.10/3.13 下各 774 passed，locked sync、Black、flake8、mypy、build 通过，PR #52 两个对应 CI 检查已通过。

## 官方语义依据

以下官方文档于 2026-10-05 查询。低延迟文档明确列出本次模型版本；Chat API 将响应 service_tier 定义为实际使用的档位，fast 为低延迟，default 为常规。流式文档示例在 chunk 上携带该字段，因此本次判定使用真实响应字段，不使用命令参数或客户端保存的 requested tier 代替。

- [低延迟在线推理](https://docs.volcengine.com/docs/ark/online-inference-low-latency?lang=zh)
- [Chat API](https://docs.volcengine.com/docs/ark/chat-api?lang=zh&redirect=1)
- [流式输出](https://docs.volcengine.com/docs/ark/streaming-output?lang=zh)
