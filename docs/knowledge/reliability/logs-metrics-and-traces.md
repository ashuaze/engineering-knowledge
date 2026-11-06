---
id: "kb-reliability-telemetry"
title: "日志、指标与链路：怎样把一次故障的证据连起来"
kind: "concept"
domain: "reliability"
status: "evolving"
summary: "区分日志、指标与链路的观察范围，解释上下文传播、标签基数与采样如何影响故障证据。"
created: "2026-10-19"
updated: "2026-10-27"
last_verified: "2026-10-19"
verification: "source-checked"
prerequisites: []
related: ["kb-reliability-slos", "kb-performance-slow-api", "kb-database-indexes-plans", "kb-ai-evals", "kb-reliability-incident-response", "kb-reliability-red-use", "kb-reliability-chaos-experiments"]
tags: ["observability", "telemetry", "context-propagation"]
---

# 日志、指标与链路：怎样把一次故障的证据连起来

学习入口：指标显示接口变慢，但日志里没有报错，下一步看什么？前置知识：一次请求会经过服务和数据依赖，了解平均[延迟](../../glossary/performance.md#performance.latency-throughput)与[尾延迟](../../glossary/performance.md#performance.percentiles)的区别。本文以请求式服务说明三类遥测的分工，依据 [OpenTelemetry](../../glossary/reliability.md#reliability.otel) 概念与 Prometheus 实践文档；不提供已部署的采集系统，也不假定所有语言与 SDK 的自动采集能力相同。

指标口径、服务/资源视角及分布合并见[RED与USE](red-use-service-signals-and-resource-evidence.md)；观测怎样支撑稳态假设与恢复判断见[混沌工程与受控故障](chaos-engineering-hypotheses-stop-conditions-and-recovery.md)。

## 三类信号回答不同问题

[OpenTelemetry 的信号说明](https://opentelemetry.io/docs/concepts/signals/)把遥测视为描述系统活动的输出。[Logs](../../glossary/reliability.md#reliability.signals)、Metrics、Traces 是常用的三类信号，系统也可能需要剖析等其他证据，不能把工具装好等同于已经能解释任意故障。

| 信号 | 主要表达什么 | 排查时适合问什么 | 主要缺口 |
| --- | --- | --- | --- |
| 日志 Logs | 某时刻发生的事件及上下文 | 哪个分支、错误类型或业务判断出现了 | 没记录的阶段无法还原；文本可能难以关联 |
| 指标 Metrics | 随时间观测的计数、数值或分布 | 哪段时间、哪类请求、多少比例异常 | 聚合通常不保留每个请求的完整细节 |
| 链路 Traces | 一次操作经过的多个带时间的工作片段 | 这次请求经过哪里，时间花在哪个边界 | 采样、漏埋点和传播失败都可能造成缺失 |

计数器适合累计完成次数等事件，Gauge 适合当前[排队](../../glossary/performance.md#performance.queueing)数等可增可减的量，Histogram 适合记录延迟分布。指标类型与标签的选择应服务于问题，而不是把每条日志都改写成一个指标。类型说明见 [Prometheus 的埋点实践](https://prometheus.io/docs/practices/instrumentation/)。

## Span 与上下文怎样连成链路

[Span](../../glossary/reliability.md#reliability.trace) 是一段有开始、结束和属性的操作记录。Trace ID 标识所属链路，Span ID 标识其中的片段，父子关系描述调用关系；异步[批处理](../../glossary/performance.md#performance.batching)等场景还可能使用链接表达关联，具体结构见 [OpenTelemetry Traces](https://opentelemetry.io/docs/concepts/signals/traces/)。应先定义“测量从哪里开始、到哪里结束”，再给片段命名。

例如“数据库调用耗时”若从取得连接后才开始记录，就不包含[连接池](../../glossary/api.md#api.pool)等待；如果从请求连接前开始，则可能包含等待与执行。两个同名片段若边界不同，数值不能直接对比。子调用也可能[并行](../../glossary/systems.md#systems.concurrency)或嵌套，不能把所有 Span 的耗时相加当作请求耗时。

[OpenTelemetry 的上下文传播说明](https://opentelemetry.io/docs/concepts/context-propagation/)解释了本地上下文及跨服务的注入、提取。HTTP 可通过 W3C `traceparent` 等格式传递 Trace ID 与父片段信息；仅在本地生成一个 ID，不会自动把下游调用接起来。[线程](../../glossary/systems.md#systems.execution-units)切换、自定义异步[队列](../../glossary/algorithms.md#algorithms.queues)或消息边界也需要相应集成。

Trace ID 是观测关联标识，不能代替身份验证、[授权](../../glossary/security.md#security.identity)或业务[幂等](../../glossary/api.md#api.idempotency)键。订单 ID 表达业务对象，请求 ID 表达应用约定的一次请求，Trace ID 表达追踪关系；[重试](../../glossary/api.md#api.retries)和异步操作使它们未必一一对应。日志应在存在有效上下文时保留 Trace ID、Span ID，并为跨业务阶段的查询保留必要业务关联；字段的保留范围需结合数据访问要求选择。

Correlation ID 是泛指“把多条记录关联起来”的应用约定，并非所有系统统一的第四种 ID；采用哪个字段、何时生成、跨重试是否复用，都需要明确契约。

## 指标标签的基数为何有成本

基数在这里指某个标签或标签组合可能出现的不同取值数量。一个 HTTP 延迟指标若按方法、路由模板和状态类别聚合，维度通常可控；若再把每次请求的唯一 ID 放进去，就会随请求持续产生新的时间序列。

教学估算：4 个方法、50 个路由模板、5 个结果类别，最多可产生 1,000 个组合；再乘 100 个实例维度，理论组合变为 100,000。并非每个组合都会出现，Histogram 桶等还会增加实际存储序列数，因此这不是后端容量测量。它用于说明维度相乘的增长方式。

[Prometheus 文档](https://prometheus.io/docs/practices/instrumentation/#do-not-overuse-labels)指出每组标签都会带来资源开销。请求 ID、Trace ID 和不受限的完整 URL 通常更适合放入日志或链路明细，不应直接作为通用指标标签。`/orders/{id}` 这样的路由模板也比带具体对象 ID 的路径更适合稳定聚合。具体容量上限应测量自己的采集、存储和查询系统，不能照抄一个普适阈值。

## 采样会改变能看见的证据

链路明细量大，采样用于控制成本。头部采样在链路较早阶段决策，通常不能预知最终是否失败；尾部采样在收集部分或完整链路后按错误、延迟等条件决定保留，需要缓冲、汇聚与超时等机制。[OpenTelemetry 的采样说明](https://opentelemetry.io/docs/concepts/sampling/)讨论了两者的适用条件。

尾部采样也无法恢复上游根本没记录或已丢弃的片段，链路过晚到达、传播失败、导出拥塞与保留期到期都可能造成缺失。因此“没搜到这条 Trace”不能证明请求没发生；“保留的 Trace 里错误比例很高”也不能直接作为总体错误率。

[服务目标](../../glossary/reliability.md#reliability.slos)的分母应来自覆盖范围明确的测量，例如入口处符合定义的请求计数，而不是把偏向保留错误的链路样本当成全量请求。还需明确超时、取消、业务失败和 HTTP 状态怎样计数；HTTP 200 不一定意味着业务操作成功。目标定义见 [SLI、SLO 与错误预算](slis-slos-and-error-budgets.md)。

## 一次变慢的证据连接顺序

教学设定：订单查询的尾延迟上升，没有假定真实故障结果。

1. 用指标限定时间窗口、版本、路由及受影响比例，检查请求量、排队量与延迟分布是否一起变化。
2. 查找同窗口的代表性链路，确认测量是否覆盖连接池等待、数据库执行与响应处理，再定位异常阶段。
3. 通过上下文找到对应日志，核对超时、重试和业务分支；若怀疑查询执行，再检查代表性参数与数据库计划。
4. 提出能被推翻的假设，在相同边界下对照正常请求或受控验证；记录传播缺口、采样规则与未观测部分。

以下为合成的结构化事件示意，字段名仅是教学约定，不是特定 SDK 的完整配置，也不是真实故障日志。

```json
{
  "event": "db_pool_wait_finished",
  "service": "orders",
  "route": "/orders/{id}",
  "trace_id": "11111111111111111111111111111111",
  "span_id": "2222222222222222",
  "wait_ms": 80,
  "outcome": "acquired"
}
```

这条事件最多说明某次获得连接前的等待，不能证明 SQL 执行很慢。若 Span 从拿到连接之后才开始，而接口很慢、SQL Span 很短，优先核对未覆盖的等待，避免仅因为数据库出现在链路上就归因于它。

跨机器的墙上时间还可能有偏差。关联时结合 Trace 关系、片段边界与各端测得的持续时间，不能仅按日志时间戳先后推导精确因果。

信号如何支持协调、时间线与业务恢复验收，见[事故响应与复盘](incident-response-recovery-and-postmortems.md)；告警恢复并不覆盖所有业务遗留。

## 自检、实现边界与关联阅读

- [Evals 与失败分析](../ai/evals-and-failure-analysis.md)：把阶段证据、系统版本和评价样本关联起来。

试着解释三个反例：每条日志都有随机 ID，为何仍串不起跨服务调用？只保留慢请求的链路，为何不能直接算 SLO？SQL Span 很短，为何数据库连接池仍可能造成接口等待？

OpenTelemetry 提供采集、处理与导出所需的规范和组件；实际还需配置仪表化、上下文传播、传输与存储查询。SDK、Collector 与后端各自承担不同环节，不会自动给出业务成功定义或根因结论。本文核查日期为 2026-10-19，仅核查机制来源；没有部署采集管道、运行 SDK 或验证生产开销。

- [SLI、SLO 与错误预算](slis-slos-and-error-budgets.md)：先定义用户结果及分母，再设计测量。
- [慢 API 排查](../performance/slow-api-investigation.md)：把总体耗时拆成可以验证的等待与执行假设。
- [索引与执行计划](../database/indexes-and-query-plans.md)：继续核查数据库执行阶段的证据。

主要来源已链接至对应段落：OpenTelemetry 的 Signals、Context propagation、采样说明，以及 Prometheus Instrumentation。
