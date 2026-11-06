---
id: "kb-architecture-quality-decisions"
title: "质量属性与架构决策：怎样把取舍变成可验证的约束"
kind: "concept"
domain: "architecture"
status: "evolving"
summary: "把性能、可用性与可修改性写成质量属性场景，区分敏感点、权衡、风险、证据与 ADR 的决定状态。"
created: "2026-10-26"
updated: "2026-10-27"
last_verified: "2026-10-26"
verification: "source-checked"
prerequisites: ["kb-architecture-module-boundaries"]
related: ["kb-architecture-knowledge-adr", "kb-architecture-deployment-boundaries", "kb-architecture-strangler-migration", "kb-performance-benchmarking", "kb-reliability-slos", "kb-reliability-fault-domains-recovery", "kb-engineering-design-documents", "kb-engineering-specification-traceability"]
tags: ["quality-attributes", "scenarios", "tradeoffs", "adr", "evidence"]
---

# 质量属性与架构决策：怎样把取舍变成可验证的约束

学习入口：评审会上大家都希望系统高性能、可扩展、易维护，为什么仍选不出方案？这些词只有连接到具体使用与变化场景，才能比较代价并定义后续证据。

前置：[模块边界](module-boundaries-and-dependencies.md)。本文借鉴 CMU 架构教学、SEI ATAM 的部分分析概念与 Nygard 的 [ADR](../../glossary/architecture.md#architecture.adr) 方法，不声称完成一次正式 ATAM。系统、时长、负载和阈值均为纸面教学输入；没有对真实项目评估、压测或作出生产架构批准。

质量决定如何连接讨论、当前说明与实施证据，见[设计文档与决策记录](../engineering/design-docs-rfcs-adrs-and-decision-lifecycles.md)；目标和实现如何追溯验收，见[规格驱动与验收追溯](../engineering/specifications-contracts-traceability-and-acceptance.md)。

## 功能说明做什么，质量场景补充在何种条件下做到

“查询商品”描述能力，“高性能”仍缺少负载、数据与时间口径。“易修改”也应说明谁改什么、允许触及哪些边界和如何衡量结果。[质量属性](../../glossary/architecture.md#architecture.quality-scenario)包括性能、可用性、安全、可修改性等；它们会影响模块、运行与部署决策，不能由一张结构图自动证明。

CMU 的[架构课程资料，第 8 页](https://www.cs.cmu.edu/~schmerl/courses/15-413/02-software-architecture.pdf#page=8)用刺激源、刺激、环境、受影响对象、响应、响应度量六部分描述质量属性场景。下面是自拟的查询场景：

| 要素 | 本例的教学定义 |
| --- | --- |
| 刺激源 | 已通过身份验证、具备查询权限的 API 调用方 |
| 刺激 | 按固定请求分布持续发送每秒 200 次有效商品查询 |
| 环境 | 常态运行、缓存已预热、100 万条商品记录、固定部署/资源配置与网络条件，连续观察 15 分钟 |
| 受影响对象 | 商品查询 API 及其实际依赖路径 |
| 响应 | 返回契约内且符合当前权限与新鲜度要求的查询结果 |
| 响应度量 | 成功请求的端到端 [p95](../../glossary/performance.md#performance.percentiles) ≤ 250 ms，同时全部有效请求中的超时/服务错误等失败比例 ≤ 0.1% |

本例用于说明六部分怎样对齐。执行前仍要把“固定配置”、请求分布、失败分类、新鲜度口径与采集边界落实为可复现记录；没有这些记录不能宣称通过。只统计成功请求的[延迟](../../glossary/performance.md#performance.latency-throughput)时，必须同时报告失败，避免靠拒绝或超时丢掉慢请求后获得好看的百分位。

可修改性也可以写成教学场景：在已明确能力契约内增加一种通知渠道，生产代码修改限于适配模块与组装处。假设由一名熟悉当前代码与工具的开发者完成，目标工作量不超过 2 人日（每人日 8 小时，含实现、测试与评审修改，外部等待另记），约定的回归和契约检查全部通过且没有契约外行为改变；测试与文档修改另列范围。这个阈值是教学设定，实际技能、工具与工作记录仍需核对。这是一个待检验目标；遇到新的业务语义时，不应为了维持“只改两处”而隐瞒必要的核心变化。

## 方案比较要围绕同一组场景

| 教学方案 | 可能帮助的目标 | 新增约束或需验证的成本 |
| --- | --- | --- |
| 保持[模块化单体](../../glossary/architecture.md#architecture.modular-monolith) | 本地协作、较少部署协调、某些共同事务 | 独立扩缩、共同发布与资源故障范围 |
| 拆出独立服务 | 按业务能力独立发布或扩缩 | 网络等待、部分失败、版本与数据协调 |
| 增加读缓存 | 降低部分查询成本、吸收重复读取 | 内容年龄、失效与权限变化，及故障时回源压力 |

表中都是要验证的假设。若主要问题是修改传播，而瓶颈并不在查询成本，增加缓存可能无助于核心目标；若强制要求立即撤销可见权限，也不能用允许旧值的缓存策略不加限制地代替实时校验。

还要写出业务优先级和不可放松的约束。主观打分可以帮助组织讨论，但不能让“易维护 5 分”变成已测量事实，也不能用多个优点相加抵消一个明确禁止的行为。

## 敏感点、权衡点与风险有不同含义

SEI [ATAM 报告 §7.2–7.3](https://sei.cmu.edu/documents/629/2000_005_001_13706.pdf)把关键质量响应对架构参数的依赖作为分析对象。某个参数对一个重要质量目标影响显著，是需要关注的敏感点；同一参数影响多个相关质量目标时，可能形成权衡点。发现这些点是进一步分析的入口，不是性能或安全证明。

例如缓存保留时间可能同时影响源站负载与内容年龄；并发上限可能影响吞吐、等待和依赖压力。是否构成不可接受的风险，要结合给定负载、业务承诺与实现，而非只看到“缓存”或“[限流](../../glossary/api.md#api.limits)”便判定好坏。

风险应写成可追踪的条件和后果，例如“实例 A 更新权限，而实例 B 的旧缓存仍能返回已撤销对象”。对应的行动可以是细化传播约定、原型验证、故障演练或修改方案。尚未知晓的数据应标为未知，不能靠增加图中的箭头消除。

## 纸面预算不是分布结论

假设同一次请求在不重叠的四段串行路径中分别花费 30、80、60、40 ms，则总时长为：

```text
30 + 80 + 60 + 40 = 210 ms
与 250 ms 的教学目标相比，该次请求还剩 40 ms 差额。
```

这不证明场景中的 p95 达标。若四个数分别是各组件的 p95，更不能直接相加当作端到端 p95；不同请求、相关性、[排队](../../glossary/performance.md#performance.queueing)与同时推进的路径都会影响分布。模型、预算、单次轨迹和真实负载统计应分开呈现，见[基准与工作负载](../performance/benchmarks-workloads-and-speedup.md)。

测试证据也有适用边界：原型可能没包含身份服务，压测可能没有冷缓存，故障演练可能只覆盖一个实例。应记录环境、假设、结果及缺口，再判断证据是否足以支持决策。

## ADR 保存当时为何这样决定

Nygard 的 [Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)用短记录保留上下文、决定、状态和后果。它帮助未来读者理解约束与理由，而不是只留下“采用某技术”四个字。

一次教学决定可记录：在当前查询/变更场景和团队运行能力下，先保留模块化单体；暂不拆成独立服务；接受共同发布的成本；在独立扩缩或变化节奏的证据出现时重评。还应写出真正比较过的备选、未解决风险、后续验证和负责人。

`proposed`、`accepted` 或被后续决定替代描述的是决定状态；它们不等于“已实现”或“已验证”。修改决定时保留替代关系与历史，避免用今天的结论覆盖昨天的上下文。知识库自己的[ADR-0001](knowledge-base-adr.md)是具体决策记录，阅读它不等于所有项目都应采用同一内容架构。

可自动检查的依赖规则、[契约测试](../../glossary/engineering.md#engineering.contracts)与运行指标，可以持续提示实现是否偏离决定；通过这些局部检查仍不能证明系统满足全部质量属性。应在业务、负载或依赖变化时重新检查原假设。

## 自检

1. 六部分质量属性场景怎样补足“高性能”？教学表执行前还缺哪些具体记录？
2. 为什么统计成功请求 p95 时还要报告失败？给慢请求返回错误是否能算性能改善？
3. 缓存保留时间为何可能成为敏感点和权衡点？它何时成为风险？
4. 四段 30/80/60/40 ms 得到什么结论？若它们分别是 p95，能否直接相加？
5. ADR accepted 为什么不等于实现和验证完成？何时应保留历史并重评？

## 来源与核查

2026-10-26 核查 CMU 架构课程中的场景要素、SEI ATAM 报告上述章节及 Nygard ADR 原文。本文为 source-checked 概念文章；未执行正式 ATAM、性能/维护评估、故障演练或生产决策流程，例中场景和方案为教学设计，不能当作本仓库或任一系统的达标证据。
