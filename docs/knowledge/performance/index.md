<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# 性能与容量

建议优先级：P0。目标：建立负载、等待、资源和[尾延迟](../../glossary/performance.md#performance.percentiles)的证据链。

下方术语用于知识索引。建议从[实际工程问题](../../problems.md)或本页核心问题进入，结合已有正文理解机制、适用边界与相关概念。

## 一个核心问题

吞吐不再增长时，继续增加[并发](../../glossary/systems.md#systems.concurrency)为什么可能更慢？

## 已有正文

- [背压与有界队列：把等待放在哪里](backpressure-and-bounded-queues.md)：区分缓存突发、拒绝过载与向上游反馈容量，追踪限制之外的等待、内存和[截止时间](../../glossary/reliability.md#reliability.retry-budget)。
- [批处理与流水线：减少往返为什么可能增加单项等待](batching-pipelining-and-amortized-waiting.md)：区分合并、重叠、并行与事务，推演往返节省和凑批等待，说明依赖、失败恢复及有界窗口。
- [基准测试与加速比：局部快四倍，整体为什么只快一点](benchmarks-workloads-and-speedup.md)：解释比较口径、工作负载、冷暖状态和测量偏差，用 [Amdahl](../../glossary/performance.md#performance.benchmark) 模型说明局部优化与整体收益的边界。
- [容量规划与自动扩缩容：副本增加为什么不等于能力立即增加](capacity-planning-scaling-and-autoscaling-feedback.md)：从请求成本和故障余量估算容量，区分水平/[垂直扩容](../../glossary/performance.md#performance.scaling)、[HPA](../../glossary/devops.md#devops.autoscaling) 指标分母、原始建议及就绪能力。
- [CPU 利用率、负载与配额：主机还有空闲，请求为什么仍在等](cpu-time-utilization-load-and-quotas.md)：区分经过时间、[CPU 时间](../../glossary/performance.md#performance.cpu-metrics)、利用率、运行[队列](../../glossary/algorithms.md#algorithms.queues)和 Linux 负载，解释核数口径、cgroup 带宽与资源压力。
- [热点与资源竞争：整体不忙为什么局部已经过载](hotspots-contention-and-serialized-service.md)：区分请求集中、共享[资源竞争](../../glossary/performance.md#performance.contention)和串行瓶颈，用热分区与锁持有时间推演局部上限及扩容边界。
- [延迟、吞吐与排队：为什么请求更多却没有更快](latency-throughput-and-queues.md)：区分到达率、吞吐、并发与尾延迟，用 Little 定律和有界[排队](../../glossary/performance.md#performance.queueing)理解容量及背压。
- [过载控制实验：排队、拒绝与取消的实际边界](overload-control-lab.md)：用固定四个执行槽和开放式到达，对比无界等待、有界拒绝与并发准入，保存逐请求记录及取消探针。
- [Profiling 与火焰图：最宽的函数，为什么未必是延迟根因](profiling-stacks-and-flame-graphs.md)：解释采样、插桩与[调用栈](../../glossary/systems.md#systems.memory-layout)聚合，区分包容/自身成本、执行与等待、[火焰图](../../glossary/performance.md#performance.profiling)与时间线及证据局限。
- [慢 API 排查：把执行时间与排队时间分开](slow-api-investigation.md)：用教学推演示范从现象提出假设、收集证据和设计验证。

## 术语范围

| 术语 | 简释 |
| --- | --- |
| [Latency / Throughput](../../glossary/performance.md#performance.latency-throughput) | 完成一次操作的时间与单位时间处理量。 |
| [QPS / RPS / TPS](../../glossary/performance.md#performance.rates) | 查询、请求和事务速率，须写清计数口径。 |
| [P50 / P95 / P99](../../glossary/performance.md#performance.percentiles) | 观测窗口内延迟分布的分位数。 |
| [CPU-bound / I/O-bound](../../glossary/performance.md#performance.bound) | 描述当前主要受计算或 I/O 等资源约束的工作，需结合运行与等待证据，不能靠固定利用率阈值分类。 |
| [Little’s Law](../../glossary/performance.md#performance.little) | 稳定系统中平均在途量、到达率和停留时间的关系。 |
| [Profiling / Flame Graph](../../glossary/performance.md#performance.profiling) | 把所选事件和资源权重归到代码或调用栈，区分聚合宽度、执行时间线、累计/自身及运行/等待范围。 |
| [Load / Stress / Soak Test](../../glossary/performance.md#performance.load-tests) | 分别观察目标负载、超限失效和持续退化；需说明请求发起方式、正确性、尾延迟及资源边界。 |
| [Horizontal / Vertical Scaling](../../glossary/performance.md#performance.scaling) | 增加实例与提升单实例资源。 |
| [Batching / Pipelining](../../glossary/performance.md#performance.batching) | 合并操作和重叠多个执行阶段。 |
| [Rate Limiting / Load Shedding](../../glossary/performance.md#performance.overload) | 约束进入速率和过载时拒绝工作。 |
| [Hotspot / Contention](../../glossary/performance.md#performance.contention) | 局部集中访问与共享资源竞争。 |
| [Queueing / Backpressure](../../glossary/performance.md#performance.queueing) | 等待队列形成和压力反馈。 |
| [Capacity Planning](../../glossary/performance.md#performance.capacity) | 用工作负载、资源余量和增长预估容量。 |
| [CPU Time / Utilization / Load Average](../../glossary/performance.md#performance.cpu-metrics) | 按范围、时间窗口和分母解释执行、利用率、平滑负载、组带宽与资源停顿，不能直接换算成慢请求比例。 |
| [Benchmark / Speedup / Amdahl’s Law](../../glossary/performance.md#performance.benchmark) | 固定工作契约、测量边界和负载比较成本，用明确假设下的局部时间占比解释整体收益与上限。 |

## 练习与验收

选择上面的一个核心问题，先画执行过程或数据边界，再构造一个正常路径和一个失败路径。用原理解释、架构或代码、诊断证据和取舍依据说明保证范围；记录已完成验证与待验证项。

[回到知识地图](../../map.md) · [问题导航](../../problems.md) · [学习路径](../../paths/index.md)
