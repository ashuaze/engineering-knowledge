<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# 性能与容量

建议优先级：P0。目标：建立负载、等待、资源和尾延迟的证据链。

下方术语用于知识索引。建议从[实际工程问题](../../problems.md)或本页核心问题进入，结合已有正文理解机制、适用边界与相关概念。

## 一个核心问题

吞吐不再增长时，继续增加并发为什么可能更慢？

## 已有正文

- [慢 API 排查：把执行时间与排队时间分开](slow-api-investigation.md)：用教学推演示范从现象提出假设、收集证据和设计验证。

## 术语范围

| 术语 | 简释 |
| --- | --- |
| Latency / Throughput | 完成一次操作的时间与单位时间处理量。 |
| QPS / RPS / TPS | 查询、请求和事务速率，须写清计数口径。 |
| P50 / P95 / P99 | 观测窗口内延迟分布的分位数。 |
| CPU-bound / I/O-bound | 瓶颈主要在计算还是 I/O 等待。 |
| Little’s Law | 稳定系统中平均在途量、到达率和停留时间的关系。 |
| Profiling / Flame Graph | 采样或插桩分析与堆栈聚合展示。 |
| Load / Stress / Soak Test | 目标负载、极限负载和长时间运行验证。 |
| Horizontal / Vertical Scaling | 增加实例与提升单实例资源。 |
| Batching / Pipelining | 合并操作和重叠多个执行阶段。 |
| Rate Limiting / Load Shedding | 约束进入速率和过载时拒绝工作。 |
| Hotspot / Contention | 局部集中访问与共享资源竞争。 |
| Queueing / Backpressure | 等待队列形成和压力反馈。 |
| Capacity Planning | 用工作负载、资源余量和增长预估容量。 |

## 练习与验收

选择上面的一个核心问题，先画执行过程或数据边界，再构造一个正常路径和一个失败路径。用原理解释、架构或代码、诊断证据和取舍依据说明保证范围；记录已完成验证与待验证项。

[回到知识地图](../../map.md) · [问题导航](../../problems.md) · [学习路径](../../paths/index.md)
