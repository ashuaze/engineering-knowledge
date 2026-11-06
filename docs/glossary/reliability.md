<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# 可观测性与可靠性词汇表

本页解释 17 组术语，按[完整术语索引](../glossary.md#reliability)中的顺序排列。示例为说明性场景；具体技术版本与验证范围见各条深入阅读。

[分类词汇表](index.md) · [可观测性与可靠性文章](../knowledge/reliability/index.md)

## 本页术语

- [Logs / Metrics / Traces](#reliability.signals)
- [OpenTelemetry](#reliability.otel)
- [Trace ID / Span / Correlation ID](#reliability.trace)
- [RED / USE](#reliability.methods)
- [SLI / SLO / SLA](#reliability.slos)
- [Error Budget](#reliability.budget)
- [Availability / Reliability](#reliability.availability)
- [RTO / RPO](#reliability.recovery)
- [Circuit Breaker / Bulkhead](#reliability.isolation)
- [Timeout / Deadline / Retry Budget](#reliability.retry-budget)
- [Readiness / Liveness / Startup Probe](#reliability.probes)
- [Disaster Recovery / Failover](#reliability.dr)
- [Incident Response / Postmortem](#reliability.incidents)
- [Chaos Engineering](#reliability.chaos)
- [Error Budget Burn Rate](#reliability.burn-rate)
- [Label Cardinality](#reliability.cardinality)
- [Failure Domain / Redundancy](#reliability.fault-domains)

<a id="reliability.signals"></a>

## Logs / Metrics / Traces

**ID：** `reliability.signals` · **建议优先级：** P0

**别名 / 检索词：** Logs、Metrics、Traces、日志、指标、链路追踪

**简释：** 离散事件、聚合数值与请求因果链。

日志记录离散事件，指标聚合数值，链路追踪连接一次执行中的相关片段。三者需以时间、资源和关联标识联系，采样与丢失限制证据完整性。

**例子：** 指标发现错误率升高，再用 Trace 定位慢依赖并查对应日志细节。

**深入阅读：** [SLI、SLO 与错误预算：怎样判断服务是否足够可靠](../knowledge/reliability/slis-slos-and-error-budgets.md) · [日志、指标与链路：怎样把一次故障的证据连起来](../knowledge/reliability/logs-metrics-and-traces.md)

<a id="reliability.otel"></a>

## OpenTelemetry

**ID：** `reliability.otel` · **建议优先级：** P0

**别名 / 检索词：** OpenTelemetry、开放遥测

**简释：** 可观测性 API、SDK、协议及采集生态。

OpenTelemetry 提供生成、传播、采集和导出遥测的规范与组件。它不等同于完整存储分析后端，仍需配置采样、脱敏、保留与成本控制。

**例子：** 应用经 SDK 生成 Span，由 Collector 处理后导出到选定后端。

**深入阅读：** [日志、指标与链路：怎样把一次故障的证据连起来](../knowledge/reliability/logs-metrics-and-traces.md)

<a id="reliability.trace"></a>

## Trace ID / Span / Correlation ID

**ID：** `reliability.trace` · **建议优先级：** P0

**别名 / 检索词：** Trace ID、Span、Correlation ID、链路标识、关联标识

**简释：** 链路标识、执行片段和业务关联。

Trace ID 标识一次追踪，Span 表示其中的操作片段，Correlation ID 可关联业务工作。传播必须覆盖线程、消息与服务边界，并避免把关联标识当权限凭据。

**例子：** 异步任务带上关联信息，便于把后台处理与原请求联系起来。

**深入阅读：** [日志、指标与链路：怎样把一次故障的证据连起来](../knowledge/reliability/logs-metrics-and-traces.md)

<a id="reliability.methods"></a>

## RED / USE

**ID：** `reliability.methods` · **建议优先级：** P0

**别名 / 检索词：** RED、USE

**简释：** 请求速率错误延迟与资源使用率饱和错误。

RED观察服务的请求速率、错误及耗时，USE检查相关资源的利用、饱和与错误。接纳/完成、错误速率/比例和分布聚合需明确口径；指标相关变化只是归因线索，不自动证明因果。

**例子：** 请求耗时变高时，继续检查连接池饱和和数据库等待以定位约束。

**深入阅读：** [RED 与 USE：指标齐全，为什么仍找不到故障原因](../knowledge/reliability/red-use-service-signals-and-resource-evidence.md)

<a id="reliability.slos"></a>

## SLI / SLO / SLA

**ID：** `reliability.slos` · **建议优先级：** P0

**别名 / 检索词：** SLI、SLO、SLA、服务指标、服务目标

**简释：** 指标、目标和对外服务约定。

SLI 定义服务质量的测量方式，SLO 为其设定目标，SLA 是对外服务约定并可能含补偿条款。成功事件、窗口和排除规则必须明确。

**例子：** 以合格请求比例定义 SLI，再规定滚动窗口内达到的目标比例。

**深入阅读：** [SLI、SLO 与错误预算：怎样判断服务是否足够可靠](../knowledge/reliability/slis-slos-and-error-budgets.md)

<a id="reliability.budget"></a>

## Error Budget

**ID：** `reliability.budget` · **建议优先级：** P0

**别名 / 检索词：** Error Budget、错误预算

**简释：** 由可靠性目标推导的可接受失败额度。

错误预算由 SLO 推导可接受的不合格额度，用来协调可靠性与变更节奏。请求型和时间型目标预算口径不同，不能把所有预算都换算成停机分钟。

**例子：** 请求成功率目标为 99.9% 时，对应合格口径下允许约 0.1% 不合格请求。

**深入阅读：** [SLI、SLO 与错误预算：怎样判断服务是否足够可靠](../knowledge/reliability/slis-slos-and-error-budgets.md)

<a id="reliability.availability"></a>

## Availability / Reliability

**ID：** `reliability.availability` · **建议优先级：** P0

**别名 / 检索词：** Availability、Reliability、可用性、可靠性

**简释：** 可提供服务的程度与持续正确工作的能力。

可用性关注定义窗口和能力下是否可提供服务；可靠性可关注规定条件与期间的连续工作，也常作服务质量的上位概念。时间比例、请求比例和首次存活概率不相同，恢复在线仍需确认正确业务状态。

**例子：** 服务能响应但持续返回错误价格，不能仅凭在线状态宣称可靠。

**深入阅读：** [可用性与可靠性：服务大部分时间在线，为什么长任务仍容易失败](../knowledge/reliability/availability-reliability-and-observation-windows.md)

<a id="reliability.recovery"></a>

## RTO / RPO

**ID：** `reliability.recovery` · **建议优先级：** P0

**别名 / 检索词：** RTO、RPO、恢复时间目标、恢复点目标

**简释：** 恢复耗时目标和可接受数据丢失范围。

RTO 是恢复服务所允许的时间目标，RPO 是允许丢失的数据范围目标。两者是目标而非已证明能力，需把检测、切换、恢复与业务核对计入演练。

**例子：** 每小时备份不自动保证一小时 RPO，还需确认备份可用且恢复链完整。

**深入阅读：** [备份与时间点恢复：备份成功为何还不够](../knowledge/database/backups-and-point-in-time-recovery.md) · [故障域、冗余与恢复目标：有副本为什么仍可能恢复不了](../knowledge/reliability/failure-domains-redundancy-and-recovery.md) · [写穿与异步写回：写入成功究竟确认到了哪里](../knowledge/cache-search/write-through-write-behind-and-durability.md)

<a id="reliability.isolation"></a>

## Circuit Breaker / Bulkhead

**ID：** `reliability.isolation` · **建议优先级：** P0

**别名 / 检索词：** Circuit Breaker、Bulkhead、熔断、舱壁隔离

**简释：** 熔断失败依赖与隔离资源池。

熔断在失败达到条件后暂时阻止调用并安排探测，舱壁隔离限制不同依赖共享的资源。两者不自动取消已发出的工作，也不能替代总体超时和容量管理。

**例子：** 为慢报表单设连接额度，避免其占满交易路径使用的资源池。

**深入阅读：** [熔断、隔离与降级：依赖变慢以后怎样收敛](../knowledge/reliability/circuit-breakers-isolation-and-degradation.md)

<a id="reliability.retry-budget"></a>

## Timeout / Deadline / Retry Budget

**ID：** `reliability.retry-budget` · **建议优先级：** P0

**别名 / 检索词：** Timeout、Deadline、Retry Budget、重试预算、截止时间

**简释：** 限制等待时间、传播截止时间并约束重试消耗。

Timeout 限制局部等待，Deadline 表示整体最晚完成时刻，Retry Budget 限制重复尝试消耗。需要跨调用层传播剩余时间并处理已发生但结果未知的副作用。

**例子：** 上游只剩 200 毫秒时，不应再发起默认等待两秒的下游调用。

**深入阅读：** [超时与重试预算：一次请求最多值得等多久](../knowledge/reliability/timeouts-and-retry-budgets.md) · [Linux 信号、取消与退出：收到停止请求后由谁完成清理](../knowledge/systems/signals-cancellation-and-shutdown.md) · [TCP 流量控制与拥塞控制：发送变慢到底受谁限制](../knowledge/networking/tcp-flow-control-and-congestion.md)

<a id="reliability.probes"></a>

## Readiness / Liveness / Startup Probe

**ID：** `reliability.probes` · **建议优先级：** P0

**别名 / 检索词：** Readiness、Liveness、Startup Probe、Health Probe、健康探针、优雅终止、就绪探针、存活探针、启动探针

**简释：** 区分接流量、重启恢复和启动完成的探测；探针结果不等于全部用户业务目标达成。

Readiness 判断是否应接流，Liveness 判断是否需重启，Startup 给启动阶段单独容忍窗口。探针应针对可恢复条件设计，过度依赖共享下游可能触发级联摘流或重启。

**例子：** 数据库短暂变慢时，重启所有应用实例往往不能修复数据库瓶颈。

**深入阅读：** [声明式部署与健康探针：实例存活为什么仍不能接流量](../knowledge/devops/declarative-deployments-and-health-probes.md)

<a id="reliability.dr"></a>

## Disaster Recovery / Failover

**ID：** `reliability.dr` · **建议优先级：** P0

**别名 / 检索词：** Disaster Recovery、Failover、灾难恢复、故障切换

**简释：** 灾难恢复计划与服务切换。

灾难恢复涵盖恢复数据和业务能力的计划，故障切换把流量或角色转到备用路径。需验证容量、依赖、数据状态与回切，而非仅观察备用实例在线。

**例子：** 切到备用地域后，还要核对数据库可写、凭据有效及用户入口已更新。

**深入阅读：** [故障域、冗余与恢复目标：有副本为什么仍可能恢复不了](../knowledge/reliability/failure-domains-redundancy-and-recovery.md)

<a id="reliability.incidents"></a>

## Incident Response / Postmortem

**ID：** `reliability.incidents` · **建议优先级：** P0

**别名 / 检索词：** Incident Response、Postmortem、故障响应、事后复盘、事故响应、事故复盘

**简释：** 止损、诊断、恢复与复盘。

事故响应组织影响确认、协调、止损与业务恢复；复盘解释事实和促成条件，再为改进指定负责人、期限及效果验证。告警恢复、业务验收与集中响应结束可以是不同时间。

**例子：** 回滚恢复流量后，继续检查数据是否需要修复并记录告警为何迟到。

**深入阅读：** [事故响应与复盘：告警恢复了，为什么还不能结束处理](../knowledge/reliability/incident-response-recovery-and-postmortems.md)

<a id="reliability.chaos"></a>

## Chaos Engineering

**ID：** `reliability.chaos` · **建议优先级：** P0

**别名 / 检索词：** Chaos Engineering、混沌工程

**简释：** 通过受控故障验证系统假设。

混沌工程以可反驳的稳态假设组织受控扰动，定义作用、观测、对照、影响范围及停止/恢复条件。注入成功不证明用户目标满足，停止注入也不撤销既有业务效果；一次结果只支持给定范围。

**例子：** 隔离一个实例后，验证剩余容量和用户错误率，而非只确认实例被杀死。

**深入阅读：** [混沌工程与受控故障：注入成功，为什么还不能宣布系统可靠](../knowledge/reliability/chaos-engineering-hypotheses-stop-conditions-and-recovery.md)

<a id="reliability.burn-rate"></a>

## Error Budget Burn Rate

**ID：** `reliability.burn-rate` · **建议优先级：** P1

**别名 / 检索词：** Burn Rate、Error Budget Burn Rate、燃烧率

**简释：** 对事件比例型 SLO，以观察窗口的不合格比例除以预算比例，衡量相对消耗速度；不等于已消耗预算份额。

燃烧率衡量错误预算相对消耗速度。事件比例型目标中，可用观察窗口不合格比例除以允许比例；数值需结合窗口和流量，不能直接当作已耗尽预算百分比。

**例子：** 允许错误比例为 0.1%，某窗口实际 1%，对应燃烧率为 10。

**深入阅读：** [SLI、SLO 与错误预算：怎样判断服务是否足够可靠](../knowledge/reliability/slis-slos-and-error-budgets.md)

<a id="reliability.cardinality"></a>

## Label Cardinality

**ID：** `reliability.cardinality` · **建议优先级：** P1

**别名 / 检索词：** Label Cardinality、标签基数

**简释：** 指标标签或其组合的不同取值规模，影响时间序列数量与资源成本。

标签基数是单标签或标签组合的不同取值规模，决定指标序列数量和成本。用户 ID、原始 URL 等高变化字段通常更适合受控日志或追踪。

**例子：** 把订单 ID 作为指标标签可能随订单数量生成大量时间序列。

**深入阅读：** [日志、指标与链路：怎样把一次故障的证据连起来](../knowledge/reliability/logs-metrics-and-traces.md)

<a id="reliability.fault-domains"></a>

## Failure Domain / Redundancy

**ID：** `reliability.fault-domains` · **建议优先级：** P1

**别名 / 检索词：** Failure Domain、Fault Domain、Redundancy、故障域、冗余

**简释：** 按故障假设识别共同失效的范围，以独立性、剩余容量与恢复路径评价冗余，而不只统计副本数。

故障域描述可能因共同原因同时失效的范围；冗余需具备相应独立性、剩余容量和可用恢复路径。副本数多但共享关键依赖，仍可能一起失效。

**例子：** 两台实例共用同一电源或数据库，不等于已隔离对应故障。

**深入阅读：** [故障域、冗余与恢复目标：有副本为什么仍可能恢复不了](../knowledge/reliability/failure-domains-redundancy-and-recovery.md) · [一致性哈希与数据放置：节点变化后哪些键需要搬走](../knowledge/distributed/consistent-hashing-placement-and-rebalancing.md)

## 资料与延伸

下列资料提供相关机制的进一步说明，并不表示覆盖本页所有术语。各条已关联的专题文章另列具体来源、适用版本与验证边界。

- [Google SRE：服务目标与故障管理](https://sre.google/sre-book/table-of-contents/)
- [OpenTelemetry：遥测信号](https://opentelemetry.io/docs/concepts/signals/)
- [Google SRE：事故管理](https://sre.google/sre-book/managing-incidents/)
- [Google SRE：无责复盘](https://sre.google/sre-book/postmortem-culture/)
- [Grafana 对 Tom Wilkie RED 方法的介绍](https://grafana.com/blog/the-red-method-how-to-instrument-your-services/)
- [Brendan Gregg 的 USE](https://www.brendangregg.com/usemethod.html)
- [Prometheus 的直方图与摘要说明](https://prometheus.io/docs/practices/histograms/)
- [NIST reliability 词条](https://csrc.nist.gov/glossary/term/reliability)
- [Google SRE Embracing Risk](https://sre.google/sre-book/embracing-risk/)
- [NIST 的 survival function](https://www.itl.nist.gov/div898/handbook/apr/section1/apr122.htm)
- [Principles of Chaos Engineering](https://principlesofchaos.org/)
- [AWS FIS stop conditions](https://docs.aws.amazon.com/fis/latest/userguide/stop-conditions.html)
- [Google SRE Testing for Reliability](https://sre.google/sre-book/testing-reliability/)

[返回分类词汇表](index.md) · [完整术语索引](../glossary.md)
