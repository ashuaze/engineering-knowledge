---
id: "kb-api-admission-controls"
title: "限流、并发限制与配额：分别在限制什么"
kind: "concept"
domain: "api"
status: "evolving"
summary: "区分接纳速率、同时占用与累计用量，解释突发、身份、分布式计数及拒绝重试的契约。"
created: "2026-10-19"
updated: "2026-10-22"
last_verified: "2026-10-19"
verification: "source-checked"
prerequisites: ["kb-performance-latency-queues"]
related: ["kb-performance-backpressure", "kb-performance-overload-lab", "kb-reliability-failure-isolation", "kb-api-contracts-pagination", "kb-api-idempotency", "kb-reliability-retry-budgets", "kb-api-styles-gateway"]
tags: ["rate-limit", "concurrency", "quota", "admission-control"]
---

# 限流、并发限制与配额：分别在限制什么

学习入口：接口已经限制每秒请求数，为什么下游一变慢，[连接池](../../glossary/api.md#api.pool)还是被占满？前置：请求身份、持续时间与接纳边界。本文是来源核查与教学设计；没有部署分布式[限流](../../glossary/api.md#api.limits)器或计费系统。

## 三个维度不能互相替代

| 控制 | 计量对象 | 教学配置 | 不能单独保证 |
| --- | --- | --- | --- |
| 速率限制 | 某规则下单位时间的尝试或接纳量 | 每秒补充 20 个令牌 | 长请求的同时占用不超限 |
| [并发](../../glossary/systems.md#systems.concurrency)限制 | 指定边界内尚未释放的工作数 | 同时占用最多 4 个执行槽 | 限制之外没有等待者；每秒总用量固定 |
| 用量配额 | 约定周期累计的请求、字节或成本单位 | 每日 10,000 个成本单位 | 短时突发受到保护 |

工程术语中 quota 有时也泛指速率或并发上限；本文特指累计用量。[接口契约](../../glossary/api.md#api.contracts)应写清单位、周期、身份、作用范围和计数时刻，不能只写一个“额度”。便宜读取与昂贵生成即使请求数相同，资源成本也可能不同。[Microsoft 的限流模式](https://learn.microsoft.com/en-us/azure/architecture/patterns/rate-limiting-pattern)说明了协调访问受限服务的设计边界。

纸面推演：稳定接纳 20 项/秒，每项平均持有槽位 0.1 秒，平均在途约 2 项；持有时间变成 2 秒时，若仍全部接纳且达到稳定状态，平均在途约 40 项。速率没变，占用已经不同；这不是 [P99](../../glossary/performance.md#performance.percentiles) 或所需[线程](../../glossary/systems.md#systems.execution-units)数的计算。

## 速率算法怎样处理突发

固定窗口按窗口计数，边界两侧可以集中到达两批工作；滑动统计能减少这种边界效应，但需要定义精度和存储成本。令牌桶把补充速率与最大积蓄量分开：令牌充足时允许突发，长期受补充约束。可对照 [ASP.NET Core 10 的算法说明](https://learn.microsoft.com/en-us/aspnet/core/performance/rate-limit?view=aspnetcore-10.0#rate-limiter-algorithms)查看固定窗口、分段滑动窗口、令牌桶和并发限制的具体差异；本文不复制其默认参数或声称已部署中间件。

教学例子：桶容量 40、每秒补充 20，初始满桶、每次消耗 1 个，可以立即接纳至多 40 次；不能把它解释为任意一秒都不超过 20 次。实现还要定义初始状态、时间来源、扣费[原子性](../../glossary/systems.md#systems.atomicity)、请求成本和不够时的动作。[RFC 3290 附录 A](https://www.rfc-editor.org/rfc/rfc3290.html#appendix-A)提供网络流量中令牌桶模型；这里借其速率和突发的区分，不将该 RFC 当作 HTTP 限流标准。

漏桶也可能指[排队](../../glossary/performance.md#performance.queueing)整形或按速率判定等不同实现；讨论算法名字时，要落到是否排队、何时释放和满时怎样处理。排队整形应继续受[队列上限和截止时间](../performance/backpressure-and-bounded-queues.md)约束。

## 并发许可应覆盖真正占用的阶段

许可从哪里获取、什么时候释放，决定了保护对象。保护数据库执行，应覆盖实际占用连接与执行的阶段；若只覆盖发起异步调用的函数返回，后台工作可能已逃出限制。客户端停止等待也不能作为远程工作已结束的证据。

先创建任务再等 [Semaphore](../../glossary/systems.md#systems.synchronization) 会产生许可之外的等待。拒绝式准入则在创建工作前预留槽位，满时返回未接纳；仍需付出请求解析与本地调度成本。[过载实验](../performance/overload-control-lab.md)只实测这种本地预留与释放，以及协作取消的边界，没有实测速率算法。

## 身份与分布式计数决定规则是否成立

规则通常需要组合租户、用户、接口、地域和全局资源。[IP](../../glossary/networking.md#networking.transport) 不必然等于用户：共享出口会聚合多人，地址变化也可能绕过限制。来自调用方的租户标识需要先验证；限流通过不替代对象[授权](../../glossary/security.md#security.identity)。

如果三台实例各允许 20 项/秒，聚合接纳可能达到 60 项/秒，不能宣称全局只有 20。共享计数需要处理并发更新、时钟和故障；分配本地份额需要处理空闲浪费、再分配及超发边界。累计配额还需要区分预留、实际消耗、[幂等](../../glossary/api.md#api.idempotency)结算和失败释放。以下是教学决策项，并未实现或验证分布式一致性：计数服务不可用时，是拒绝、放行，还是使用有上限的本地余量？答案应由资源风险和业务目标决定并可观测。

## 拒绝响应也是调用契约

[RFC 6585 第 4 节](https://www.rfc-editor.org/rfc/rfc6585.html#section-4)定义 429 表达一定时间内请求过多，并允许携带 [Retry](../../glossary/api.md#api.retries)-After，但不规定怎样识别用户和计数。[RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html#name-503-service-unavailable)中的 503 可表达暂时过载等服务不可用情形。[状态码](../../glossary/api.md#api.http-semantics)应与接纳层和接口约定一致，不能仅凭某个码推断后台是否已有业务副作用。

Retry-After 可用秒数或 HTTP 日期表达等待提示。调用方应把提示、剩余[截止时间](../../glossary/reliability.md#reliability.retry-budget)、退避与重试预算一起判断；提示不代表稍后必定成功，也不建立写操作的幂等保证。多层立刻重试可能扩大压力，详见[幂等性](idempotency.md)与[重试预算](../reliability/timeouts-and-retry-budgets.md)。

入口额度与执行服务实际成本需要分别约定。不同调用/查询契约以及网关对预算、重试和业务执行的责任，继续见[API 风格与网关](api-styles-contracts-and-gateway-boundaries.md)。

## 怎样检验一个接纳规则

分别测试窗口边界、突发、长请求、多个身份、多实例、计数故障和重试。记录拒绝原因，区分速率耗尽、并发占满和累计额度耗尽；同时观察已完成业务量与排队时间。只看“返回得很快”不能证明[服务目标](../../glossary/reliability.md#reliability.slos)达到。

自检：每日额度尚有 90%，能否接纳一次会占用所有连接的突发？解释为什么累计余量、速率和同时占用需要分别判断，再给出等待上限和失败响应。

核查日期：2026-10-19。HTTP 语义和令牌桶模型依据所链一手资料；数字、配额决策项与分布式故障问题为教学综合，不是已执行的限流系统。
