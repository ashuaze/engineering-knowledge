---
id: "kb-performance-overload-lab"
title: "过载控制实验：排队、拒绝与取消的实际边界"
kind: "lab"
domain: "performance"
status: "evolving"
summary: "用固定四个执行槽和开放式到达，对比无界等待、有界拒绝与并发准入，保存逐请求记录及取消探针。"
created: "2026-10-19"
updated: "2026-10-20"
last_verified: "2026-10-19"
verification: "tested"
prerequisites: ["kb-performance-latency-queues", "kb-performance-backpressure"]
related: ["kb-api-admission-controls", "kb-reliability-failure-isolation", "kb-reliability-retry-budgets", "kb-runtime-async-blocking"]
tags: ["overload", "asyncio", "queueing", "cancellation", "lab"]
---

# 过载控制实验：排队、拒绝与取消的实际边界

问题：输入持续增加时，把工作全收下、限制等待数量、满槽立即拒绝，分别会怎样影响积压与完成[延迟](../../glossary/performance.md#performance.latency-throughput)？本实验于 2026-10-19 实际执行，使用 Python 3.13.13 / Windows 11 x64。它测量本地[协程](../../glossary/systems.md#systems.execution-units)调度和接纳策略；服务工作是合成等待，不代表 CPU、HTTP、数据库或生产容量。

## 固定什么，改变什么

每项工作持有一个执行槽，执行 `await asyncio.sleep(0.04)`，再返回 `id × 3 + 7`。四个槽始终相同；40ms 是配置的资源占用等待，实际调度后的持续时间另行记录。算术上的理想速率为 100 项/秒，不能把它当作实测吞吐。

| 策略 | 接纳动作 | 业务等待上限 |
| --- | --- | --- |
| unbounded，无界等待 | 全部放入 asyncio.[Queue](../../glossary/algorithms.md#algorithms.queues)，由四个工作者取出 | 未设上限 |
| bounded，有界等待 | put_nowait；队列满则明确拒绝 | 队列最多 12 项，另有至多 4 项执行中 |
| [concurrency](../../glossary/systems.md#systems.concurrency)，并发准入 | 先同步预留槽位，再创建任务；满槽即拒绝 | 没有业务等待队列，至多 4 项已预留工作 |

并发准入仍有[事件循环](../../glossary/runtime.md#runtime.event-loop)[调度等待](../../glossary/performance.md#performance.cpu-metrics)；没有业务队列不表示零延迟。队列峰值在入队后采样，包括可能很快被工作者取走的元素，不等于整个进程的请求内存上限。

目标到达率为 40、120、240 次/秒，每次运行计划输入 1.2 秒，分别提交 48、144、288 次尝试。每种组合重复三次并轮换策略顺序，共 27 组、4,320 次尝试。发生器按单调时钟的绝对时刻提交，不等待任务完成或队列空位；迟到时可能形成追赶突发，原始记录保留计划与实际提交时间。这是开放式到达，目标速率并不等于精确实现的速率。

## 怎样运行与查原始证据

在仓库根目录运行，无需第三方 Python 依赖：

```bash
python examples/overload_control/lab.py
python -m unittest discover -s examples/overload_control -p 'test_*.py' -v
```

第一条会覆盖本地结果 JSON；如需保留本轮基线，先复制记录。重新运行、保存测试输出后，才使用 `python examples/overload_control/lab.py --freeze-manifest` 更新摘要；摘要匹配只证明文件一致，不证明观察可以外推。

- [实验实现](../../../examples/overload_control/lab.py)与[契约测试](../../../examples/overload_control/test_lab.py)。
- [完整结果 JSON](../../../examples/overload_control/results/results.json)：环境、27 组参数、每次尝试的时间及结果、所有汇总口径、6 次取消探针。
- [四项测试原始输出](../../../examples/overload_control/results/tests.txt)与[字节数及 SHA256 清单](../../../examples/overload_control/results/manifest.json)。

本机 Windows 沙盒内 asyncio 事件循环启动受阻，最终完整实验及测试在获准的沙盒外执行；程序不建立 HTTP 服务，也不访问远程依赖。单次运行结束后等待所有已接纳任务完成，关闭工作者，再开始下一组。

## 测量口径

逐请求记录使用同一运行起点的秒数：scheduled_at 是计划输入，offered_at 是实际提交，started_at 是拿到工作后的执行开始，finished_at 是计算结果完成。拒绝另记 rejected_at，不产生成功结果。

- 完成延迟：`finished_at - offered_at`，只统计最终完成的已接纳工作，包括输入阶段结束后才完成者。
- 队列/调度等待：`started_at - offered_at`；工作占用：`finished_at - started_at`。并发模式的前者只有调度等待。
- 计划到完成：`finished_at - scheduled_at`，另外呈现发生器迟到，避免把这部分成本藏在提交时间之前。
- 输入阶段持续到所有计划尝试发出，且时钟达到 1.2 秒；若提交迟到则延长。实际尝试速率为尝试数除以实际阶段时长，阶段内完成吞吐只计该时点前完成的工作。
- 阶段末积压是已接纳但未完成数；排空时间从阶段末到这些工作全部完成，排空不再产生新输入。它不是持续输入时的稳定延迟。

[分位数](../../glossary/performance.md#performance.percentiles)使用 nearest-rank：排序后取第 `ceil(p × n)` 项；空总体记 null。每组只有几十到几百项，P99 接近样本最慢端，三次重复不能证明稳定分布。拒绝时间独立统计，不混入成功延迟，也不平均多个运行的 P99。

## 本机观察

表中范围是三次运行的最小值到最大值；完成和拒绝列也是单次运行计数范围，不能把上下界跨组拼成一组结果。延迟列是各次 P99 的范围，单位 ms。

| 目标次数/秒 | 策略 | 完成 / 拒绝 | 完成 P99 ms | 队列峰值 | 排空 ms |
| --- | --- | --- | --- | --- | --- |
| 40 | 无界等待 | 48 / 0 | 55.2–57.8 | 1 | 31.2–33.5 |
| 40 | 有界等待 | 48 / 0 | 55.8–103.6 | 1 | 17.4–30.7 |
| 40 | 并发准入 | 48 / 0 | 53.7–81.9 | 0 | 14.2–34.9 |
| 120 | 无界等待 | 144 / 0 | 564.8–633.7 | 43–47 | 533.2–629.8 |
| 120 | 有界等待 | 109–111 / 33–35 | 200.6–205.1 | 12 | 175.6–197.8 |
| 120 | 并发准入 | 89–94 / 50–55 | 55.9–73.6 | 0 | 39.3–46.4 |
| 240 | 无界等待 | 288 / 0 | 2383.9–2431.4 | 191 | 2369.7–2412.7 |
| 240 | 有界等待 | 106–112 / 176–182 | 203.5–241.7 | 12 | 166.0–185.0 |
| 240 | 并发准入 | 96–99 / 189–192 | 58.6–71.5 | 0 | 32.1–50.8 |

40 档所有尝试均完成，但仍存在本地调度波动。240 档无界队列每次接纳 288 项，输入结束时均有 195 项尚未完成，队列峰值 191；这三组的输入阶段完成吞吐约为 76.5–76.7 项/秒，并非 240 项/秒。后续仍能排空，是因为输入已经停止。

有界策略在 240 档每次只完成 106–112 项，拒绝 176–182 项；并发准入完成 96–99 项，拒绝 189–192 项。较短的已接纳延迟伴随大量拒绝，需要同时报告业务损失。12 项队列最多加上四个执行槽，限制的是这条本地路径的等待与执行数量，不是所有请求的完整内存。

240 档实际尝试速率约 236.6–239.7 次/秒；全体运行的发生器最大迟到最高约 80.9ms。调度和定时波动会影响突发、占用和接纳数量，不能据此推荐生产阈值。原始 JSON 同时保留占用时间、发生器迟到分位数、拒绝时间与阶段末状态，可检查上述解释。

## 超时不等于工作停止

另做两类探针，各三次。工作先占槽并等待一个未释放的 Event；调用方等待 20ms 后[超时](../../glossary/api.md#api.retries)，随后记录任务状态，再显式清理。20ms 只是本地对照参数，不是建议的网络超时。

| 方式 | 超时时的观察 | 清理后 |
| --- | --- | --- |
| wait_for(shield([task](../../glossary/runtime.md#runtime.microtasks))) | 调用方超时，任务未结束，仍持有槽位 | 释放 Event 后工作完成并归还槽位 |
| wait_for(task) | 协作取消到达 Event 等待处，finally 已归还槽位，任务被标为取消 | 没有产生完成结果 |

六次探针均符合上述状态断言。它们只验证 Python 的协作取消：没有不可中断计算、真实网络、数据库提交或外部 SDK。wait_for 会等待取消处理，实际返回时间也不保证严格等于配置上限。远端是否已提交仍需业务查询或[幂等](../../glossary/api.md#api.idempotency)协议。

## 检查通过意味着什么

每组保存八个检查结果，共 216 个：尝试结果完整归类、标识唯一、接纳结果正确、时间顺序成立、活动数不超过四、有界队列不超限、并发模式没有业务队列、结束后本组任务和资源已释放。其中 36 个属于策略不适用而直接通过的条件项，不能当作 216 种独立场景。最终任务结束和资源释放来自[运行时](../../glossary/runtime.md#runtime.virtual-machine)断言，记录只保存通过状态，不能单凭逐请求时间重新证明。检查不以“哪种策略快多少”作为通过条件。

四项[契约测试](../../glossary/engineering.md#engineering.contracts)分别检查三种策略的结果及资源上限、await put 在满队列时等待消费者腾位、调用方超时后工作继续、协作取消后释放槽位。第二项使用 Event 和取出元素来协调顺序，不用固定睡眠猜测生产者是否在等待。测试输出中的一次慢任务调度提示保留在证据里，测试结果为通过。

本实验的有界拒绝没有实现上游自动减速；单独的 await put 测试只验证局部反馈契约。没有运行令牌桶、分布式配额、[熔断](../../glossary/reliability.md#reliability.isolation)统计或半开探测、业务降级，也没有测真实 HTTP/数据库池、内存峰值、CPU 容量或生产 [SLO](../../glossary/reliability.md#reliability.slos)。相关概念保持 source-checked。

## 关联阅读与来源

- [背压与有界队列](backpressure-and-bounded-queues.md)：定位等待与压力反馈。
- [限流、并发与配额](../api/rate-limits-concurrency-and-quotas.md)：区分速率和同时占用。
- [熔断、隔离与降级](../reliability/circuit-breakers-isolation-and-degradation.md)：本实验尚未覆盖的故障与恢复机制。
- [超时与重试预算](../reliability/timeouts-and-retry-budgets.md)：把等待、清理与额外尝试放进总预算。
- [Python 3.13 Queue](https://docs.python.org/3.13/library/asyncio-queue.html)与[Task](https://docs.python.org/3.13/library/asyncio-task.html)：API 语义核查日期 2026-10-19，实测数值以随附记录为准。
