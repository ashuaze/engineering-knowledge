---
id: "kb-architecture-event-sourcing"
title: "事件溯源：事件流怎样成为事实，快照与投影怎样安全重建"
kind: "concept"
domain: "architecture"
status: "evolving"
summary: "解释权威事件流、预期版本追加、状态重建、快照、投影和历史演进，并区分事件存储、Broker、Outbox 与审计日志。"
created: "2026-10-23"
updated: "2026-10-23"
last_verified: "2026-10-23"
verification: "source-checked"
prerequisites: ["kb-architecture-aggregates-invariants", "kb-messaging-event-evolution"]
related: ["kb-architecture-cqrs", "kb-messaging-outbox", "kb-messaging-partitions-offsets", "kb-database-cdc", "kb-distributed-logical-clocks"]
tags: ["event-sourcing", "optimistic-concurrency", "snapshots", "projections"]
---

# 事件溯源：事件流怎样成为事实，快照与投影怎样安全重建

学习入口：系统只保存账户余额 70，怎样解释它由哪几次入账和出账形成，并在投影丢失后得到同一状态？[事件溯源](../../glossary/architecture.md#architecture.event-sourcing)把状态变化保存为有序[事件流](../../glossary/messaging.md#messaging.models)，但“有事件”不等于事件已经成为权威历史。前置：[聚合与业务不变量](domain-models-aggregates-and-invariants.md)、[事件格式演进](../messaging/event-contracts-schema-evolution-and-replay.md)。本文的账户、版本与恢复流程是纸面推演，没有运行事件存储或 [Broker](../../glossary/messaging.md#messaging.roles)。

## 权威记录是事件流，而不只是附带审计日志

事件溯源（Event Sourcing）把应用状态的每次有效变化记录为事件序列，并通过按序应用事件得到当前或过去状态。[Fowler 的原始说明](https://martinfowler.com/eaaDev/EventSourcing.html)强调，关键不是额外写一份变更日志，而是所有领域状态变化都由这些事件发起并可由其重建。

一个事件通常需要稳定的流身份、流内版本、事件身份、类型、发生事实所需的数据和格式版本。名称采用过去式业务事实，例如 `MoneyDeposited`，因为写入后它声明某件事已经被权威接纳。`SetBalanceTo70` 只记录结果，可能丢失原因、参与金额和可解释性；但事件粒度仍须按具体领域选择，不能把每次字段赋值机械地转成事件。

[Microsoft Event Sourcing 模式](https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing)把每个[实体](../../glossary/architecture.md#architecture.domain-model)的有序事件流、追加存储、重建和物化视图列为核心机制，也明确提醒：事件设计、并发、演进和查询成本会显著增加复杂度，多数系统仍适合传统当前状态存储。

## 命令先重建状态，再按预期版本追加

以账户 `A9` 为例，权威流已有：

| 流版本 | 事件 | 应用后的余额 |
| --- | --- | ---: |
| 1 | `AccountOpened` | 0 |
| 2 | `MoneyDeposited(100)` | 100 |
| 3 | `MoneyWithdrawn(30)` | 70 |

两个处理者同时读取到版本 3 和余额 70，都尝试取 50。若事件存储只管追加，两笔都会写入，余额变成 -30。正确性来自“在预期版本 3 之后原子追加”：第一笔追加版本 4，余额变 20；第二笔以同一预期版本追加时被拒绝。它必须重读版本 4、重新执行业务判断，随后因余额不足拒绝，而不是把旧决定直接重试。

```text
load(stream=A9) -> events 1..3 -> state(balance=70, version=3)
decide(Withdraw(50)) -> MoneyWithdrawn(50)
append(stream=A9, expected_version=3, events=[...])
```

预期版本只保护这个流的追加条件。跨多个流共同成立的不变量、外部付款和消息发布仍需要其他事务或协调协议；全局时间戳也不能替代每个权威流的并发条件。一个命令产生多个事件时，还要说明它们是否作为同一次原子追加提交。

## 快照缩短重放，不替代事件历史

流很长时，可保存“应用到版本 100 后的状态快照”，加载时先验证快照身份和版本，再读取 101 之后的事件。快照是性能派生物：丢失时应能从事件重建，过旧时可以补放，格式升级失败时可以舍弃重做。若系统删除了快照之前的事件，快照就承担了新的权威责任，恢复、审计和迁移承诺必须随之改变。

快照不能修复坏事件，也不能证明应用逻辑在新版本下仍会得到相同结果。重放函数应尽量是确定的纯状态转换；当前时间、随机值、外部汇率和远程查询若没有作为事实保存，历史重算会漂移。事件处理还需分开两种行为：

- 聚合重建只更新内存状态，不发送邮件、扣款或再次发布集成事件；
- 在线订阅可以更新投影或触发外部流程，但要用事件身份、进度和业务状态约束重复效果。

因此，“重放”不是再次执行原始请求。历史流可以被读取很多次，真实副作用不能随之重复。

## 投影是可替换的解释结果

事件存储通常不适合订单列表、搜索或跨实体统计，常用投影把事件转换成面向查询的表或文档。这可以和 [CQRS](cqrs-read-write-models-and-projection-lag.md)组合，但两者彼此独立：[CQRS](../../glossary/architecture.md#architecture.cqrs) 可把普通事务表作为写模型；事件溯源也可直接计算小流状态而没有独立查询存储。

投影处理需要至少记录：投影代码版本、源流/分区位置、目标已持久版本和错误事件。更新投影与推进检查点若不在同一原子边界，崩溃后可能重复应用或越过未完成事件。累计型事件尤其危险：余额投影收到 `MoneyDeposited(100)` 两次不能变成 200；可以在目标事务内按事件 ID 去重，或按账户流版本做条件更新。

重建时，新投影 `P2` 从完整保留的历史或配对快照开始，读取到声明前沿，验证后再切换查询路由。旧 `P1` 在回退期继续服务。直接清空当前投影并原地回放，会把读者暴露在部分历史状态中；历史保留不足、解码器不兼容或投影代码依赖外部可变数据时，也不能保证重建。

## 事件演进与更正必须保留旧含义

不可变表示已经写入的事实不被静默改写，不表示所有字段永远合法保留，也不消除隐私删除义务。敏感数据可从事件中最小化、引用到有独立生命周期的受控存储，或采用符合具体法规和威胁模型的删除设计；不能用“事件不可变”覆盖适用要求。

格式演进要能解释全部保留历史。常见选择包括：保留多版本处理器；读取时把旧格式转换为当前内存表示；或追加明确的更正/冲销事件。直接批量改写历史会改变审计和重放输入，应作为高风险迁移单独证明。更多 writer/reader 方向、默认值和回放身份见[事件格式演进](../messaging/event-contracts-schema-evolution-and-replay.md)。

更正错误事实也不等于删除原事件。例如错误出账 30 后追加 `WithdrawalReversed(30, original_event_id=...)`，可以保留发生和更正的关系；但怎样修正外部付款、报表和已通知用户仍是业务流程，而不是重放自动完成。

## 不要把五类记录混成一个东西

| 记录 | 主要责任 | 不能自动提供 |
| --- | --- | --- |
| 事件存储 | 按流读取、预期版本追加、长期保存权威领域历史 | Broker 扇出、所有查询和外部副作用一次性完成 |
| 消息 Broker / 事件流平台 | 保留与分发消息，管理分区、消费者和位置 | 每个聚合的权威并发检查或完整领域重建接口 |
| [Transactional Outbox](../../glossary/messaging.md#messaging.outbox) | 将本地业务提交与待发布意图放入同一事务 | 把当前状态表变成事件溯源，或完成消费者业务 |
| CDC | 从数据库日志或变更接口捕获已提交数据变化 | 自动还原业务意图、保证事件粒度适合领域重建 |
| 审计日志 | 记录谁在何时执行了什么操作，支持追责、调查或合规证据 | 完整领域重建、流内并发控制或可重放的业务语义 |

一个实现可以让同一记录兼任多项职责，但必须逐项证明查询、并发、保留、恢复和发布保证。只因为 Kafka 中保存了很多事件，不能据此声称它就是满足本系统需求的事件存储。

事件溯源适合历史重建、业务事实天然重要且团队能长期维护[事件契约](../../glossary/messaging.md#messaging.event-contract)的局部领域。简单 CRUD、短生命周期系统、必须立即一致查询却没有投影方案，或无法承担历史演进与运维成本时，当前[状态模型](../../glossary/engineering.md#engineering.state-models)通常更合适。可按[限界上下文](../../glossary/architecture.md#architecture.ddd)选择，没必要全系统统一。

## 自检

1. 事件溯源与“当前表旁边加一张审计表”的权威关系有什么不同？
2. 两个命令都基于流版本 3 时，为什么预期版本追加能阻止旧决定同时生效？
3. 快照损坏或过旧时，系统依靠什么恢复；删除早期事件后承诺怎样变化？
4. 为什么聚合重放不能再次发邮件或扣款，在线投影又怎样处理重复事件？
5. 事件存储、Broker、Outbox、CDC 与审计日志分别解决哪一段问题？

## 来源与核查

- [Martin Fowler：Event Sourcing](https://martinfowler.com/eaaDev/EventSourcing.html)，核查日期 2026-10-23；覆盖事件作为状态变化来源、完整重建、时点查询与重放。
- [Microsoft：Event Sourcing pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing)，核查日期 2026-10-23；覆盖事件流、预期版本并发、快照/投影、事件存储与 Broker 区别及适用边界。
- [Microsoft：CQRS pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs)，核查日期 2026-10-23；覆盖事件溯源与读模型组合、投影[延迟](../../glossary/performance.md#performance.latency-throughput)及快照成本；本文不把两种模式视为绑定关系。

本文为 source-checked 概念说明。账户流、并发追加、快照、投影和更正事件均为综合纸面推演；没有执行事件存储、并发冲突、历史升级、投影重建、外部副作用或[灾难恢复](../../glossary/reliability.md#reliability.dr)实验。
