---
id: "kb-performance-slow-api"
title: "慢 API 排查：把执行时间与排队时间分开"
kind: "case"
domain: "performance"
status: "evolving"
summary: "用教学推演示范从现象提出假设、收集证据和设计验证。"
created: "2026-10-16"
updated: "2026-10-20"
last_verified: null
verification: "design-proposal"
prerequisites: []
related: ["kb-runtime-async-blocking", "kb-api-idempotency", "kb-reliability-retry-budgets", "kb-frontend-long-tasks", "kb-performance-latency-queues", "kb-reliability-slos", "kb-database-indexes-plans", "kb-reliability-telemetry", "kb-networking-http-pools", "kb-networking-connections-lab", "kb-performance-cpu-metrics", "kb-performance-profiling", "kb-performance-benchmarking"]
tags: ["performance", "observability"]
---

# 慢 API 排查：把执行时间与排队时间分开

## 案例来源与限制

这是**教学推演**，不是作者真实生产事故；不提供虚构的实测[延迟](../../glossary/performance.md#performance.latency-throughput)、[QPS](../../glossary/performance.md#performance.rates) 或优化收益。目标是展示一种可用于真实案例的证据组织方式。

假定现象：某个 API 在业务高峰变慢，[CPU 利用率](../../glossary/performance.md#performance.cpu-metrics)看起来不高，数据库单条查询也不明显变慢。以上是问题设定，尚未证明瓶颈位置。

## 先定义时间边界

把用户等待拆成入口[排队](../../glossary/performance.md#performance.queueing)、应用调度、连接获取、数据库执行、外部调用和响应传输。各阶段可能存在重叠，不能把所有 [span](../../glossary/reliability.md#reliability.trace) 的耗时直接求和；先确认链路是否顺序执行以及追踪是否完整。

## 假设与反证

系统性能概念可配套读[CPU 利用率与配额](cpu-time-utilization-load-and-quotas.md)、[Profiling 与火焰图](profiling-stacks-and-flame-graphs.md)、[基准测试与加速比](benchmarks-workloads-and-speedup.md)。分别解释资源约束、执行/等待归因和公平对照；新文的来源核查不构成本案例实际采集或优化效果的证据。

| 假设 | 应寻找的证据 | 什么会削弱该假设 |
| --- | --- | --- |
| [连接池](../../glossary/api.md#api.pool)等待 | 连接获取耗时、活跃连接、等待[队列](../../glossary/algorithms.md#algorithms.queues) | 获取连接耗时稳定且很短 |
| [事件循环](../../glossary/runtime.md#runtime.event-loop)被占用 | 事件循环延迟、CPU profile、同步调用 | 延迟与慢请求无时间关联 |
| 数据库锁等待 | [阻塞](../../glossary/systems.md#systems.blocking)链、事务年龄、等待事件 | 慢窗口中没有对应等待 |
| 下游变慢或[重试](../../glossary/api.md#api.retries)放大 | 依赖 span、重试次数、超时分布 | 下游耗时和请求放大均无变化 |
| 应用前已经排队 | 网关接收和应用接收时间差 | 请求进入应用前无等待 |

此处的观测项目是排查建议，不是对当前假设的证明。

## 若证据指向连接池

进一步检查连接持有时间，长事务、游标未关闭、事务内外部 HTTP 调用都可能延长占用。连接池满也可能只是下游变慢的症状。直接把池从小值放大，可能将更多工作压到数据库并加重等待。

候选措施包括缩短事务范围、为等待设定超时、限制应用[并发](../../glossary/systems.md#systems.concurrency)、修复资源泄漏。是否增加连接数，需要数据库剩余容量和压测证据支持。

HTTP 方向可另读[连接池与阶段超时](../networking/http-reuse-pools-and-timeouts.md)及[回环连接实验](../networking/connection-lifecycle-lab.md)，观察请求尚未取得 [socket](../../glossary/systems.md#systems.fd-socket) 的等待。该局部对照没有验证本文假设的生产瓶颈或数据库池，也不将此教学案例改为实测事故。

## 验证方案

固定工作负载、数据规模和依赖条件，对照修改前后：端到端延迟分布、连接等待、连接占用、吞吐、错误率和数据库资源。既检查正常高峰，也检查下游退化时是否出现更长队列。

这里只提出验证方法，没有报告“优化成功”。完成实际实验后，保留原始结果及环境，再将本文扩展成实测案例。

## 自检与关联

- [索引与执行计划](../database/indexes-and-query-plans.md)：先确认等待发生在数据库内部，再检查[行数估计](../../glossary/database.md#database.selectivity)与访问路径。
- [日志、指标与链路](../reliability/logs-metrics-and-traces.md)：明确连接等待的采集边界，避免把采样链路当作完整分母。
- [延迟、吞吐与排队](latency-throughput-and-queues.md)：为等待、容量与[尾延迟](../../glossary/performance.md#performance.percentiles)建立共同口径。
- [SLI、SLO 与错误预算](../reliability/slis-slos-and-error-budgets.md)：先确认用户结果与评估窗口，再判断影响。

当看到“SQL 很快，但 API 很慢”，能否指出至少三个 SQL 执行之外的等待位置？如果证据推翻第一个假设，下一步收集什么？

- [异步与阻塞](../runtime/async-and-blocking.md)
- [API 幂等性](../api/idempotency.md)：超时或结果未知后重试，避免重复产生业务副作用。
- [超时与重试预算](../reliability/timeouts-and-retry-budgets.md)：检查排队、单次超时和多层重试如何消耗总时间。
- [浏览器长任务](../frontend/long-tasks-and-responsiveness.md)：接口响应后，还需检查客户端的输入处理与绘制等待。

本文为维护者的教学诊断方案；具体数据库等待指标、驱动行为和 [Runtime](../../glossary/runtime.md#runtime.virtual-machine) 指标需在实际系统中按版本核实。
