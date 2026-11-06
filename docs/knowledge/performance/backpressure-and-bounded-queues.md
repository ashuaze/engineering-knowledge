---
id: "kb-performance-backpressure"
title: "背压与有界队列：把等待放在哪里"
kind: "concept"
domain: "performance"
status: "evolving"
summary: "区分缓存突发、拒绝过载与向上游反馈容量，追踪限制之外的等待、内存和截止时间。"
created: "2026-10-19"
updated: "2026-10-26"
last_verified: "2026-10-19"
verification: "source-checked"
prerequisites: ["kb-performance-latency-queues"]
related: ["kb-performance-overload-lab", "kb-api-admission-controls", "kb-reliability-failure-isolation", "kb-reliability-retry-budgets", "kb-systems-synchronization", "kb-networking-http-pools", "kb-networking-connections-lab", "kb-algorithms-linear-structures", "kb-algorithms-trees-heaps", "kb-cache-load-coalescing", "kb-performance-batching-pipelines", "kb-performance-capacity-autoscaling"]
tags: ["backpressure", "bounded-queue", "admission-control", "overload"]
---

# 背压与有界队列：把等待放在哪里

学习入口：消费者只能同时处理四项工作，为什么改成异步后内存仍不断增长？前置：能区分到达率、完成吞吐和在途数量。本文核查机制与 API；配套[过载实验](overload-control-lab.md)只验证本地调度和接纳边界。

在途窗口怎样约束见[批处理与流水线](batching-pipelining-and-amortized-waiting.md)；有界接纳与[容量规划与自动扩缩容](capacity-planning-scaling-and-autoscaling-feedback.md)相配合，扩容等待期间仍要控制积压。

## 队列吸收突发，不能制造处理能力

