---
id: "kb-performance-batching-pipelines"
title: "批处理与流水线：减少往返为什么可能增加单项等待"
kind: "concept"
domain: "performance"
status: "evolving"
summary: "区分合并、重叠、并行与事务，推演往返节省和凑批等待，说明依赖、失败恢复及有界窗口。"
created: "2026-10-26"
updated: "2026-10-26"
last_verified: "2026-10-26"
verification: "source-checked"
prerequisites: ["kb-performance-latency-queues", "kb-performance-backpressure"]
related: ["kb-performance-capacity-autoscaling", "kb-performance-hotspots-contention", "kb-cache-redis-data-types", "kb-performance-benchmarking"]
tags: ["batching", "pipelining", "latency", "bounded-window"]
---

# 批处理与流水线：减少往返为什么可能增加单项等待

学习入口：把多次请求一起发送后总吞吐提高，为什么第一条记录反而更晚完成？需要分清固定开销摊销、请求重叠、[并行](../../glossary/systems.md#systems.concurrency)执行和等凑批的时间。

前置：[延迟、吞吐与排队](latency-throughput-and-queues.md)、[背压](backpressure-and-bounded-queues.md)。本文参照 Redis [pipelining](../../glossary/performance.md#performance.batching)、PostgreSQL 18 libpq pipeline 和过载控制原则，数字是理想化纸面输入。没有执行命令、运行客户端或测量吞吐。

## 四种机制有不同承诺

| 机制 | 改变什么 | 不自动获得什么 |
| --- | --- | --- |
| 批处理 Batching | 多项作为一批交给某个边界，摊销请求等固定开销 | 整批原子成功、单项无等待 |
| 流水线 Pipelining | 无需等上一项结果就继续发送，重叠等待 | 服务端并行执行、没有前后依赖 |
| 并行执行 | 多个执行资源同时工作 | 没有共享瓶颈或顺序约束 |
| 事务 | 按协议约束一组状态变化的提交 | 自动减少网络往返或执行成本 |

[Redis pipelining](https://redis.io/docs/latest/develop/using-commands/pipelining/)解释不逐条等待回复的收益，也提醒待发送和回复缓冲的内存成本。不能把 pipeline 当成事务接口，批内也未必没有其他参与者的影响。

## 用同一组条件比较往返

假设四项彼此独立、现在都已可发送；每次网络往返 4 ms，每项服务端处理 0.5 ms，忽略传输长度、编码、调度和[排队](../../glossary/performance.md#performance.queueing)，服务端仍串行处理。比较全部四项完成所需时间：

```text
逐项等待：4 × (4 + 0.5) = 18 ms
一次批量：4 + 4 × 0.5 = 6 ms
可重叠往返的理想流水线：最后一项也可接近 6 ms
```

后两项相同只是该简化模型的结果，不是两种协议在现实中等价。固定开销、flush、网络拥塞、响应大小和窗口边界都会改变结果；第一项何时可见，还要看协议是否允许逐项返回。

## 凑批延迟可能抵消固定成本收益

另设四项分别在 0、5、10、15 ms 到达，等满四项时于 15 ms 才发出。四项仅凑批等待分别为 15、10、5、0 ms，平均为 7.5 ms，尚未计算网络和处理。

因此低流量下大批量可能长期不满；通常需要同时限定批内项数、字节数和最大等待时间。到时间发出不满批，可能牺牲部分吞吐换取等待边界。只限制条数无法约束含大对象的内存，也不能阻止生产者积压无限多批。

## 依赖与错误要在协议边界说明

若第二个请求的参数需要第一个请求的返回值，客户端不能在尚不知道它时正确预发。可把相关逻辑移到受约束的服务端能力，或在依赖处等待；不能仅靠打开 pipeline 消除数据依赖。

[PostgreSQL 18 pipeline mode](https://www.postgresql.org/docs/18/libpq-pipeline-mode.html)要求维护请求与结果对应，并处理同步点和错误后的跳过等状态。具体事务关系由协议和同步边界决定，不可把其他客户端的批量 API 直接套用。

部分结果已成功、连接随后断开时，应确定哪些项已提交、哪些不确定、如何沿用操作身份安全恢复。简单重发整批可能重复副作用；重新发送也不必保留原批的分组方式，关键是业务操作身份与顺序。

## 有界窗口与公平性一起考虑

大量预发会同时占用客户端缓冲、服务端[队列](../../glossary/algorithms.md#algorithms.queues)和返回缓冲。为每条连接及整体工作设置在途项/字节上限，消费结果后再推进；还需给取消和慢消费者留出收敛路径。过载下接纳与拒绝的职责见 [Google SRE Handling Overload](https://sre.google/sre-book/handling-overload/)。

一个大批还可能长时间占住共享资源，使短请求等待。比较时记录批尺寸、填充率、最长等待、峰值内存、单项[延迟](../../glossary/performance.md#performance.latency-throughput)与有用吞吐，不只看每秒提交的批数。

## 自检

1. 批处理、流水线、并行和事务分别改变什么？
2. 18 ms 与 6 ms 算例成立需要哪些假设？
3. 0/5/10/15 ms 到达的凑批等待分别是多少？平均是多少？
4. 第二项需要第一项返回值时，为什么不能直接预发？
5. 断线后重发整批与无限扩大窗口各有哪些风险？

## 来源与核查

2026-10-26 核查 Redis 官方 pipeline、PostgreSQL 18 libpq pipeline 和 Google SRE 过载章节。本文为 source-checked 概念文章；未执行数据库/缓存命令、验证批内提交语义、错误恢复或性能收益。
