---
id: "kb-performance-hotspots-contention"
title: "热点与资源竞争：整体不忙为什么局部已经过载"
kind: "concept"
domain: "performance"
status: "evolving"
summary: "区分请求集中、共享资源竞争和串行瓶颈，用热分区与锁持有时间推演局部上限及扩容边界。"
created: "2026-10-26"
updated: "2026-10-26"
last_verified: "2026-10-26"
verification: "source-checked"
prerequisites: ["kb-performance-latency-queues", "kb-systems-synchronization", "kb-systems-cpu-caches"]
related: ["kb-performance-capacity-autoscaling", "kb-performance-profiling", "kb-performance-batching-pipelines", "kb-cache-load-coalescing", "kb-database-partitioning-sharding"]
tags: ["hotspot", "contention", "serialization", "partitioning"]
---

# 热点与资源竞争：整体不忙为什么局部已经过载

学习入口：集群平均 CPU 只有 30%，请求却排很久；加更多[线程](../../glossary/systems.md#systems.execution-units)后更慢。平均值可能遮住一个热键、分区、锁或共享依赖的串行路径。

前置：[排队](latency-throughput-and-queues.md)、[同步原语](../systems/locks-and-synchronization.md)、[CPU 缓存](../systems/cpu-caches-locality-and-false-sharing.md)。本文讨论诊断模型和取舍，数字为纸面假设；没有采集锁统计、硬件事件或运行竞争负载。

## 热点描述集中，竞争描述冲突

[热点](../../glossary/performance.md#performance.contention)可以是某个键承接大量访问，也可以是单个分区、租户或 CPU 核心。资源竞争发生在多个执行者同时需要有限能力时；锁只是其中一种，数据库连接、网络带宽、[队列](../../glossary/algorithms.md#algorithms.queues)额度和[缓存行](../../glossary/systems.md#systems.cpu-cache)都可能成为共享限制。

[USE Method](https://www.brendangregg.com/usemethod.html)按具体资源观察利用、饱和和错误，有助于避免只看总体利用率。应按键、分区、线程、节点和时间窗口拆开证据；高访问量本身也不代表有故障，要看可服务能力和结果。

## 热分区可以先于总容量耗尽

假设四个分区各能稳定完成 300 项/秒，忽略其他限制，总名义能力 1200 项/秒。实际输入为 1000 项/秒，其中 45% 落到同一分区：该分区输入 450 项/秒，超过其 300 上限；其他三个即使有余量，也不会自动替它完成受固定归属约束的工作。

平均负载看起来低于总容量，热分区仍会积压、拒绝或增加[延迟](../../glossary/performance.md#performance.latency-throughput)。若持续该输入、不拒绝且仍完成 300 项/秒，积压净增约 150 项/秒。重分区、拆热键、缓存或改变路由可能有帮助，但应明确顺序、数据归属和[业务不变量](../../glossary/architecture.md#architecture.domain-model)。若同一业务键必须串行修改，单纯增加分区数可能并未拆开这条约束。

## 关键区给出一个串行上限

假设每次请求都必须独占同一把锁 2 ms，处理不能重叠，锁外成本和调度开销暂忽略，则由关键区得到的上限为 `1 / 0.002 = 500 次/秒`。这是理想上界，不是实测吞吐或建议接纳速率。

增加等待线程不缩短关键区，反而可能增加切换、缓存争用和[排队](../../glossary/performance.md#performance.queueing)。将工作移出关键区要重新证明读取、更新与生命周期安全；分锁也要说明哪些规则仍需一起保护，不能用更快掩盖一致性破坏。

[Linux lockstat](https://docs.kernel.org/locking/lockstat.html)区分等待、持有、获取和竞争等统计。一次持锁长与大量短持锁的解释不同；累计等待也可能由多个等待者重叠贡献，不能直接当作墙钟停顿时长。

## 没有互斥锁也可能竞争

原子计数器的同一缓存行被多个核心频繁修改，会付出一致性与竞争成本；逻辑上独立的数据共享缓存行，还可能出现伪共享，见 [Linux False Sharing](https://docs.kernel.org/kernel-hacking/false-sharing.html)。无锁进度保证也不等于在任意竞争负载下更快。

可考虑局部计数、分条、批量汇总或减少共享写入，但这些方法改变了观察精度、合并时机或内存使用。需要精确即时全局值的场景不能未经说明就改成延迟汇总。

## 对不同竞争使用不同措施

| 原因 | 可研究的措施 | 要保留的边界 |
| --- | --- | --- |
| 同一数据重复加载 | 共享加载、缓存与有界等待 | 失效、取消和身份范围 |
| 热租户/热分区 | 按实际负载拆分或隔离 | 顺序、所有权、再均衡成本 |
| 关键区过长 | 减少共享工作、缩短持有 | [原子性](../../glossary/systems.md#systems.atomicity)与对象寿命 |
| 依赖已饱和 | 限制接纳、背压或提高依赖能力 | 更多调用者不创造依赖容量 |

从聚合数据提出假设，再用对应粒度的等待、持有、请求成本与结果证据验证，见[性能剖析](profiling-stacks-and-flame-graphs.md)。一次工具输出不能替代完整因果判断，本文未执行该采集。

## 自检

1. 热点、资源竞争和高总体利用率有什么区别？
2. 四分区算例中，为何总输入 1000 小于 1200 仍会局部过载？
3. 独占 2 ms 得到什么上限？增加线程为什么不保证突破它？
4. 累计锁等待为何不能直接解释为进程停顿的墙钟时长？
5. 分锁、局部计数和拆热键分别可能改变哪些业务或观察保证？

## 来源与核查

2026-10-26 核查 [USE](../../glossary/reliability.md#reliability.methods) Method 作者说明与 Linux lockstat/false-sharing 文档，范围为资源粒度与竞争机制。本文为 source-checked 概念文章；分区和上限算例未运行，未证明某种锁、拆分或缓存方案的实际收益。
