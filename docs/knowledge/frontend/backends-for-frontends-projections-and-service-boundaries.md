---
id: "kb-frontend-bff"
title: "BFF 与前端适配：聚合成一次请求，为什么仍需业务边界"
kind: "concept"
domain: "frontend"
status: "evolving"
summary: "区分面向客户端的投影、通用网关与领域规则，说明聚合等待、部分结果、权限和个性化缓存的边界。"
created: "2026-10-27"
updated: "2026-10-27"
last_verified: "2026-10-27"
verification: "source-checked"
prerequisites: ["kb-api-styles-gateway", "kb-security-object-authorization"]
related: ["kb-frontend-routing-cache", "kb-architecture-module-boundaries", "kb-api-resource-validation", "kb-reliability-retry-budgets"]
tags: ["bff", "aggregation", "frontend-contract", "authorization"]
---

# BFF 与前端适配：聚合成一次请求，为什么仍需业务边界

学习入口：移动端把订单、物流和推荐合成一个接口，为什么还会出现越权、等待放大和数据不一致？面向界面的组合改变了交互方式，各下游的业务规则和提交边界仍需明确。

前置：[API 风格与网关](../api/api-styles-contracts-and-gateway-boundaries.md)、[对象级授权](../security/object-level-authorization.md)。本文参考 Newman 与 Azure 模式说明，接口与时长为纸面设计；没有部署[BFF](../../glossary/frontend.md#frontend.bff)、发送请求或测量页面性能。

## 适配层围绕某类客户端的需要组织

[Sam Newman 的 BFF 模式](https://samnewman.io/patterns/architectural/bff/)讨论面向特定界面的边缘服务。移动端和桌面端可能需要不同字段、交互顺序和负载形态；BFF提供适合某类客户端的契约，并可由相应团队维护。

它不要求每张页面或每个设备都新增一个服务。若客户端需求相近，一个共同后端也可能足够；分离需要权衡演进自主性、重复代码和运行成本，见[Azure BFF](https://learn.microsoft.com/en-us/azure/architecture/patterns/backends-for-frontends)。

## 投影、通用策略与业务规则分工

| 职责 | 适合解释的问题 | 仍需保留的边界 |
| --- | --- | --- |
| BFF | 该客户端需要哪些字段、怎样组合及呈现部分结果 | 不能任意改写领域规则 |
| 网关/入口 | 路由、协议接入、通用流量与身份策略 | 不自动完成每个对象的业务[授权](../../glossary/security.md#security.identity) |
| 领域服务 | 合法状态转换、价格、库存及提交 | 不能因调用方来自BFF就信任任意字段 |

部署位置或使用[GraphQL](../../glossary/api.md#api.styles)并不能单独决定某层就是BFF。关键是它服务谁、拥有什么契约和变化责任；领域不变量不应在多个客户端适配器中各复制一份不同实现。

## 聚合减少外部交互，也增加组合责任

教学例只统计BFF下游等待与组合编码，未单列客户端网络等耗时：订单、物流、推荐调用分别耗时90/80/70ms，组合与编码20ms。假定三项独立、可以同时启动、无额外[排队](../../glossary/performance.md#performance.queueing)和资源限制：串行为260ms；理想[并行](../../glossary/systems.md#systems.concurrency)组合约为 `max(90,80,70)+20=110ms`。

这是单次请求的简化时长，不能把三个组件的[p95](../../glossary/performance.md#performance.percentiles)取最大值当作端到端p95，也不证明实际BFF变快。依赖参数、连接上限、扇出和重试都可能改变等待，聚合还可能将一个慢依赖放大为整页失败。

[Azure Gateway Aggregation](https://learn.microsoft.com/en-us/azure/architecture/patterns/gateway-aggregation)讨论合并请求、故障和监控等责任。应共享总预算，区分必需数据与可选数据；取消本地等待也不能自动撤销远端已提交动作。

## 部分成功需要可被客户端理解

订单可用但推荐失败时，可以按约定返回部分结果；应明确缺失、旧值、无权限和业务上为空的区别。不能把支付状态未知写成“未付款”，也不能用空[数组](../../glossary/algorithms.md#algorithms.sequences)悄悄掩盖关键依赖故障。

多个独立读取可能来自不同时间点，组合成一个JSON不自动形成一致快照。若页面需要某个业务版本或严格状态关系，须由相应服务/数据协议提供，不能靠BFF最后一次拼接来补出事务保证。

## 身份传播与缓存键必须贯穿组合

按可信主体、租户和对象分别验证字段；不要把前端给出的用户ID直接当作授权事实。BFF登录检查和下游对象权限可以共同工作，但各自的责任和可信上下文应明确。

个性化结果缓存还需包含必要的身份、权限、新鲜度和语言等变化维度，或采用适当的私有/不缓存策略。缓存命中不能绕过当前访问约束；增加聚合层也增加了一条失效与撤权传播路径。

## 自检

1. BFF、通用网关和领域服务各自主要负责什么？
2. 为什么不必为每张页面或设备创建独立BFF？
3. 90/80/70/20ms例子的260与110ms依赖哪些条件？
4. 部分结果与一致快照有什么区别？
5. 个性化聚合为什么需要同时检查权限传播与缓存范围？

## 来源与核查

2026-10-27 核查 Newman BFF原文、Azure BFF与Gateway Aggregation。本文为source-checked；未运行聚合、权限/缓存对照、故障恢复或性能基准，具体产品配置及实现收益仍待验证。
