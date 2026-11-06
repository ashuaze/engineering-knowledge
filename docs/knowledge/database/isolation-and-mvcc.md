---
id: "kb-database-isolation-mvcc"
title: "事务隔离与 MVCC：同一事务到底能看到什么"
kind: "concept"
domain: "database"
status: "evolving"
summary: "以 PostgreSQL 18 的普通查询解释语句快照、事务快照与写偏斜，明确可串行化和重试边界。"
created: "2026-10-16"
updated: "2026-10-20"
last_verified: "2026-10-16"
verification: "source-checked"
prerequisites: []
related: ["kb-database-concurrent-inventory", "kb-distributed-consistency", "kb-api-idempotency", "kb-reliability-retry-budgets", "kb-database-indexes-plans", "kb-api-contracts-pagination", "kb-database-inventory-lab", "kb-systems-deadlocks-recovery", "kb-database-wal-recovery"]
tags: ["transactions", "isolation", "mvcc"]
---

# 事务隔离与 MVCC：同一事务到底能看到什么

学习入口：一个事务里两次查询结果不同，是数据库没遵守事务吗？前置知识：基本 SELECT/UPDATE、提交与回滚。本文限定 PostgreSQL 18 主库上普通数据表的事务与查询；带锁查询、DDL、序列和副本有额外规则，不把这里的行为推广到所有数据库。

## 原子提交与隔离分别解决什么

