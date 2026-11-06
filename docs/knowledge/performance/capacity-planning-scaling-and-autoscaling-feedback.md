---
id: "kb-performance-capacity-autoscaling"
title: "容量规划与自动扩缩容：副本增加为什么不等于能力立即增加"
kind: "concept"
domain: "performance"
status: "evolving"
summary: "从请求成本和故障余量估算容量，区分水平/垂直扩容、HPA 指标分母、原始建议及就绪能力。"
created: "2026-10-26"
updated: "2026-10-26"
last_verified: "2026-10-26"
verification: "source-checked"
prerequisites: ["kb-performance-cpu-metrics", "kb-performance-latency-queues", "kb-devops-declarative-health"]
related: ["kb-performance-hotspots-contention", "kb-performance-batching-pipelines", "kb-performance-benchmarking", "kb-reliability-fault-domains-recovery", "kb-api-admission-controls"]
tags: ["capacity-planning", "scaling", "autoscaling", "hpa", "headroom"]
---

# 容量规划与自动扩缩容：副本增加为什么不等于能力立即增加

学习入口：[HPA](../../glossary/devops.md#devops.autoscaling) 已把期望副本数提高，为什么[队列](../../glossary/algorithms.md#algorithms.queues)仍在增长？先估算实际工作负载需要什么资源，再区分期望、调度、启动、就绪与最终有用吞吐。

前置：[CPU 时间与配额](cpu-time-utilization-load-and-quotas.md)、[延迟与排队](latency-throughput-and-queues.md)、[声明式控制](../devops/declarative-deployments-and-health-probes.md)。HPA 参照 Kubernetes v1.36，算例仅为纸面模型，不是部署规格或容量承诺；未压测、调节资源或运行扩缩容。

## 容量取决于工作成本与约束

每秒请求数相同，请求体、查询范围、缓存命中、写入比例和[重试](../../glossary/api.md#api.retries)次数不同，资源成本就可能不同。容量目标应同时声明[延迟](../../glossary/performance.md#performance.latency-throughput)、失败比例、观察窗口和资源条件；不能把某次达到峰值的请求数当作长期安全能力。

[Google SRE Handling Overload](https://sre.google/sre-book/handling-overload/)讨论按实际资源限制组织接纳与过载收敛。CPU、内存、连接、存储和下游服务可能分别成为上限；只增加一个维度并不保证整体变快。

## 纸面 CPU 预算与故障余量

假设每个同质副本能使用 2 核 CPU，计划利用上限为 70%，每请求消耗 0.005 CPU 秒；流量能合理分摊到可用副本，请求可充分利用这些核，忽略其他瓶颈与调度开销：

```text
每副本目标能力 = 2 × 0.70 / 0.005 = 280 请求/秒
1000 请求/秒至少需 ceil(1000 / 280) = 4 个可用副本
若要在失去一个副本后仍保留这4个，教学配置至少需5个
```

5 是这组条件下的数量预算，不保证[故障域](../../glossary/reliability.md#reliability.fault-domains)分布、数据库和内存也满足目标。若一个故障域同时丢掉多个副本，或平均成本掩盖重请求，就需重新计算并验证。

[水平扩容](../../glossary/performance.md#performance.scaling)增加实例，垂直扩容提高单实例资源。前者可能要求状态分布与协调，后者受单机限制、配额和代码[并行](../../glossary/systems.md#systems.concurrency)度影响；两者都不能自动解除热键或共享数据库的串行瓶颈。

## HPA 根据观测建议，不直接创造就绪能力

[Kubernetes v1.36 HPA](https://v1-36.docs.kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/)的基础比例模型为：

```text
原始建议副本数 = ceil(当前副本数 × 当前指标 / 目标指标)
```

另作一个独立例子：10 个 [Pod](../../glossary/devops.md#devops.k8s) 各声明 CPU request=1 核，相关平均使用量为 0.75 核，即相对 request 的 75%；目标为 50%，原始建议 `ceil(10×75/50)=15`。这里的 75% 不是相对节点总核数，也不是自动按 CPU limit 计算。

该式尚未包含缺失指标、未就绪 Pod、容忍区间、上下限、稳定窗口与变更速率等规则。多个指标、指标故障和实际资源约束还需依版本核对，不能把 15 写成“控制器必然立即得到 15 个就绪副本”。

## 反馈回路有延迟，扩容也可能放大依赖压力

从采集指标到决定、调度、拉取[镜像](../../glossary/devops.md#devops.containers)、初始化、加载运行所需状态和流量接入都有时间。新 Pod 若因节点不足处于 Pending，调整 HPA 不会自动扩出节点；新增连接还可能让已经饱和的数据库更忙。启动/就绪的区别见 [Pod 生命周期](https://v1-36.docs.kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)。

只看 CPU 可能遗漏 I/O [阻塞](../../glossary/systems.md#systems.blocking)和队列积压；只看总队列长度，也可能忽略单项成本和分区不均。指标应能反映该扩容动作真正能改善的工作量，并定义采集缺失时的行为。

缩容还需要限制震荡、排空工作并保留恢复余量。消费位置、长流和外部状态不能随着 Pod 删除自动恢复，见[优雅关闭](../api/graceful-shutdown-draining-and-inflight-outcomes.md)。

## 用负载与故障验证预算

分别检查常态、突发、冷启动、[缓存失效](../../glossary/cache-search.md#cache-search.invalidation)、单副本/故障域损失和依赖降速。记录到达与有用完成、[排队](../../glossary/performance.md#performance.queueing)、失败、资源及扩缩时序，避免把重试流量或快速拒绝都算作业务能力。模型是提出假设的工具，验证范围见[基准测试](benchmarks-workloads-and-speedup.md)。

## 自检

1. [请求速率](../../glossary/performance.md#performance.rates)相同为什么仍需不同容量？
2. 2 核、70%、0.005 CPU 秒得到多少？1000 请求/秒及失去一个副本时需多少？
3. HPA 的 10、75%、50% 得到什么原始建议？CPU 百分比的分母是什么？
4. 为什么期望副本增加不保证就绪能力立刻增加？
5. 水平/垂直扩容、缩容和故障余量各需核对哪些限制？

## 来源与核查

2026-10-26 核查 Google SRE 过载章节及 Kubernetes v1.36 HPA、Pod 生命周期文档。本文为 source-checked 概念文章；未执行容量/成本测量、HPA、节点扩容、冷启动、缩容排空或故障容量实验。
