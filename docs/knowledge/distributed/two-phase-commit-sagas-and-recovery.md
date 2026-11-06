---
id: "kb-distributed-transactions-sagas"
title: "跨服务事务：2PC、Saga 与补偿恢复"
kind: "concept"
domain: "distributed"
status: "evolving"
summary: "从部分成功解释两阶段提交的持久决议与阻塞，以及 Saga 的本地提交、业务补偿、并发隔离和恢复责任。"
created: "2026-10-22"
updated: "2026-10-22"
last_verified: "2026-10-22"
verification: "source-checked"
prerequisites: ["kb-database-isolation-mvcc", "kb-distributed-consistency"]
related: ["kb-distributed-consensus-quorum", "kb-messaging-outbox", "kb-api-idempotency", "kb-distributed-leases-fencing", "kb-reliability-retry-budgets"]
tags: ["transactions", "two-phase-commit", "saga", "compensation", "recovery"]
---

# 跨服务事务：2PC、Saga 与补偿恢复

学习入口：订单已提交、库存已预留，支付却失败了，系统现在算成功还是失败？各服务使用自己的[数据库事务](../../glossary/database.md#database.isolation)，只能分别保护各自的提交范围。跨服务流程必须再定义：哪些结果可以暂时存在、谁决定最终结果、[进程](../../glossary/systems.md#systems.execution-units)重启后依据什么继续。

前置：[事务隔离与 MVCC](../database/isolation-and-mvcc.md)、[一致性与复制](consistency-and-replication.md)。本文解释经典[两阶段提交](../../glossary/distributed.md#distributed.2pc)与 [Saga](../../glossary/distributed.md#distributed.saga) 的机制和恢复边界；不提供事务管理器实现，也不把所有分布式事务归为这两种方式。

## 本地成功不能直接合成跨服务原子性

设订单服务与库存服务独立提交。先提交订单再扣库存，会有“订单已提交、库存尚未提交”的窗口；调换顺序只是交换窗口位置。把 HTTP 调用写进订单事务，不能让库存数据库自动加入这个事务，订单回滚也不能撤销已经完成的库存提交。

可先问业务规则到底要求什么。如果“不允许任何参与者最终提交、另一些最终回滚”，需要能覆盖这些资源的原子提交协议。如果允许预订暂时存在，失败后以取消、退款等业务动作收敛，则可以讨论 Saga。若同一规则必须在一个不可分割的决策内判断，也应重新评估数据与服务边界。

| 方案 | 跨边界的主要承诺 | 需要另行说明 |
| --- | --- | --- |
| 本地事务 | 所覆盖资源内共同提交或回滚 | 事务之外的调用、消息与业务动作 |
| 2PC | 参与资源遵守同一最终提交或中止决定 | 持久状态、失联等待、隔离与读取范围 |
| Saga | 本地步骤分别提交，以后续步骤或补偿处理部分完成 | 中间状态、业务补偿、[并发](../../glossary/systems.md#systems.concurrency)冲突与失败责任 |

## 2PC：Prepared 是承诺，不是最终提交

两阶段提交 Two-Phase Commit（2PC）由协调者联系参与资源。以所有参与者都需要实际修改数据的基本流程为例：

1. **准备阶段**：协调者请求 Prepare；参与者检查本地事务能否提交，保存恢复所需状态，再回复 Prepared。无法准备的参与者投否决票。
2. **决定阶段**：只有全部参与者准备成功，协调者才可决定 Commit；否则可决定 Abort。随后把最终决定送到各参与者，参与者完成本地提交或回滚。

投票及阶段边界参照 [Microsoft 的 2PC 协议说明](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-tpsod/e34079f0-22de-4c03-9cb8-84c2448a4613)。实际协议还可能有只读参与者、层级协调与日志优化，不应把这里的两轮文字当成完整实现规范。

Prepared 的含义是“我已保留以后按最终决定完成的能力”，不是“我已独立提交”。[PostgreSQL 18 的 PREPARE TRANSACTION](https://www.postgresql.org/docs/18/sql-prepare-transaction.html)会把事务状态保存到磁盘，并与原会话分离；以后可由其他会话执行 COMMIT PREPARED 或 ROLLBACK PREPARED。准备期间仍持有相应锁，也会妨碍旧版本清理，因此不能把 Prepared 当成可无限遗忘的轻量任务。

参与者必须在回复 Prepared 前持久保存准备状态，协调者必须在发布 Commit 前持久保存提交决定；恢复者要能够找到这些记录及事务标识。[Gray 与 Lamport 的原论文第 3、5 节](https://arxiv.org/pdf/cs/0408036)解释了稳定存储与协调者故障的关系。下面的恢复分析采用显式记录最终决定的基本模型，不替代具体产品对中止记录和日志清理的规则。

## 协调者恢复：重新发送决定，不能重新投一次票

教学设定：资源 A、B 都已 Prepared，事务号为 X；日志可靠保留，参与者不任意破坏协议。

| 故障窗口 | 恢复时应依据什么 | 危险处理 |
| --- | --- | --- |
| 协调者尚未形成持久提交决定便停止 | 依其日志协议恢复未决事务；本模型可决定中止并记录、通知 | 把“应用请求提交过”当作已经决定提交 |
| 协调者记录 Commit，A 已提交，给 B 的消息丢失 | 恢复同一个 Commit 决定，继续驱动 B 完成 | 因 B 等待过久而改成 Abort |
| B 已提交，但完成回执丢失 | 用 X 查询、核对终态，按协议重复通知 | 另起一笔业务事务再扣一次 |
| B 只知道自己已 Prepared，又联系不到决议持有者 | 等待或向协议允许的恢复方查询 | 仅凭本地[超时](../../glossary/api.md#api.retries)自行回滚 |

最后一行说明经典 2PC 的协议阻塞条件：参与者已承诺准备，又无法得到足以确定结果的信息。这指协议暂时不能确定终态，不要求某个执行线程挂起。它不能排除协调者已经决定 Commit，甚至另一个参与者已经提交。超时只证明未及时得到答复；本地“直接回滚以释放锁”可能破坏[原子性](../../glossary/systems.md#systems.atomicity)。若尚未作出准备承诺，处理选择不同；不能笼统说任意阶段都永远不能超时中止。

这里的保证还依赖故障模型：稳定记录可恢复、事务标识与参与集合正确、消息可按协议重试，且恢复过程不会出现互相冲突的权威。永久丢失决议日志、人工启发式处置或绕过协议提交，都需要单独分析；不能拿经典结论兜底。

2PC 负责原子提交，不能单凭它推出跨资源任意读取都[可串行化](../../glossary/distributed.md#distributed.linear-serial)、所有位置同一瞬间可见。它也不等同于多数副本[共识](../../glossary/distributed.md#distributed.consensus)：复制协调者状态可以改善某些故障下的恢复，但仍需资源的准备、参与集合和完整提交协议。原论文讨论的是它们的具体联系，不能从“都做决定”推导相同[可用性](../../glossary/reliability.md#reliability.availability)。参见[共识与 Quorum](consensus-leaders-and-quorums.md)。

## Saga：每一步已提交，补偿是另一笔业务

Saga 把长流程拆成可与其他工作交错的本地事务，各步分别提交；后续失败时，以补偿修正已完成步骤的效果，机制参照 [Microsoft 的 Saga 模式](https://learn.microsoft.com/en-us/azure/architecture/patterns/saga)。服务实现还需要消息、持久流程状态和恢复机制，不能只画一串调用箭头。

下面是自设的订单教学流程，各步业务契约均是假设，未执行：

| 已提交步骤 | 对应补偿 | 补偿后的业务含义 |
| --- | --- | --- |
| T1：以预订号 R 预留一件库存 | C1：释放 R 对应的预留 | 撤销这次预留，不覆盖其他订单的库存变化 |
| T2：以支付号 P 扣款 | C2：按 P 发起退款 | 形成扣款与退款记录；到账时间、费用另有约定 |
| T3：确认发货 | 未必存在完整逆操作 | 已交付商品可能只能进入退货或人工处置流程 |

若 T2 明确失败，可执行 C1；若 T2 只是响应超时，必须先核实 P 的结果，不能直接认定没有扣款。即使 C2 成功，扣款历史、手续费或用户已经收到的通知也不会消失。

[Microsoft 的补偿事务模式](https://learn.microsoft.com/en-us/azure/architecture/patterns/compensating-transaction)明确指出，补偿不必恢复最初数据，也不总按原步骤逆序执行；它依赖业务规则。不可逆动作应设清楚的承诺边界：尽量先完成必要校验和可取消预留，再进入承诺阶段，之后可能需要向前完成、对账或人工处置，不能虚构一个通用 `Undo`。

## 隔离与重试：恢复动作本身也会竞争

Saga 的子事务已经提交，其他流程可能观察并使用中间结果。[官方 Saga 模式的并发异常说明](https://learn.microsoft.com/en-us/azure/architecture/patterns/saga#potential-data-anomalies-in-sagas)指出跨服务没有内建隔离。这里的“读到未完成 Saga 的中间状态”不等于数据库允许读取未提交 SQL 数据，两层边界必须分开。

教学反例：库存初始可用量 10，流程 X 预留 1 后为 9，流程 Y 又预留 2 后为 7。X 失败时若把库存“恢复为之前的 10”，就抹掉了 Y 的合法预留。C1 应按预订号取消 X 所拥有的那一份，并在本地事务中检查当前状态；能否取消还取决于预留是否已经转为发货。

可用预订记录、处理中状态、条件更新与业务版本保护共享不变量；所有相关写入口都必须遵守同一规则。它们是具体并发协议，不会因命名为 Saga 就自动获得可串行化。旧恢复者继续发出命令时，还可能需要[执行代次隔离](leases-heartbeats-and-fencing.md)。

正向步骤和补偿都可能重复。建议稳定标识至少区分流程、步骤与动作类型，例如 `(X, reserve)` 和 `(X, release)`；服务在自己的事务内记录动作结果与状态转换。相同动作重试应复用已知结果，重复释放不能再次增加库存。先到达的取消命令还应使迟到的预留被拒绝或转入已约定的恢复路径，避免“取消后又预留”。这些是本例的设计要求，实际实现需另验。

## 让失败留下可接手的责任

编排式 Saga 由协调流程决定下一步；事件协作式 Saga 由参与者响应事件。两者都需要能恢复的事实记录。AWS 的[编排式说明](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/saga-orchestration.html)与[事件协作式说明](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/saga-choreography.html)展示了这两种组织方式；选择其中一种并不消除命令丢失、重复和部分完成。

建议为每个流程保存：稳定标识、当前阶段、已确认效果、未知结果、待补偿动作、[重试预算](../../glossary/reliability.md#reliability.retry-budget)和负责方。下面是教学状态划分：

| 记录状态 | 后续责任 |
| --- | --- |
| 结果未知 | 依据稳定动作号查询外部事实，或按可证明安全的契约重试 |
| 正向待继续 | 从已确认边界继续，不重复生成新的业务意图 |
| 补偿待继续 | 保留待办与已完成补偿，允许从中断处恢复 |
| 需人工处理 | 明确告警、负责人和未解决效果；不能伪装为已补偿 |
| 业务已收敛 | 保留可审计终态，再按保留策略回收恢复记录 |

补偿本身可能失败。上述[补偿事务模式](https://learn.microsoft.com/en-us/azure/architecture/patterns/compensating-transaction)要求保留进度、支持重复执行，并在自动恢复不足时通知人工处理。有限重试预算用完后，应转移责任并保留事实，而不是删掉流程或承诺“一定最终一致”。

[Outbox](../messaging/transactional-outbox.md)可以让本地业务状态和下一步消息意图共同提交；它不替 Saga 实现补偿语义，也不使下游只执行一次。[幂等性](../api/idempotency.md)处理重复效果，[重试预算](../reliability/timeouts-and-retry-budgets.md)限制恢复负载，这些机制需要组合使用。

## 自检与核查范围

自检：B 处于 Prepared 且超时，为何不能自行回滚？协调者已有 Commit 日志，重启后为何不应重新收票？退款成功为何不等于扣款从未发生？X 的补偿为何不能覆盖库存旧值？补偿失败后谁持有未完成责任？

核查日期：2026-10-22。2PC 依据 Gray/Lamport 原论文、Microsoft 协议说明和 PostgreSQL 18；Saga、补偿与组织方式依据 Microsoft 和 AWS 官方架构文档。本文订单、故障表和状态划分为教学推演与设计分析；未运行分布式事务管理器、准备事务、消息编排或支付/退款实验。实际选型还需核对产品版本、资源支持、恢复日志与隔离承诺。