等待[队列](../../glossary/algorithms.md#algorithms.queues)把生产和消费在时间上分开。短突发结束后，消费者可能利用余量消化积压；持续输入高于处理能力时，没有过期、拒绝或减速的队列会继续增长。每一项还可能持有请求体、上下文、连接和回调；按“条数”设上限，不能自动限制字节数。

扩大队列会改变等待位置与内存成本，不保证增加有效吞吐。教学推演：四个执行槽、每项占用 40ms，忽略其他成本，理想完成速率是 100 项/秒。若持续到达 240 项/秒，多出的工作需要等待、被拒绝或由上游减少；这些数字不是生产配置建议。先读[延迟与排队](latency-throughput-and-queues.md)理解统计边界。

## 有界与背压是不同的约定

| 队列满时的动作 | 调用方看到什么 | 压力最终去了哪里 |
| --- | --- | --- |
| 等待空位 | 生产调用挂起，恢复后才提交 | 若生产者受此约束，可降低继续生产的速度 |
| 立即拒绝 | 明确的未接纳结果 | 上游必须决定停止、稍后[重试](../../glossary/api.md#api.retries)或返回失败 |
| 丢弃或合并 | 部分工作被舍弃或替换 | 业务需要允许丢失，且能识别实际处理的版本 |
| 转存其他队列 | 当前提交成功 | 积压移到其他存储，仍需容量与过期策略 |

[背压](../../glossary/performance.md#performance.queueing)是下游的容量约束影响上游生产的反馈关系。有界队列是一个实现约束；仅返回拒绝并没有证明上游会减速。[Reactive Streams](https://www.reactive-streams.org/)给出了异步流中按需求传递元素的协议；它的需求信号不能直接等同于任意 HTTP 服务的业务接纳协议。

Python 3.13 的 [asyncio.Queue](https://docs.python.org/3.13/library/asyncio-queue.html)提供具体反例：`maxsize=0` 表示无界；正数上限下，`await put()` 在满时等待，`put_nowait()` 则抛出 `QueueFull`。两种调用使用同一个上限，反馈行为不同。本库实验用后者比较拒绝；另有[契约测试](../../glossary/engineering.md#engineering.contracts)验证前者会等待空位。

## 限制之外可能还有队列

只在工作[协程](../../glossary/systems.md#systems.execution-units)里获取 [Semaphore](../../glossary/systems.md#systems.synchronization)，可以限制同时持有许可的人，却可能先创建成千上万个等待许可的任务。调用方等待池连接、代理缓存请求体、重试定时器和持久消息积压，也都可能位于业务队列之外。

设计时沿着“入口 → 身份与接纳 → 等待 → 执行 → 外部依赖”逐段写出：谁持有资源、谁能继续生产、满时怎样返回、取消怎样移除等待者。入口也有解析和拒绝成本；业务队列有界不表示整个进程内存有界。[TCP 接收窗口](https://www.rfc-editor.org/rfc/rfc9293.html#name-managing-the-window)约束字节传输，不能证明每个到达的业务请求都有执行容量。

等待生产者时还要检查依赖环：生产者若持有消费者完成工作必需的锁，再等待队列空位，可能互相等待。[同步原语](../systems/locks-and-synchronization.md)保护的范围与排队位置需要一起判断。

## 队列长度还需要时间与业务边界

任务排到空位时可能已经过期。应携带[截止时间](../../glossary/reliability.md#reliability.retry-budget)，入队、出队和昂贵调用前检查剩余预算；等待和执行共用同一个端到端预算。调用方超时后，已接纳工作是否继续，需要明确取消协议和清理责任，详见[重试预算](../reliability/timeouts-and-retry-budgets.md)。

队列上限也不提供公平性。单个租户可以占满所有空位；FIFO 可能让便宜请求等在昂贵请求后面。按租户、优先级或成本分配资源时，要明确饥饿风险与共享总上限；使用多个队列并不自动隔离共享数据库和 CPU。

## 怎样观察保护是否有效

同时记录尝试、接纳、完成、拒绝、超时、队列长度和队列等待分布。把成功完成的[延迟](../../glossary/performance.md#performance.latency-throughput)和拒绝返回时间分开；快速拒绝增多可能让总体响应时间变短，但可用的业务结果减少。到达阶段结束后的排空成本也应记录。

[本地过载实验](overload-control-lab.md)比较无界等待、12 项有界等待和无业务等待队列的[并发](../../glossary/systems.md#systems.concurrency)准入。它使用真实定时与协程调度，工作本身是合成等待；没有实现上游自适应减速、真实 HTTP [连接池](../../glossary/api.md#api.pool)或业务成本估计。

另有[真实回环 HTTP/1.1 实验](../networking/connection-lifecycle-lab.md)，展示连接上限之外的池等待与正文消费；未覆盖跨代理或真实负载容量。

自检：将队列从 100 项改成 1,000 项后不再报满，能否说容量提高十倍？需要先检查完成速率、超时和排空时间，再追问上游是否真的减少输入。

合并同一键的重复读取之后，等待者、不同键和依赖调用仍会占用资源，继续见[缓存加载合并与惊群控制](../cache-search/cache-load-coalescing-and-stampedes.md)。共享工作需要自身的寿命与总容量边界。

## 关联阅读与来源

[容器](../../glossary/devops.md#devops.containers)基础继续读[线性结构与端点操作](../algorithms/sequences-stacks-queues-and-deques.md)及[树、堆与优先队列](../algorithms/trees-heaps-and-priority-queues.md)。有界 deque 的丢弃行为和优先堆的取出规则，都不自动提供本篇的可靠接纳或背压协议；没有重跑或扩大既有过载实验。

- [限流、并发限制与配额](../api/rate-limits-concurrency-and-quotas.md)：明确时间窗、在途数和累计用量。
- [熔断、隔离与降级](../reliability/circuit-breakers-isolation-and-degradation.md)：限制故障依赖占用与恢复探测。
- [Google SRE：Cascading Failures](https://sre.google/sre-book/addressing-cascading-failures/)：资源耗尽、积压与级联失败。

核查日期：2026-10-19。API 与协议说明依据上述一手资料；队列位置、截止时间检查表及算例为教学综合，具体实验结果只由独立实验页承担。