[原子性](../../glossary/systems.md#systems.atomicity)关心一组数据库修改共同提交或回滚；隔离性关心[并发](../../glossary/systems.md#systems.concurrency)事务允许看到和产生怎样的结果。把几条 SQL 放在 BEGIN/COMMIT 之间，不代表其他事务暂停运行，也不代表每次查询都看到同一版本。

[MVCC](../../glossary/database.md#database.mvcc)（多版本并发控制）保留不同版本，并结合快照与可见性规则决定一次读取能看到什么。[PostgreSQL 的机制介绍](https://www.postgresql.org/docs/18/mvcc-intro.html)说明普通读写如何借助版本减少相互[阻塞](../../glossary/systems.md#systems.blocking)。这不意味着所有操作都无锁：并发更新、显式行锁和表级锁仍可能等待。

## 普通读取：快照在什么时候确定

以下是 [PostgreSQL 18 隔离文档](https://www.postgresql.org/docs/18/transaction-iso.html)中普通 SELECT 的简化口径；查询也能看到自身事务此前的修改。

| 级别 | 普通读取的快照 | 主要边界 |
| --- | --- | --- |
| Read Committed（默认） | 每条语句开始时取得自己的快照 | 两次查询间可见其他事务新提交的修改 |
| Repeatable Read | 从第一条非事务控制语句起使用稳定的事务快照 | PostgreSQL 中避免[不可重复读](../../glossary/database.md#database.anomalies)与幻读，仍可能有[序列化](../../glossary/runtime.md#runtime.serialization)异常 |
| Serializable | 在稳定快照基础上监测危险依赖 | 成功提交的相关事务可解释为串行执行；应用需处理序列化失败 |

PostgreSQL 的 Read Uncommitted 按 Read Committed 工作。[隔离级别](../../glossary/database.md#database.isolation)名称具有标准最低约束，但实现可能更强，不能拿这张表直接描述其他数据库。

脏读指读到其他事务未提交的修改；不可重复读指重读记录时看见其他事务提交的变化；幻读关心再次按条件查询时结果集合变化。避免这几类现象仍不足以推导所有业务规则都成立。

## 两次读取的纸面历史

教学设定：一行数据的值初始为 10，没有 DDL 或第三个写入者，A 只执行普通查询。

| 时刻 | 会话 A | 会话 B |
| --- | --- | --- |
| 1 | BEGIN，然后 SELECT，得到 10 | |
| 2 | | BEGIN，UPDATE 为 20，COMMIT |
| 3 | 再次执行相同 SELECT | |
| 4 | COMMIT | |

Read Committed 下，A 的第二条查询可以看到 20；Repeatable Read 下仍看到 10，因为 B 的提交发生在 A 已确定的快照之后。这里的“仍看到旧值”符合事务快照设计，与异步副本落后是不同原因。

若 A 随后更新 B 已改动的行，不能继续照搬“普通读取”的结论。Read Committed 下可能等待并重新检查更新条件；Repeatable Read 下可能因并发更新而失败。库存中的条件更新机制见[库存并发](concurrent-inventory.md)。

## 稳定快照为什么仍可能违反规则

教学规则：两名值班者 A、B 中至少一人保持在岗。初始两人均在岗，每人只有自己的状态行。两个 Repeatable Read 事务都先读到“在岗人数为 2”，随后分别将自己改为离岗。

```text
T1：看到 A、B 都在岗 → 更新 A 为离岗
T2：看到 A、B 都在岗 → 更新 B 为离岗
两者更新不同的行；若都提交，最终无人值班。
```

两边的读取可以各自稳定，最终结果仍不符合任何遵守该检查的串行顺序。这类依赖问题通常称为[写偏斜](../../glossary/database.md#database.write-skew)（Write Skew）。[应用层一致性检查文档](https://www.postgresql.org/docs/18/applevel-consistency.html)解释了快照检查与并发写入之间的依赖风险。

处理方式应围绕不变量选择：能表达为唯一或其他数据库约束的规则优先明确约束；也可设计所有相关写入共同遵守的锁定协议，或让完整检查与修改在 Serializable 下执行。只锁“当前查到的那一行”不自动覆盖另一行或尚不存在的记录。所有影响不变量的写路径都必须参与，单独改一个接口的级别不能保护任意绕行写入。

## 可串行化需要完整事务重试

在上述教学规则中，相关事务都使用 Serializable 并完整执行检查时，数据库不能让违反串行语义的结果一起提交；应用应准备接收失败并重做决策。Serializable 不修复一个单独运行就写错的业务流程，也不包含事务之外的支付或邮件副作用。

[PostgreSQL 的失败处理说明](https://www.postgresql.org/docs/18/mvcc-serialization-failure-handling.html)要求对 `40001` [重试](../../glossary/api.md#api.retries)整个事务，包括决定查询和写入值的逻辑。只重放最后一条 UPDATE，会继续沿用旧判断。重试仍需次数、退避与总时间预算，提交结果未知也不能自动当成已经回滚。

事务内已调用外部支付，数据库回滚后重跑就可能再次扣款。外部动作应另设稳定标识与恢复协议；本地隔离保证不等于跨系统[恰好一次](../../glossary/messaging.md#messaging.exactly-once)。

## 自检与证据边界

为一次并发操作分别写出：要保护的不变量、读取快照、冲突对象、允许失败的位置与重试范围。再解释三个反例：稳定快照为何不必然保护跨行规则；事务开始时间为何不能总当作快照时间；数据库回滚为何不能撤销外部动作。

本文两段并发历史均为依据文档的纸面推演，尚未按本文时序直接执行；[库存并发实验](inventory-concurrency-lab.md)已覆盖固定单行库存的 Read Committed 竞争、回滚和锁错误，未覆盖本文的稳定快照与跨行写偏斜历史。[查询计划实验](query-plans-lab.md)也不覆盖这些隔离历史。后续实测需记录版本、隔离设置、完整时序、提交结果和 SQLSTATE；显式锁、DDL、序列及副本行为应分别核查。

## 关联阅读与来源

- [WAL 与崩溃恢复](wal-and-crash-recovery.md)：把原子提交、并发隔离与持久化恢复分开解释。

- [HTTP 契约与分页](../api/contracts-and-pagination.md)：游标位置不冻结跨请求的结果，区分分页与快照保证。

- [索引与执行计划](indexes-and-query-plans.md)：把记录可见性与访问路径分开，理解索引仅扫描的表访问。
- [库存并发](concurrent-inventory.md)：把单行库存约束放进原子条件更新；[配套实验](inventory-concurrency-lab.md)已有实际会话、回滚与锁错误记录。
- [一致性与复制](../distributed/consistency-and-replication.md)：区分事务快照与读取副本的新鲜度。
- [幂等性](../api/idempotency.md)：处理结果未知与重复业务动作。
- [重试预算](../reliability/timeouts-and-retry-budgets.md)：限制冲突恢复的额外负载与耗时。

核查日期：2026-10-16，适用范围为 PostgreSQL 18 文档所述机制。值班者与读取历史为教学设计，未作数据库实验。

- [PostgreSQL 18：Introduction to MVCC](https://www.postgresql.org/docs/18/mvcc-intro.html)
- [PostgreSQL 18：Transaction Isolation](https://www.postgresql.org/docs/18/transaction-iso.html)
- [PostgreSQL 18：Data Consistency Checks at the Application Level](https://www.postgresql.org/docs/18/applevel-consistency.html)
- [PostgreSQL 18：Serialization Failure Handling](https://www.postgresql.org/docs/18/mvcc-serialization-failure-handling.html)
