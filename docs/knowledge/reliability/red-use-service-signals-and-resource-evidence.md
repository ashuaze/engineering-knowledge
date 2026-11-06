---
id: "kb-reliability-red-use"
title: "RED 与 USE：指标齐全，为什么仍找不到故障原因"
kind: "concept"
domain: "reliability"
status: "evolving"
summary: "连接服务请求的速率、错误和时长与资源利用、饱和和错误，明确计数边界、未完成工作及分布聚合。"
created: "2026-10-27"
updated: "2026-10-27"
last_verified: "2026-10-27"
verification: "source-checked"
prerequisites: ["kb-reliability-telemetry", "kb-performance-latency-queues"]
related: ["kb-reliability-slos", "kb-performance-cpu-metrics", "kb-performance-hotspots-contention", "kb-reliability-chaos-experiments"]
tags: ["red", "use", "observability", "measurement"]
---

# RED 与 USE：指标齐全，为什么仍找不到故障原因

学习入口：CPU 曲线平稳，接口却越来越慢；或资源饱和了，用户结果暂时仍正常。服务层与资源层需要用一致的时间、范围和负载连接，指标清单本身不能证明因果。

前置：[日志、指标与链路](logs-metrics-and-traces.md)、[延迟与排队](../performance/latency-throughput-and-queues.md)。本文核查 [RED](../../glossary/reliability.md#reliability.methods)、USE 与 Prometheus 说明；数字均为纸面输入，没有部署埋点、执行查询或采集真实资源。

## 先看服务结果，再检查对应资源

| 方法 | 观察对象 | 三个问题 |
| --- | --- | --- |
| RED | 声明边界上的请求或工作单元 | Rate：每秒多少；Errors：哪些失败及多少；Duration：耗时分布怎样 |
| USE | 每种相关资源 | `Utilization`：用了多少；Saturation：多少需求无法立即服务；Errors：资源发生什么错误 |

[Grafana 对 Tom Wilkie RED 方法的介绍](https://grafana.com/blog/the-red-method-how-to-instrument-your-services/)连接请求数量、错误和时长。[Brendan Gregg 的 USE](https://www.brendangregg.com/usemethod.html)则从资源清单出发检查利用、饱和和错误；可研究的软件资源及配额也需明确含义。

两者互补：用户请求慢可能来自连接等待、CPU 调度、存储或外部依赖；某资源高利用也不必然造成用户故障。应提出可检验假设，再找匹配边界的证据。

## 请求速率要说明计在接纳还是完成

教学窗口长60秒，初始没有在途工作，接纳12600项、完成12000项，其中120项按本例定义失败；没有其他出入路径，取消若发生也计为完成：

```text
接纳速率 = 12600 / 60 = 210项/秒
完成速率 = 12000 / 60 = 200项/秒
完成中的失败速率 = 120 / 60 = 2项/秒
完成中的失败比例 = 120 / 12000 = 1%
窗口末未完成 = 0 + 12600 - 12000 = 600项
```

2项/秒与1%不是同一个量。600项未完成也不是已经确认失败；仅统计已完成结果可能遗漏一直等待的工作，[SLO](../../glossary/reliability.md#reliability.slos)还需按自己的合格事件、期限与归属窗口处理。

如果存在拒绝、取消、[重试](../../glossary/api.md#api.retries)或跨窗口完成，应为计数边界补相应项；已纳入完成数的取消不重复计入。客户端尝试、网关转发和业务操作可能不是一一对应，不能把重试增长直接解释成用户需求增长。

## 错误与时长的含义要跨层核对

HTTP 200 可以表示已接纳，也可能携带业务拒绝；网络超时可能发生在业务提交之后。错误分类应连接产品目标，资源错误计数则反映另一层机制，不一定与请求失败数相等。

耗时从接纳前、[排队](../../glossary/performance.md#performance.queueing)后还是获取连接后开始，决定包括哪些等待。还应区分成功、失败和未完成工作；只看快速失败请求的平均时长，会把严重过载误读为变快。

## 分位数不能直接平均成整体分位数

纸面例子：实例A的99项全部10ms，实例B的1项为1000ms。各自[p95](../../glossary/performance.md#performance.percentiles)为10ms和1000ms，平均为505ms；合并100项后，按nearest-rank取第95项，整体p95为10ms。平均局部分位数丢失了样本数和分布。

[Prometheus 的直方图与摘要说明](https://prometheus.io/docs/practices/histograms/)讨论可聚合分布与预计算分位数的差别。应先在兼容的观测口径下合并分布，再计算所需统计；桶边界、分辨率和数据缺失仍影响精度，本文不提供具体查询或后端配置。

## USE 要按实际资源及限制解释

CPU 忙碌比例、内存占用、[连接池](../../glossary/api.md#api.pool)占用不是同一口径。饱和是存在当前无法服务的额外需求，可能体现为等待、积压或拒绝；“占用未满”也不能排除配额、单核、热分区或下游限制。

从服务异常的时间和受影响范围出发，对照具体实例、版本、资源与依赖。若仪表缺少某段等待，记录缺口；若采集失败，不能把没有数据等同于零错误。实际归因还需链路、日志、剖析或受控验证。

## 自检

1. RED 与 USE 分别观察什么，为什么不能互相替代？
2. 60秒算例的五个结果是多少？失败速率和失败比例有什么区别？
3. 为什么600项未完成不应直接算成功或失败？
4. A/B例子的局部分位数平均和整体p95分别是多少？
5. 资源高利用、没有错误数据与用户故障之间，各需补什么证据？

## 来源与核查

2026-10-27 核查 RED 方法介绍、Gregg USE 原文和 Prometheus 分布说明。本文为 source-checked；未部署监控、执行PromQL、测量资源、验证告警或证明实际因果，所有计数与分位数均为教学推演。
