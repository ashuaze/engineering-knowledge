---
id: "kb-architecture-cqrs"
title: "CQRS：读写模型分开以后，怎样处理投影延迟与重建"
kind: "concept"
domain: "architecture"
status: "evolving"
summary: "解释命令与查询模型的职责分离、同库与分库存储、投影进度、读己之写和可切换重建边界。"
created: "2026-10-23"
updated: "2026-10-26"
last_verified: "2026-10-23"
verification: "source-checked"
prerequisites: ["kb-architecture-aggregates-invariants", "kb-messaging-outbox"]
related: ["kb-architecture-event-sourcing", "kb-database-cdc", "kb-cache-search-index-cutover", "kb-distributed-consistency", "kb-api-conditional-requests", "kb-architecture-deployment-boundaries", "kb-architecture-quality-decisions"]
tags: ["cqrs", "projections", "consistency", "rebuild"]
---

# CQRS：读写模型分开以后，怎样处理投影延迟与重建

学习入口：订单提交已经成功，列表页为什么仍显示“草稿”？如果列表来自异步读模型，这可能是可预期的投影[延迟](../../glossary/performance.md#performance.latency-throughput)，也可能是更新链路已经停住。前置：[领域模型、聚合与业务不变量](domain-models-aggregates-and-invariants.md)、[Transactional Outbox](../messaging/transactional-outbox.md)。本文讨论 [CQRS](../../glossary/architecture.md#architecture.cqrs) 的模型与恢复边界；订单版本、时间线和伪代码是纸面推演，没有运行数据库、消息系统或投影器。

读写职责分离不直接决定服务数量，部署选择见[模块化单体与微服务](modular-monoliths-microservices-and-service-boundaries.md)；是否值得承担投影与恢复成本，需用[质量场景和架构决策](quality-attribute-scenarios-tradeoffs-and-adrs.md)明确目标与证据。

## 分开的是职责和模型，不必先分数据库

CQRS（Command Query Responsibility Segregation）让修改状态的命令与读取状态的查询采用不同模型或接口。命令表达业务意图，例如“提交订单”，由写模型检查权限、当前版本和不变量；查询返回面向页面或调用方的 DTO，不承担修改权威状态的职责。[Microsoft CQRS 模式](https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs)明确给出两种层次：读写模型可共享一个存储，也可使用不同存储。

因此，下面几件事不能从“采用 CQRS”自动推出：

- 必须拆成两个服务或两个数据库；
- 必须异步处理命令；
- 必须采用[事件溯源](../../glossary/architecture.md#architecture.event-sourcing)；
- 读模型可以跳过[授权](../../glossary/security.md#security.identity)，或把陈旧结果当成写入前提。

CQRS 也不等于把每个 HTTP GET 和 POST 放进不同类。只有当读写的模型、规则、负载或演进方向确实不同，分离才有实质意义。[Fowler 的 CQRS 说明](https://martinfowler.com/bliki/CQRS.html)同样强调，它适合少数复杂领域或明显不对称的读写需求，普遍套用会增加风险。

## 命令回答是否接纳，查询回答当前可见状态

命令应包含稳定的目标身份、业务意图和必要的并发前提。它可以同步返回“已拒绝”、新资源 ID、权威版本或已接纳的操作 ID；不能因为名称叫 command 就禁止一切返回值。真正要避免的是用查询模型的陈旧字段代替写侧验证。

```text
SubmitOrder(order_id=O7, expected_version=41)
  写模型读取 O7 的权威版本与状态
  校验调用者、草稿状态、明细和 expected_version
  原子提交订单 version=42 与待投影记录 source_version=42
  返回 accepted, order_id=O7, write_version=42
```

查询模型可以把订单、客户显示名、商品摘要和配送状态预先组合成一行，以便直接返回列表。它面向访问模式，不应反向成为修改订单的权威入口。[Materialized View 模式](https://learn.microsoft.com/en-us/azure/architecture/patterns/materialized-view)把这种视图描述为可从来源重建、由专门组件维护的只读投影，而不是调用方直接修改的第二份事实。

## 同库与分库存储对应不同的一致性成本

| 形态 | 更新方式 | 能得到什么 | 仍需承担什么 |
| --- | --- | --- | --- |
| 同一存储、不同模型 | 一次事务更新权威表，查询使用专用视图、索引或 DTO | 可以保留事务内一致读取，先验证职责分离是否有价值 | 读写负载仍争用同一存储，模型演进仍需协调 |
| 不同读写存储 | 写侧提交后，通过日志、[Outbox](../../glossary/messaging.md#messaging.outbox) 或 CDC 更新读侧 | 可独立扩缩、采用不同结构并隔离复杂查询 | 延迟、重复、漏更新、[重排](../../glossary/cache-search.md#cache-search.hybrid)、重建和切换成为显式协议 |

分库存储时，“写表成功”和“投影更新已持久完成”是两个提交点。直接先写数据库再发布消息会留下双写窗口；可用 [Outbox](../messaging/transactional-outbox.md)保存发布意图，或用 [CDC](../database/cdc-snapshots-log-positions-and-replay.md)从已提交日志捕获变化。两者都不替投影器完成去重、顺序验证和目标提交。

## 版本 42 已提交，读模型仍为 40

假设写模型已原子提交订单 `O7` 的版本 42，读模型还停在版本 40：

| 观察 | 可以判断 | 不能判断 |
| --- | --- | --- |
| 命令返回 `write_version=42` | 写侧契约声明版本 42 已接纳并提交 | 页面投影已经包含版本 42 |
| 查询返回 `projection_version=40`，且它表示最后连续应用的源版本 | 这份读结果至少落后两个源版本 | 命令失败，或版本 41/42 永久丢失 |
| 投影进度长期不变 | 链路可能阻塞、毒消息或检查点异常 | 单凭年龄确定具体故障点 |

读己之写必须写成可执行契约，可按需求选择：命令响应直接返回刚确认的必要字段；查询携带最低版本 42 并有界等待投影追上；临时回源权威存储；或在会话中把已确认变化覆盖到旧投影上。等待超时应明确返回“写入已成功、视图仍在追赶”，不能盲目重交命令。

投影器可以为每个订单保存 `last_applied_version`。收到版本 42 时，若当前为 41，则在同一目标事务中更新视图和进度；再次收到 42 时不重复累计；当前仍为 40 时则等待 41、从可证明连续的位置补读或触发重建。只存一个全局“最后时间”通常不足以证明跨分区连续性；来源位置、业务版本和目标持久进度要分别记录。

对金额汇总尤其要声明输出语义。若版本 42 给出“订单总额现为 130”，目标应按订单与版本覆盖；若给出“增加 30”，重复应用就会放大。[幂等](../../glossary/api.md#api.idempotency)键、版本条件和目标写入必须与事件含义一致。

## 重建投影需要完整来源、进度和原子切换

可重建不是一句“删表重放”。安全流程通常是：

1. 固定可配对的来源快照和日志位置 `S`，在新命名空间建立投影版本 `P2`。
2. 从快照回填，再从 `S` 连续追增量；记录每个来源分区或业务流的已完成位置。
3. 比较行数、关键[聚合](../../glossary/architecture.md#architecture.domain-model)、缺口、重复和授权过滤，确认 `P2` 追到切换要求的前沿。
4. 原子切换读别名或路由，保留 `P1` 作为有限期回退；切换后继续监控延迟和错误。

这与[索引重建水位和切换](../cache-search/index-rebuild-watermarks-and-cutover.md)的边界相同：全量扫描和增量订阅必须接成一条连续历史，半成品不能直接覆盖仍可用的旧视图。若源端保留期短于重建耗时，或投影逻辑不能读取旧格式，声称“随时可重建”没有证据。

## 陈旧、安全与删除都要有显式策略

读模型延迟不仅影响显示。若它用于余额、库存或权限判断，调用者可能基于旧值发起危险动作；写模型仍须在提交时重新检查权威状态和授权。面向不同受众的投影还要执行字段最小化、[租户隔离](../../glossary/security.md#security.tenant-isolation)与删除传播，不能因为源端已经撤权，就默认旧投影立即不可读。

需要观测的不只是[队列](../../glossary/algorithms.md#algorithms.queues)长度：至少记录源端最新可用位置、投影已持久位置、版本缺口、最老未应用年龄、重复/拒绝量、重建阶段和切换版本。[服务目标](../../glossary/reliability.md#reliability.slos)应说明允许多旧、哪些查询必须读己之写、超限时降级到哪里。

简单 CRUD、强一致查询和规模有限时，共享模型通常更直接。只为一个昂贵报表建立专用投影，也不必把全部查询都迁入 CQRS。收益应由模型复杂度、读写不对称或隔离需求解释，而不是由流行架构图解释。

## 自检

1. CQRS 是否要求读写使用不同数据库，为什么？
2. 写侧版本 42 已提交而读侧为 40 时，客户端怎样区分“命令失败”和“投影追赶中”？
3. 投影重复收到同一增量时，哪项状态必须与业务更新一起提交？
4. 重建读模型时，快照和增量从哪个位置接续，怎样避免把半成品发布给读者？
5. 哪些权限或业务不变量必须回到写侧确认，不能相信陈旧投影？

## 来源与核查

- [Microsoft：CQRS pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs)，核查日期 2026-10-23；覆盖同库/分库模型、命令与查询职责、异步同步及复杂度边界。
- [Microsoft：Materialized View pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/materialized-view)，核查日期 2026-10-23；覆盖只读投影、刷新、陈旧、重建和版本化替换。
- [Martin Fowler：CQRS](https://martinfowler.com/bliki/CQRS.html)，核查日期 2026-10-23；覆盖模型分离、适用范围及过度采用风险。

本文为 source-checked 概念说明。版本 40/42、投影伪代码、读己之写和重建流程均为综合教学设计；没有执行数据库双写、Outbox/CDC、消息重放、投影切换、权限传播或真实负载实验。
