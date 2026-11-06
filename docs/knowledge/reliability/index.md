<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# 可观测性与可靠性

建议优先级：P0。目标：建立用户目标、故障证据与可执行恢复流程。

下方术语用于知识索引。建议从[实际工程问题](../../problems.md)或本页核心问题进入，结合已有正文理解机制、适用边界与相关概念。

## 一个核心问题

告警很多却不知道用户是否受影响，缺了什么？

## 已有正文

- [可用性与可靠性：服务大部分时间在线，为什么长任务仍容易失败](availability-reliability-and-observation-windows.md)：区分某时刻可用、连续完成能力及恢复，说明时间型/事件型比例、观察窗口、均值与相关故障的限制。
- [混沌工程与受控故障：注入成功，为什么还不能宣布系统可靠](chaos-engineering-hypotheses-stop-conditions-and-recovery.md)：用可反驳的稳态假设组织故障实验，区分作用确认、用户结果、影响限制、停止注入与业务恢复。
- [熔断、隔离与降级：依赖变慢以后怎样收敛](circuit-breakers-isolation-and-degradation.md)：区分[熔断](../../glossary/reliability.md#reliability.isolation)的调用许可、隔离的资源边界和降级的业务结果，解释探测恢复、[超时](../../glossary/api.md#api.retries)与共享瓶颈。
- [故障域、冗余与恢复目标：有副本为什么仍可能恢复不了](failure-domains-redundancy-and-recovery.md)：从共同故障与业务依赖解释[冗余](../../glossary/reliability.md#reliability.fault-domains)、[故障切换](../../glossary/reliability.md#reliability.dr)和灾难恢复，区分 [RTO](../../glossary/reliability.md#reliability.recovery)/RPO 目标、实际恢复时间与可恢复数据边界。
- [事故响应与复盘：告警恢复了，为什么还不能结束处理](incident-response-recovery-and-postmortems.md)：区分告警、事故声明、止损、业务恢复与复盘，建立协调责任、证据时间线、交接和可验证的改进闭环。
- [日志、指标与链路：怎样把一次故障的证据连起来](logs-metrics-and-traces.md)：区分日志、指标与链路的观察范围，解释上下文传播、[标签基数](../../glossary/reliability.md#reliability.cardinality)与采样如何影响故障证据。
- [RED 与 USE：指标齐全，为什么仍找不到故障原因](red-use-service-signals-and-resource-evidence.md)：连接服务请求的速率、错误和时长与资源利用、饱和和错误，明确计数边界、未完成工作及分布聚合。
- [SLI、SLO 与错误预算：怎样判断服务是否足够可靠](slis-slos-and-error-budgets.md)：从用户结果定义指标、目标与窗口，计算事件型[错误预算](../../glossary/reliability.md#reliability.budget)和[燃烧率](../../glossary/reliability.md#reliability.burn-rate)，并区分观测与诊断。
- [超时与重试预算：一次请求最多值得等多久](timeouts-and-retry-budgets.md)：用[截止时间](../../glossary/reliability.md#reliability.retry-budget)、尝试上限与重试安全性约束等待，避免失败时放大依赖负载。

## 术语范围

| 术语 | 简释 |
| --- | --- |
| [Logs / Metrics / Traces](../../glossary/reliability.md#reliability.signals) | 离散事件、聚合数值与请求因果链。 |
| [OpenTelemetry](../../glossary/reliability.md#reliability.otel) | 可观测性 API、SDK、协议及采集生态。 |
| [Trace ID / Span / Correlation ID](../../glossary/reliability.md#reliability.trace) | 链路标识、执行片段和业务关联。 |
| [RED / USE](../../glossary/reliability.md#reliability.methods) | [请求速率](../../glossary/performance.md#performance.rates)错误[延迟](../../glossary/performance.md#performance.latency-throughput)与资源使用率饱和错误。 |
| [SLI / SLO / SLA](../../glossary/reliability.md#reliability.slos) | 指标、目标和对外服务约定。 |
| [Error Budget](../../glossary/reliability.md#reliability.budget) | 由[可靠性](../../glossary/reliability.md#reliability.availability)目标推导的可接受失败额度。 |
| [Availability / Reliability](../../glossary/reliability.md#reliability.availability) | 可提供服务的程度与持续正确工作的能力。 |
| [RTO / RPO](../../glossary/reliability.md#reliability.recovery) | 恢复耗时目标和可接受数据丢失范围。 |
| [Circuit Breaker / Bulkhead](../../glossary/reliability.md#reliability.isolation) | 熔断失败依赖与隔离资源池。 |
| [Timeout / Deadline / Retry Budget](../../glossary/reliability.md#reliability.retry-budget) | 限制等待时间、传播截止时间并约束重试消耗。 |
| [Readiness / Liveness / Startup Probe](../../glossary/reliability.md#reliability.probes) | 区分接流量、重启恢复和启动完成的探测；探针结果不等于全部用户业务目标达成。 |
| [Disaster Recovery / Failover](../../glossary/reliability.md#reliability.dr) | 灾难恢复计划与服务切换。 |
| [Incident Response / Postmortem](../../glossary/reliability.md#reliability.incidents) | 止损、诊断、恢复与复盘。 |
| [Chaos Engineering](../../glossary/reliability.md#reliability.chaos) | 通过受控故障验证系统假设。 |
| [Error Budget Burn Rate](../../glossary/reliability.md#reliability.burn-rate) | 对事件比例型 SLO，以观察窗口的不合格比例除以预算比例，衡量相对消耗速度；不等于已消耗预算份额。 |
| [Label Cardinality](../../glossary/reliability.md#reliability.cardinality) | 指标标签或其组合的不同取值规模，影响时间序列数量与资源成本。 |
| [Failure Domain / Redundancy](../../glossary/reliability.md#reliability.fault-domains) | 按故障假设识别共同失效的范围，以独立性、剩余容量与恢复路径评价冗余，而不只统计副本数。 |

## 练习与验收

选择上面的一个核心问题，先画执行过程或数据边界，再构造一个正常路径和一个失败路径。用原理解释、架构或代码、诊断证据和取舍依据说明保证范围；记录已完成验证与待验证项。

[回到知识地图](../../map.md) · [问题导航](../../problems.md) · [学习路径](../../paths/index.md)
