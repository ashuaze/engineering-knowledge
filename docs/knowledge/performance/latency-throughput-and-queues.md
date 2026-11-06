---
id: "kb-performance-latency-queues"
title: "延迟、吞吐与排队：为什么请求更多却没有更快"
kind: "concept"
domain: "performance"
status: "evolving"
summary: "区分到达率、吞吐、并发与尾延迟，用 Little 定律和有界排队理解容量及背压。"
created: "2026-10-16"
updated: "2026-10-26"
last_verified: "2026-10-16"
verification: "source-checked"
prerequisites: []
related: ["kb-performance-slow-api", "kb-runtime-async-blocking", "kb-reliability-retry-budgets", "kb-reliability-slos", "kb-performance-backpressure", "kb-api-admission-controls", "kb-performance-overload-lab", "kb-performance-cpu-metrics", "kb-performance-benchmarking", "kb-performance-batching-pipelines", "kb-performance-hotspots-contention", "kb-performance-capacity-autoscaling"]
tags: ["latency", "throughput", "queueing", "backpressure"]
---

# 延迟、吞吐与排队：为什么请求更多却没有更快

学习入口：提高[并发](../../glossary/systems.md#systems.concurrency)后，成功请求数几乎不变，[P99](../../glossary/performance.md#performance.percentiles) 却翻倍，资源去了哪里？前置知识：请求响应、资源池与基本平均数。本文建立容量分析的概念，数字均为纸面计算，没有运行压测或据此给出容量建议。

继续区分[批处理与流水线](batching-pipelining-and-amortized-waiting.md)的等待、[热点与资源竞争](hotspots-contention-and-serialized-service.md)的局部串行点，以及[容量规划与自动扩缩容](capacity-planning-scaling-and-autoscaling-feedback.md)的成本和反馈。

## 先把统计边界说清

| 概念 | 含义 | 必须同时说明 |
| --- | --- | --- |
| [延迟](../../glossary/performance.md#performance.latency-throughput) Latency | 一次操作从起点到终点的时间 | 客户端、服务端还是某段依赖；是否包含[排队](../../glossary/performance.md#performance.queueing) |
| 到达率 | 单位时间进入指定边界的工作数 | 外部尝试、实际接纳与内部[重试](../../glossary/api.md#api.retries)是否分开 |
| 吞吐 Throughput | 单位时间完成的工作数 | 完成含成功、失败还是只计有效业务结果 |
| 并发数 | 某时刻边界内尚未离开的工作数 | 包含等待和执行，还是仅统计执行者 |
| P99 | 按给定统计方法估计的第 99 百分位延迟 | 时间窗、样本范围、失败与超时如何计入 |

[RPS](../../glossary/performance.md#performance.rates)/QPS 只是速率单位：发起 1,000 次尝试每秒，并不表示完成 1,000 个有效订单每秒。[批处理](../../glossary/performance.md#performance.batching)、重试和请求成本差异也会改变二者关系。[Google 的过载处理说明](https://sre.google/sre-book/handling-overload/)特别讨论了仅按 QPS 估算资源需求的局限。

## 等待怎样进入响应时间

把某段服务简化为“等待资源 → 持有资源处理 → 离开”。当到达的工作持续超过可完成的工作，又没有拒绝或过期处理时，积压就会增长。异步等待可以让[线程](../../glossary/systems.md#systems.execution-units)去做别的事，却不会消除排队中的请求、内存和[截止时间](../../glossary/reliability.md#reliability.retry-budget)。

即使平均到达率低于容量，突发流量、处理时间差异和共享[资源竞争](../../glossary/performance.md#performance.contention)仍会产生等待。接近容量时，系统缺少吸收波动的余量；具体延迟曲线需要负载模型或测量，不能只凭“利用率达到某百分比”统一判断所有系统。

教学例子：一个工作者每个任务固定处理 10ms，10 个任务同时到达，[FIFO](../../glossary/algorithms.md#algorithms.queues) 且没有其他成本。第一项在 10ms 完成，最后一项要等到 100ms，平均完成延迟为 55ms。任务自身没有变慢，响应已经变慢。若每秒持续到达 120 项，而每秒只能处理 100 项，未限制的积压会持续增长。

## Little 定律关联三个平均量

对长期稳定、统计口径一致且相关平均量存在的系统：

```text
L = λ × W
L：边界内平均工作数
λ：进入该边界的有效平均到达率；稳定时与离开率相平衡
W：每项工作在同一边界内的平均停留时间
```

公式参见 [MIT 排队论教材](https://web.mit.edu/urban_or_book/www/book/chapter4/4.4.html)。它可以用于整个处理系统，也可以只用于等待队列，但三个量必须一起改变口径。

纸面例子：某服务稳定完成 200 项/秒，平均从接纳到离开为 0.15 秒，平均在途工作数约为 30。若固定吞吐而平均停留时间升至 0.5 秒，对应平均在途数为 100。这些数包含边界内等待者，不能直接当作所需线程数。

Little 定律关联平均量，不解释因果，也不计算 P99。不能把 P99 代入平均时间的位置，不能用客户端所有尝试的到达率配服务端接纳后的延迟，更不能把正在无限积压的短窗口当作稳定容量证明。

## 尾延迟与平均值各回答什么

平均延迟概括总时间成本，P95/P99 揭示较慢一端的体验。请求类型、租户、缓存未命中和热点资源不同，可能让总体平均掩盖局部问题。[Google 的监控章节](https://sre.google/sre-book/monitoring-distributed-systems/)讨论了延迟分布与尾部观测的必要性。

聚合多个实例时，应合并可聚合的分布数据或原始样本后计算；直接平均实例 P99，通常得不到总体 P99。[Prometheus 的直方图与摘要说明](https://prometheus.io/docs/practices/histograms/)展示了可聚合分布与预计算分位数的区别。样本少时尾部估计也不稳定。只统计成功返回，还会遗漏超时和拒绝；它们应作为独立结果或按预先定义的[服务指标](../../glossary/reliability.md#reliability.slos)纳入，避免快速失败让图表看起来“更快”。

## 用有界队列与背压明确容量责任

| 机制 | 控制什么 | 仍需承担的成本 |
| --- | --- | --- |
| 并发限制 | 同时占用稀缺资源的工作数 | 限制外仍可能排队，必须说明等待上限 |
| 有界队列 | 暂存工作数或字节数 | 队列满、任务过期和公平性需要策略 |
| 背压 Backpressure | 把处理能力约束反馈给上游 | 上游必须减速、等待或停止接纳，不能只搬移队列 |
| [限流](../../glossary/api.md#api.limits) / [负载丢弃](../../glossary/performance.md#performance.overload) | 控制接纳速率或拒绝过载工作 | 拒绝也有成本，并可能引发重试 |

例如消费者通过有界拉取控制未处理消息数，API 通过接纳限制保护[连接池](../../glossary/api.md#api.pool)。限制值需结合资源成本、用户目标和负载测量决定；扩大连接池或队列可能只是让更多工作同时竞争。

应传播截止时间，在开始昂贵工作前检查剩余预算，并定义取消与资源释放。调用方停止等待，不保证后台工作停止；过载响应若触发无预算重试，队列会继续受压。

## 用什么证据检验假设

资源统计配套读[CPU 利用率与配额](cpu-time-utilization-load-and-quotas.md)，比较优化则读[基准测试与加速比](benchmarks-workloads-and-speedup.md)。先对齐范围、分母、实际负载与工作契约，再解释收益；新文的时长和[加速比](../../glossary/performance.md#performance.benchmark)是模型计算，没有新增本文负载结果。

按相同请求组合逐步增加发起速率，同时记录实际接纳、完成、成功、拒绝和超时率，观察延迟分布、队列长度、资源利用与池等待。固定并发且等上次完成才发新请求的压测，会随服务变慢自动减少发起量；需要记录实际负载，不能仅凭并发数声称承受了某个到达率。

自检：对“每秒完成 500 项、平均停留 0.2 秒”的稳定系统，先算出平均在途 100 项，再解释为什么不能推出需要 100 个 CPU 核或 P99 为 0.2 秒。本文的纸面算例没有作为压测执行；新增[过载控制实验](overload-control-lab.md)另外执行了合成等待工作负载的接纳对照，不提供生产容量结论。

## 关联阅读与来源

- [背压与有界队列](backpressure-and-bounded-queues.md)：区分限制等待与真正向上游反馈。
- [限流、并发与配额](../api/rate-limits-concurrency-and-quotas.md)：区分时间窗、在途数量和累计用量。

- [慢 API 排查](slow-api-investigation.md)：用证据定位连接池等待与实际执行时间。
- [同步、异步与阻塞](../runtime/async-and-blocking.md)：执行位置与异步契约不等于容量。
- [重试预算](../reliability/timeouts-and-retry-budgets.md)：控制额外尝试与等待成本。
- [SLI、SLO 与错误预算](../reliability/slis-slos-and-error-budgets.md)：把性能观测转换为用户结果目标。

核查日期：2026-10-16。Little 定律依据 MIT 教材，过载与延迟分布依据 Google SRE 的工程说明。算例、指标组合及验证计划为教学综合，没有系统容量或性能实测。

- [MIT：Some Important Relationships in Queueing Theory](https://web.mit.edu/urban_or_book/www/book/chapter4/4.4.html)
- [Google SRE：Handling Overload](https://sre.google/sre-book/handling-overload/)
- [Google SRE：Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/)
- [Prometheus：Histograms and summaries](https://prometheus.io/docs/practices/histograms/)
