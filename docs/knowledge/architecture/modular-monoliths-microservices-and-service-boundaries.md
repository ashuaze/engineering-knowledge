---
id: "kb-architecture-deployment-boundaries"
title: "模块化单体与微服务：代码边界为什么不等于部署边界"
kind: "concept"
domain: "architecture"
status: "evolving"
summary: "区分业务模型、代码、数据与部署边界，解释模块化单体与独立服务的收益、部分失败及演进成本。"
created: "2026-10-26"
updated: "2026-10-26"
last_verified: "2026-10-26"
verification: "source-checked"
prerequisites: ["kb-architecture-module-boundaries", "kb-architecture-aggregates-invariants"]
related: ["kb-architecture-strangler-migration", "kb-architecture-quality-decisions", "kb-messaging-outbox", "kb-engineering-contract-compatibility", "kb-distributed-transactions-sagas"]
tags: ["modular-monolith", "microservices", "boundaries", "deployment", "ownership"]
---

# 模块化单体与微服务：代码边界为什么不等于部署边界

学习入口：把订单和库存放到两个[进程](../../glossary/systems.md#systems.execution-units)，为什么仍要一起发布？把它们放回同一部署包，又是否必然变成难以维护的大系统？先区分模型、源码、数据和运行部署分别在哪条边界上独立。

前置：[模块边界与依赖](module-boundaries-and-dependencies.md)、[聚合与业务不变量](domain-models-aggregates-and-invariants.md)。本文讨论架构风格与演进条件，不给出固定服务数量、团队人数或流量门槛。订单、库存和故障时序为纸面设计；没有拆分项目、部署服务或测量维护与性能收益。

## 四类边界可以重合，也可以不同

| 边界 | 核心问题 | 单独划开仍不能证明 |
| --- | --- | --- |
| 业务模型 | 哪套语言、规则和不变量在这里成立 | 每个[限界上下文](../../glossary/architecture.md#architecture.ddd)必须单独部署 |
| 代码模块 | 哪些实现细节隐藏，允许哪些依赖 | 进程与数据库已隔离 |
| [数据所有权](../../glossary/architecture.md#architecture.domain-model) | 谁能解释、修改并守住某份状态 | 必须一服务一台物理数据库服务器 |
| 部署与运行 | 哪些部分可以独立发布、扩缩和恢复 | 所有变更与故障都不会互相影响 |

[Bounded Context](https://martinfowler.com/bliki/BoundedContext.html)解释模型与语言的适用范围。一个上下文可以由多个运行组件协作实现；多个上下文也可以在一个部署单元中保持清楚的接口。边界映射是设计决定，不能从名词直接推出拓扑。

## 模块化单体保留本地协作，也需要约束

[模块化单体](../../glossary/architecture.md#architecture.modular-monolith)在同一部署单元内组织职责与接口。调用通常可在进程内进行，跨模块流程也可能使用同一[数据库事务](../../glossary/database.md#database.isolation)；是否确实共同提交，要看实际连接、存储和事务范围，而非同一进程这一事实。

它需要可执行的访问规则：模块公开什么、禁止谁读取内部表或类、跨模块修改通过什么能力进行、如何发现[循环依赖](../algorithms/graphs-traversal-and-dependency-order.md)。共享一个数据库可以保留逻辑所有权，前提是调用方不能任意绕过模块规则；拆目录和加一个 interface 都不足以阻止内部结构泄漏。

整个应用作为一个发布单元有发布和资源上的共同约束。可用多个副本提高整体容量，但无法仅因模块目录分开，就独立部署其中一段代码。相应选择与成本见 [Monolith First](https://martinfowler.com/bliki/MonolithFirst.html)；其经验观察不是所有项目都必须先做单体的定理。

## 微服务的价值来自可独立演进的业务能力

[微服务](../../glossary/architecture.md#architecture.microservices)以业务能力和运行边界组织协作。Lewis 与 Fowler 的 [Microservices](https://martinfowler.com/articles/microservices.html)将独立部署、业务能力与运行治理作为重要特征。服务边界把部分调用变成进程外协议，可能使独立发布、定向扩缩和隔离成为现实；这些收益仍依赖边界、契约兼容与基础设施。

若订单发布必须等待库存升级，库存升级又必须等待共享 SDK 和所有数据库调用方同步发布，即使已有多个容器，也还没有获得这些变更上的独立性。不同进程也可能共享故障数据库、线程池上游或容量瓶颈，不能把“有网络边界”当成完整故障隔离。

独立服务会增加名称解析、连接、超时、身份、观测和版本兼容等责任。[Microservice Prerequisites](https://martinfowler.com/bliki/MicroservicePrerequisites.html)讨论自动部署、监控等基础能力；本文不沿用该历史文章中的具体时长作为当前组织门槛。

## 纸面拆分：函数调用变成不确定结果

假设单体中订单与库存的最终修改原本由同一个数据库事务原子提交。拆分后，库存服务有自己的事务，订单服务通过请求预留库存：

1. 订单发出预留请求，库存提交成功。
2. 响应在返回途中丢失，订单只观察到等待超时。
3. 订单无法由超时判断库存一定没改；使用新操作 ID 重新预留可能重复占用。
4. 订单自身的提交、库存预留以及后续释放，还需要业务流程与恢复规则协调。

“两边各自用了事务”不恢复原来的共同提交边界；发布一个事件也不能自动覆盖数据库提交与事件派送之间的故障窗口。可按需求研究 [Outbox](../messaging/transactional-outbox.md)或[跨边界事务与补偿](../distributed/two-phase-commit-sagas-and-recovery.md)，并明确它们各自提供什么保证。

这里并未证明单体一定正确：原事务也要真正覆盖不变量并正确处理并发。比较方案时应把原来成立的保证写出来，再说明哪些保留、哪些被异步流程或补偿替代。

## 先找独立变化，再决定是否拆出

教学判断：商品目录读流量大、变化节奏独立，而且允许短暂陈旧，可成为候选；订单与价格规则经常一同改变、需要紧密协同，则应先研究接口和规则所有权。它们是需验证的线索，不能仅按流量或表名机械拆分。

可比较相同业务变更下的影响范围、契约演进、故障恢复和运行成本。记录观察窗口、谁承担运维、哪些依赖仍共同发布；一次成功的服务启动不能证明收益。若尚不能说明独立演进的价值，保持清楚模块并逐步积累证据也可能合理。

迁移无需把整个系统一次切成目标拓扑，见[渐进替换](strangler-fig-migration-write-authority-and-rollback.md)。最终选择与重评条件应写入[架构决策](quality-attribute-scenarios-tradeoffs-and-adrs.md)。

## 自检

1. 限界上下文、模块、数据所有权和部署单元分别描述什么？为何不必一一对应？
2. 同一进程或同一数据库服务器，能否单独证明跨模块修改原子提交？
3. 两个服务必须一起发布，独立部署的目标在哪一类变更上尚未实现？
4. 库存提交后响应丢失，订单超时为什么不能证明预留失败？
5. 决定拆出商品目录前，除流量外还应验证哪些变化和运行条件？

## 来源与核查

2026-10-26 核查 Fowler/Lewis 的 Microservices、Monolith First、Bounded Context 与 Microservice Prerequisites 原文，分别用于风格特征、模型边界和历史经验。本文为 source-checked 概念文章；交易时序为教学推演，未实施服务拆分、共同发布分析、故障隔离或容量/维护效果对照。
