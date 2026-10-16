<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# 可观测性与可靠性

建议优先级：P0。目标：建立用户目标、故障证据与可执行恢复流程。

下方术语用于知识索引。建议从[实际工程问题](../../problems.md)或本页核心问题进入，结合已有正文理解机制、适用边界与相关概念。

## 一个核心问题

告警很多却不知道用户是否受影响，缺了什么？

## 已有正文

- [超时与重试预算：一次请求最多值得等多久](timeouts-and-retry-budgets.md)：用截止时间、尝试上限与重试安全性约束等待，避免失败时放大依赖负载。

## 术语范围

| 术语 | 简释 |
| --- | --- |
| Logs / Metrics / Traces | 离散事件、聚合数值与请求因果链。 |
| OpenTelemetry | 可观测性 API、SDK、协议及采集生态。 |
| Trace ID / Span / Correlation ID | 链路标识、执行片段和业务关联。 |
| RED / USE | 请求速率错误延迟与资源使用率饱和错误。 |
| SLI / SLO / SLA | 指标、目标和对外服务约定。 |
| Error Budget | 由可靠性目标推导的可接受失败额度。 |
| Availability / Reliability | 可提供服务的程度与持续正确工作的能力。 |
| RTO / RPO | 恢复耗时目标和可接受数据丢失范围。 |
| Circuit Breaker / Bulkhead | 熔断失败依赖与隔离资源池。 |
| Timeout / Deadline / Retry Budget | 限制等待时间、传播截止时间并约束重试消耗。 |
| Readiness / Liveness | 是否接收流量与是否需要重启的探测。 |
| Disaster Recovery / Failover | 灾难恢复计划与服务切换。 |
| Incident Response / Postmortem | 止损、诊断、恢复与复盘。 |
| Chaos Engineering | 通过受控故障验证系统假设。 |

## 练习与验收

选择上面的一个核心问题，先画执行过程或数据边界，再构造一个正常路径和一个失败路径。用原理解释、架构或代码、诊断证据和取舍依据说明保证范围；记录已完成验证与待验证项。

[回到知识地图](../../map.md) · [问题导航](../../problems.md) · [学习路径](../../paths/index.md)
