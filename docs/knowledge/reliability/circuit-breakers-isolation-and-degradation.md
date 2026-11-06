---
id: "kb-reliability-failure-isolation"
title: "熔断、隔离与降级：依赖变慢以后怎样收敛"
kind: "concept"
domain: "reliability"
status: "evolving"
summary: "区分熔断的调用许可、隔离的资源边界和降级的业务结果，解释探测恢复、超时与共享瓶颈。"
created: "2026-10-19"
updated: "2026-10-20"
last_verified: "2026-10-19"
verification: "source-checked"
prerequisites: ["kb-reliability-retry-budgets", "kb-performance-latency-queues"]
related: ["kb-performance-backpressure", "kb-api-admission-controls", "kb-performance-overload-lab", "kb-reliability-slos", "kb-cache-search-cache-aside", "kb-devops-declarative-health", "kb-reliability-fault-domains-recovery"]
tags: ["circuit-breaker", "bulkhead", "degradation", "recovery"]
---

# 熔断、隔离与降级：依赖变慢以后怎样收敛

学习入口：推荐服务变慢，为什么连不需要推荐的订单查询也开始[超时](../../glossary/api.md#api.retries)？前置：超时预算、资源池与请求成功语义。本文核查架构机制，故障时序为教学设计；没有执行[熔断](../../glossary/reliability.md#reliability.isolation)状态机、真实依赖故障或线上恢复实验。

## 三种机制回答不同问题

| 机制 | 决定什么 | 必须补充的边界 |
| --- | --- | --- |
| 熔断 Circuit Breaker | 根据近期故障或慢调用信号，是否继续发起某类依赖调用 | 统计窗口、错误分类、探测和恢复条件 |
| 舱壁隔离 Bulkhead | 哪些调用共享多少执行槽、连接与等待空间 | 共享 CPU、内存、数据库等剩余[耦合](../../glossary/architecture.md#architecture.coupling) |
| 降级 Degradation | 原能力不可用时，允许返回怎样的替代结果 | 数据新鲜度、权限、正确性与用户可见语义 |

它们可以组合。隔离减少单个依赖耗尽公共资源的范围；熔断减少继续打向异常依赖的尝试；降级改变允许提供的能力。设置了一个开关，不会自动完成其他两项设计。[Microsoft 的舱壁模式](https://learn.microsoft.com/en-us/azure/architecture/patterns/bulkhead)解释了按资源分区限制故障扩散的思路。

## 熔断状态中的“开”是阻止调用

| 状态 | 新调用 | 转换示意 |
| --- | --- | --- |
| Closed，闭合 | 按通常路径尝试，并收集结果 | 足够样本下达到配置的失败条件后打开 |
| Open，打开 | 快速返回熔断结果，不发起受保护调用 | 到达探测时机后进入半开 |
| Half-open，半开 | 只放行有限探测，其余仍受限 | 探测符合恢复条件则闭合，失败则重新打开 |

这是[熔断模式](https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker)的概念状态，不是某个库的默认阈值。实现可能按失败数、比例、慢调用、最小样本及时间窗判断，恢复策略也不同。鉴权失败、参数错误与预期业务拒绝不能不加区分地归为依赖故障；本地准入拒绝是否进入统计，也要单独约定。

打开后通常不会自动终止已经在途的调用。探测应有数量与时间预算，避免所有实例同时恢复造成新一轮冲击；单个实例半开一次，不等于整个集群只发出一次探测。路由、依赖操作和租户之间的统计边界会影响误伤范围。

## 超时与隔离负责熔断生效之前的成本

如果一次调用很久才返回失败，熔断器可能尚未积累足够信号，执行槽已经占满。每次依赖调用仍需[截止时间](../../glossary/reliability.md#reliability.retry-budget)与[并发](../../glossary/systems.md#systems.concurrency)上限；等待[队列](../../glossary/algorithms.md#algorithms.queues)也要有界。取消需要等待实际释放或走清理协议，不能把调用方返回当作下游已停止。

教学设计：推荐与订单查询分别有[连接池](../../glossary/api.md#api.pool)和等待上限，推荐槽满时只拒绝推荐工作。若两个池仍访问同一数据库[热点](../../glossary/performance.md#performance.contention)、竞争同一[事件循环](../../glossary/runtime.md#runtime.event-loop)或占满宿主内存，故障仍可能扩散。分池会带来空闲容量难以互借的代价；分[进程](../../glossary/systems.md#systems.execution-units)或分机器则增加调度与运维成本。隔离强度需要按实际[故障域](../../glossary/reliability.md#reliability.fault-domains)判断，不能以池的名字证明隔离完成。

## 降级必须保留业务真相

教学例子：推荐不可用时，可以返回明确标记的空推荐区域；读取缓存时需说明版本、时间与访问范围。对写入付款、扣库存或权限判断，不能用“默认成功”掩盖未完成动作。若缓存含其他租户数据，降级也不能跳过[授权](../../glossary/security.md#security.identity)。

降级路径自己也会消耗资源：推荐失败后所有请求转查数据库，可能把压力送往另一个瓶颈。需要给替代路径独立预算与上限，同时观察提供了多少正常能力、多少替代结果和多少失败；降级结果是否计入 [SLI](../../glossary/reliability.md#reliability.slos) 的好事件，由事先约定的用户目标决定。[Google SRE 的过载处理](https://sre.google/sre-book/handling-overload/)讨论了服务降级与接纳保护；它不替代每项业务的成功定义。

## 恢复不能只看开关回到闭合

恢复检查应覆盖依赖[延迟](../../glossary/performance.md#performance.latency-throughput)与错误、探测并发、在途清理、积压排空、缓存回填及重试流量。积压和客户端重试可能在依赖恢复后继续施压。逐步恢复、探测错峰和重试预算是可选设计手段，具体参数需要测量，不能照搬纸面阈值。

[过载实验](../performance/overload-control-lab.md)只提供固定执行槽、有界拒绝与本地取消清理的证据。它没有失败率窗口、半开探测或降级业务结果，不能把其中的拒绝模式称作熔断实验。

## 用什么问题验收设计

画出一个依赖持续变慢的时序：何时达到并发上限，哪些请求被拒绝，何时进入熔断，谁发探测，业务返回什么，恢复后积压如何消退。为每一步指定可观测信号和用户影响，而不是只记录“熔断已启用”。

自检：订单池和推荐池各自独立，但推荐逻辑在同一线程上执行长计算，订单查询仍卡住，为什么？先找共享执行者，再判断是否需要改变执行位置与[资源隔离](../../glossary/devops.md#devops.isolation)边界。

## 关联阅读与来源

- [背压与有界队列](../performance/backpressure-and-bounded-queues.md)：等待与拒绝怎样向上游传递。
- [限流、并发与配额](../api/rate-limits-concurrency-and-quotas.md)：时间和资源的不同计量边界。
- [SLI/SLO](slis-slos-and-error-budgets.md)：区分成功、降级、拒绝和超时的用户结果。
- [缓存失效](../cache-search/cache-aside-and-invalidation.md)：替代读取的版本与并发约束。

核查日期：2026-10-19。状态与隔离机制依据 Microsoft 架构模式，过载保护依据 Google SRE；业务例子、恢复清单与资源组合为教学综合，未执行依赖故障实验。

[声明式部署与健康探针](../devops/declarative-deployments-and-health-probes.md)展开依赖变慢时 [readiness](../../glossary/reliability.md#reliability.probes)/liveness 的不同动作及重启反馈；[故障域与恢复目标](failure-domains-redundancy-and-recovery.md)继续检查跨实例共同依赖和剩余容量。两篇为概念推演，未补充真实熔断、探针或容灾恢复证据。
