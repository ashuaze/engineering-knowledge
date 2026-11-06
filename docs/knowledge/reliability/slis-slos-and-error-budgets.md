---
id: "kb-reliability-slos"
title: "SLI、SLO 与错误预算：怎样判断服务是否足够可靠"
kind: "concept"
domain: "reliability"
status: "evolving"
summary: "从用户结果定义指标、目标与窗口，计算事件型错误预算和燃烧率，并区分观测与诊断。"
created: "2026-10-16"
updated: "2026-10-27"
last_verified: "2026-10-16"
verification: "source-checked"
prerequisites: []
related: ["kb-performance-latency-queues", "kb-performance-slow-api", "kb-reliability-retry-budgets", "kb-devops-delivery-lifecycle", "kb-reliability-telemetry", "kb-devops-declarative-health", "kb-reliability-fault-domains-recovery", "kb-reliability-red-use", "kb-reliability-availability-models", "kb-reliability-chaos-experiments"]
tags: ["sli", "slo", "error-budget", "observability"]
---

# SLI、SLO 与错误预算：怎样判断服务是否足够可靠

学习入口：CPU 不高、监控全绿，用户却一直投诉失败，[服务目标](../../glossary/reliability.md#reliability.slos)该怎样定义？前置知识：请求成功与失败、比例与统计窗口。本文用请求事件定义服务目标，数字为教学计算，没有接入生产监控；具体阈值需由服务相关方根据用户需求确定。

指标的服务/资源边界见[RED与USE](red-use-service-signals-and-resource-evidence.md)，时间/事件与连续工作含义见[可用性与可靠性](availability-reliability-and-observation-windows.md)；目标怎样用于故障验证见[混沌工程与受控故障](chaos-engineering-hypotheses-stop-conditions-and-recovery.md)。

## 从用户结果区分三个概念

| 概念 | 回答的问题 | 示例 |
| --- | --- | --- |
| SLI（服务水平指标） | 用户得到的服务水平是多少 | 合格订单请求中，成功且在 500ms 内完成的比例 |
| SLO（服务水平目标） | 在什么窗口达到什么水平 | 滚动 28 天内，上述比例至少为 99.9% |
| SLA（服务水平协议） | 对服务水平有哪些约定及违约后果 | 按约定口径衡量，并约定未达标时的处理 |

这一区分依据 [Google 的服务水平目标说明](https://sre.google/sre-book/service-level-objectives/)。内部有 SLO 不代表已经作出同口径的外部协议；目标数字也需要连同对象、窗口和计算方式一起阅读。

CPU、内存、[队列](../../glossary/algorithms.md#algorithms.queues)长度有助于解释资源状态，单独看并不能代表用户完成了任务。HTTP 200 也可能承载业务失败；若接口只表示“已接收”，完成率和完成时延还要观察后续流程。

## 把分子、分母与测量位置写完整

对常见事件型 SLI，可以定义：

```text
SLI = good_events / eligible_events
good_events：符合用户结果与时延等条件的事件数
eligible_events：按预先约定规则纳入评估的事件数
```

[Google 的 SLO 实施指南](https://sre.google/workbook/implementing-slos/)区分“希望评价什么结果”与“实际在哪里怎样测量”。服务端日志无法覆盖所有未到达服务端的请求，客户端测量也会有采样和上报缺失。

一份能复核的指标定义，至少包括这些内容：

- **对象与边界**：哪个用户旅程、接口、区域或租户，起点与终点是什么。
- **纳入规则**：哪些请求合格；无效输入、健康检查、测试流量与客户端取消如何分类。
- **好事件条件**：成功的业务含义、时延阈值、数据新鲜度或正确性条件。
- **窗口与测量**：滚动还是日历窗口，使用哪个数据源，缺失与[延迟](../../glossary/performance.md#performance.latency-throughput)到达的数据怎么处理。

排除规则应事先确定并可审计。因服务过载而产生的拒绝，若属于该用户旅程，就不能为了提高成功率临时移出分母。客户端[重试](../../glossary/api.md#api.retries)也应说明按尝试还是按一次用户操作计数：尝试指标适合看请求行为，旅程指标更接近最终体验。

## 错误预算是允许的不合格比例

对目标比例 S，[错误预算](../../glossary/reliability.md#reliability.budget)比例为 `1 - S`。在一个已经确定分母 N 的窗口，允许的不合格事件数为 `N × (1 - S)`。

教学例子：目标 99.9%，窗口内有 1,000,000 次合格请求，预算是 1,000 次不合格事件。若已有 400 次不合格，已消耗 40%，剩余 600 次。成功但超过延迟门槛的请求，若不符合本指标的好事件条件，也要消耗预算。

请求型预算不能直接换算为允许停机多少分钟：高峰和低峰的流量不同，同样停机一分钟可能影响不同数量的请求。时间型[可用性](../../glossary/reliability.md#reliability.availability)指标有另一种分母，必须单独定义。滚动窗口中事件会移出，流量也会变化，剩余额度不是一个永久固定的库存。

## 燃烧率描述消耗速度

对上述事件型目标，可用某观察窗口内的不合格比例 r，计算[燃烧率](../../glossary/reliability.md#reliability.burn-rate)；机制依据 [Google 的 SLO 告警说明](https://sre.google/workbook/alerting-on-slos/)：

```text
燃烧率 burn_rate = r / (1 - S)
```

目标为 99.9% 时，若近期不合格比例为 1%，燃烧率为 10。它表示该窗口的不合格比例达到预算比例的十倍，不表示已经消耗总预算的 10%，也不自动给出“还能撑几小时”。预测耗尽时间，还需要未来流量、持续时间和窗口规则等假设。

短窗口反应快但容易受少量样本影响，长窗口更稳定但可能发现得晚。告警需要组合观察窗口、预算消耗与影响范围，并说明数据缺失、无请求和低流量时的行为；没有请求时，比例可能没有定义，不能自动按 100% 成功处理。本文不提供可直接上线的告警阈值。

## 把预算接到决策和诊断

预算帮助决定何时优先改进可靠性、控制发布风险，而不是给团队分配可以随意造成的故障额度。[Google 的错误预算政策示例](https://sre.google/workbook/error-budget-policy/)把预算状态与发布及改进工作关联，但其中规则属于特定示例，不能直接当作所有组织的制度。

一份本地政策可以说明负责人、接近或耗尽预算时的动作、紧急修复例外和恢复条件。若不达标，却只改目标或排除范围来消除报表上的问题，实际用户影响不会因此解决；目标调整应有需求与测量依据。

SLO 告诉我们用户结果是否偏离目标，诊断还需要其他证据：[Metrics](../../glossary/reliability.md#reliability.signals) 提供聚合变化，Logs 记录具体事件，Traces 关联一次执行中的跨度与依赖。它们需要共同的业务边界与[关联标识](../../glossary/reliability.md#reliability.trace)；追踪采样数据通常不能未经校正就当作完整请求分母。[监控分布式系统章节](https://sre.google/sre-book/monitoring-distributed-systems/)提供了从用户症状和内部信号分别观测的依据。

## 纸面自检与关联阅读

为一个真实用户操作写一份指标定义，构造“快速失败”“成功但超时”“未到达服务端”和“没有流量”四种情形，逐一判断如何计数。再把 99.9% 的目标换成 99.95%，在同一百万请求中算出预算减为 500 次，解释为什么不能仅凭数字决定成本是否值得。

- [日志、指标与链路](logs-metrics-and-traces.md)：连接服务目标与诊断信号，区分采样明细与总体分母。
- [延迟、吞吐与排队](../performance/latency-throughput-and-queues.md)：限定时延、速率和统计分布的边界。
- [慢 API 排查](../performance/slow-api-investigation.md)：从用户症状进一步定位等待的证据。
- [重试预算](timeouts-and-retry-budgets.md)：约束单次调用恢复的额外尝试；与服务窗口内的错误预算作用不同。
- [构建、部署与回滚](../devops/build-deploy-rollback.md)：将观测到的用户影响作为发布判断的输入。

核查日期：2026-10-16。定义、事件比例和预算政策依据 Google SRE 资料。订单条件、数字与验证题为教学综合，未部署指标或告警规则，不代表本知识库已承诺对应 SLO。

- [Google SRE：Service Level Objectives](https://sre.google/sre-book/service-level-objectives/)
- [Google SRE Workbook：Implementing SLOs](https://sre.google/workbook/implementing-slos/)
- [Google SRE Workbook：Example Error Budget Policy](https://sre.google/workbook/error-budget-policy/)
- [Google SRE Workbook：Alerting on SLOs](https://sre.google/workbook/alerting-on-slos/)
- [Google SRE：Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/)

[声明式部署与健康探针](../devops/declarative-deployments-and-health-probes.md)区分控制器、就绪与用户结果；[故障域、冗余与恢复目标](failure-domains-redundancy-and-recovery.md)解释特定故障下的 [RTO](../../glossary/reliability.md#reliability.recovery)/RPO。探针成功、恢复目标达成和窗口 SLO 分别需要对应证据，不能直接相互换算；新篇均无新增集成实测。
