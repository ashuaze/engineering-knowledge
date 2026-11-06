---
id: "kb-architecture-aggregates-invariants"
title: "领域模型、聚合与业务不变量：规则究竟由谁守住"
kind: "concept"
domain: "architecture"
status: "evolving"
summary: "区分实体身份、值语义、聚合一致性边界与限界上下文，解释数据所有权、并发写入及跨边界流程的验证责任。"
created: "2026-10-20"
updated: "2026-10-26"
last_verified: "2026-10-20"
verification: "source-checked"
prerequisites: ["kb-architecture-module-boundaries", "kb-database-isolation-mvcc"]
related: ["kb-database-concurrent-inventory", "kb-messaging-outbox", "kb-api-conditional-requests", "kb-engineering-contract-compatibility", "kb-engineering-property-state-models", "kb-database-models-access-patterns", "kb-architecture-cqrs", "kb-architecture-event-sourcing", "kb-architecture-deployment-boundaries", "kb-architecture-strangler-migration"]
tags: ["domain-model", "aggregate", "invariant", "ownership"]
---

# 领域模型、聚合与业务不变量：规则究竟由谁守住

学习入口：接口、后台任务和[批处理](../../glossary/performance.md#performance.batching)都能改订单，怎样保证它们遵守同一条业务规则？前置：[模块边界](module-boundaries-and-dependencies.md)与[事务隔离](../database/isolation-and-mvcc.md)。本文用订单模型解释 [DDD](../../glossary/architecture.md#architecture.ddd) 的部分战术概念，不要求所有系统采用同一种组织方式；订单规则和流程是教学设计，没有实施项目[重构](../../glossary/architecture.md#architecture.debt)。

模型与部署边界的映射继续见[模块化单体与微服务](modular-monoliths-microservices-and-service-boundaries.md)；迁移时模型翻译、数据连续性与写入归属见[渐进替换](strangler-fig-migration-write-authority-and-rollback.md)。

## 模型先表达业务含义，再选择代码结构

领域模型组织业务中的概念、状态与规则，帮助回答某项行为是否允许，以及结果应满足什么约束。相同字段可以在不同限界上下文中具有不同含义，例如交易中的客户与配送中的收件人，不必共享一份能被所有模块任意修改的对象。模型适用范围见 [Microsoft 领域分析](https://learn.microsoft.com/en-us/azure/architecture/microservices/model/domain-analysis)。

[业务不变量](../../glossary/architecture.md#architecture.domain-model)指在声明的边界和时机必须成立的规则。它需要交代作用范围、允许的中间状态和生效时刻：草稿暂时没有商品，与提交完成后仍没有商品，是不同判断。不能只写“订单永远有效”却没有可执行的含义。

本文教学规则限定为：订单只有草稿才能改明细；提交时至少有一条明细，数量为正，金额按约定整数单位计算且币种一致。折扣、退款、支付与履约规则不在本例中；这些规则不能直接套用到所有交易系统。

## 实体看连续身份，值对象看值语义

| 概念 | 教学对象 | 判断方式与责任 |
| --- | --- | --- |
| Entity，实体 | 订单 | 明细变化后仍是同一订单，用业务中稳定的身份关联生命周期 |
| Value Object，值对象 | 金额、地址快照 | 按所建模的属性值判断相等，明确单位、币种或规范化规则 |
| Aggregate，聚合 | 订单与需共同维护规则的明细 | 把相关状态作为一致性单元，由明确入口控制修改 |
| Aggregate Root，聚合根 | 本例中的订单 | 对外提供行为，维护聚合内部[不变量](../../glossary/systems.md#systems.atomicity) |

实体与值对象的区分不由“有没有数据库主键”决定。存储可以为一份地址分配技术 ID，但领域里仍可能把它当作一个值；同样数值的 100 分人民币和 100 美分也不是相等金额。值语义及不可变实现的讨论见 [Martin Fowler：Value Object](https://martinfowler.com/bliki/ValueObject.html)。

值对象常采用不可变设计，改变时创建新值，减少共享引用被意外修改的问题；这不替代有效值构造、相等规则和[序列化](../../glossary/runtime.md#runtime.serialization)约定。把字段包进一个类，并不会自动落实这些含义。

## 聚合边界按一致性需要划分

聚合把一组相关领域对象视为一个单元，由根或明确机制维护整体规则。外部修改通过根的行为进入，避免调用方绕过约束直接改变内部明细。[Eric Evans 的 DDD Reference](https://www.domainlanguage.com/wp-content/uploads/2016/05/DDD_Reference_2015-03.pdf#page=23)讨论了聚合、不变量与一致性边界；[Fowler 的聚合说明](https://martinfowler.com/bliki/DDD_Aggregate.html)也用订单和明细说明这一模型。

教学设计可以提供这些行为，而不暴露任意改字段的接口：

```text
Order.add_line(product, quantity, price)
  检查仍为草稿、数量为正、币种与金额单位符合本例契约
Order.change_quantity(line_id, quantity)
  维护明细及订单内部的有效状态
Order.submit()
  检查至少一条明细，建立提交后的状态
```

这是行为草图，没有执行代码。它把“怎样才算合法”放到明确入口，但仍须限制可变内部对象的泄漏，并让批处理、管理入口和其他写入路径遵守同样规则。只给一个类起名 AggregateRoot，不能防止其他路径直接改数据库。

聚合大小需要取舍。把全部客户、历史订单和所有库存都装进一个根，会让无关操作争用一个边界；拆得过细，又可能使必须共同成立的规则失去维护者。小聚合与跨聚合协作的设计依据见 [Microsoft Tactical DDD](https://learn.microsoft.com/en-us/azure/architecture/microservices/model/tactical-domain-driven-design)。边界应由具体不变量和竞争成本解释。

## 对象检查之后，还要守住持久化的并发边界

两个请求分别加载同一个草稿副本，在内存里都通过检查，随后写回时仍可能相互覆盖。对象方法只约束它看见的状态；真正提交时还需要事务、[并发](../../glossary/systems.md#systems.concurrency)版本或其他适合的数据约束，并正确处理冲突。

教学情形：甲提交订单，乙仍基于旧草稿修改明细。若存储无条件接受乙的旧状态，就可能把已提交订单写回草稿或改掉提交内容。应把预期版本与修改放到同一原子边界检查；冲突后重新读取并重新判断，不能只覆盖[重试](../../glossary/api.md#api.retries)。HTTP 层的表达见[条件请求](../api/conditional-requests-and-cache-validation.md)，数据库范围见[隔离与 MVCC](../database/isolation-and-mvcc.md)。

数据约束可以防住其表达范围内的非法值；跨行或跨对象规则还需专门设计。已有[库存并发](../database/concurrent-inventory.md)展示了“两个事务都提交”仍可能违反业务含义的窗口。聚合模型、数据库约束和并发协议应共同落实承诺，不把其中任何一层视为全部证明。

## 数据所有权与部署边界分开判断

数据所有权说明哪个模型和写入路径负责解释、校验并改变权威状态。其他模块可以持有必要标识、读取约定快照或建立查询投影，但投影更新滞后时，不能自动成为权威写入依据。只读查询可以跨模型组合；是否允许修改以及由谁确认规则，是另一个问题。

[CQRS](cqrs-read-write-models-and-projection-lag.md)可以让聚合写模型与查询投影采用不同表示；[事件溯源](event-sourcing-streams-snapshots-and-projections.md)可以把聚合变化保存为按预期版本追加的[事件流](../../glossary/messaging.md#messaging.models)。两种选择都不会自动确定聚合边界，也不放宽提交时的不变量。

限界上下文约束模型含义，聚合约束局部一致性，模块约束代码依赖，服务约束运行和部署。一个上下文可以包含多个聚合，一个部署单元也可以包含多个上下文；不能从“一张表”“一个 [REST](../../glossary/api.md#api.styles) 资源”或“一次网络调用”机械推出聚合大小。

库存与订单若属于不同维护者，需要说明跨边界业务流程：例如先建立待确认订单，再申请库存预留，成功才确认，失败则拒绝或释放已经取得的资源。等待、超时、重复消息和补偿都应有可见状态与责任；释放或补偿自身也可能失败，需要明确重试、对账和无法自动收敛时的处理责任。事件名称或“最终一致”不会自动补齐这些步骤。[Outbox](../messaging/transactional-outbox.md)可处理本地状态与待发事件的提交窗口，但不保证外部消费者的全部业务结果。

如果需求要求两个边界之间立即原子成立，就需要重审划分或明确事务/协调方案；不能通过拆分类或发送事件消除这条要求。本文不规定所有[数据库事务](../../glossary/database.md#database.isolation)只能覆盖一个聚合，也不提供已验证的跨服务协调实现。

业务事实、数据依赖与持久化表示的取舍继续见[数据模型与访问模式](../database/data-models-and-access-patterns.md)；聚合规则、表结构、访问路径与分布位置需要分别判断。

## 从规则写出可验证的设计依据

| 教学问题 | 需要留下什么 |
| --- | --- |
| 谁可改变订单明细 | 可信入口、[授权](../../glossary/security.md#security.identity)与所有写入路径清单 |
| 提交与修改并发时谁成功 | 原子提交条件、冲突处理和允许的状态变化 |
| 库存迟迟没有结果 | 待确认状态、期限、重试及资源归还责任 |
| 一个字段出现在多个上下文 | 各自语义、权威来源与同步契约 |

业务权限仍须独立检查，聚合根并不证明调用者有权修改。验证行为可以从固定反例开始，再用[属性测试与状态模型](../engineering/property-testing-and-state-models.md)生成更多命令组合；跨组件输入输出则由[契约测试](../engineering/contract-testing-and-compatibility.md)补充。

自检：哪些规则在提交时必须成立？哪些中间状态允许存在？哪些写入者能绕过根？一次对象测试能否说明数据库并发与外部库存也正确？为边界写出这些答案，比先给每张表建立一个聚合类更有依据。

2026-10-20 核查 Evans、Fowler 与 Microsoft 的领域建模资料，状态为 source-checked。订单模型、方法与流程为教学设计；未运行 ORM、聚合持久化、并发冲突或跨聚合协调实验，未把已有库存实验扩展为这些设计的实测证据。
