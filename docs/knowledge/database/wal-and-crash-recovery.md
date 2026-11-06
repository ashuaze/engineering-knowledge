---
id: "kb-database-wal-recovery"
title: "WAL 与崩溃恢复：提交后数据页为何还没写完"
kind: "concept"
domain: "database"
status: "evolving"
summary: "区分日志持久化、数据页写回、检查点与恢复，说明提交确认和存储故障的边界。"
created: "2026-10-19"
updated: "2026-10-20"
last_verified: "2026-10-19"
verification: "source-checked"
prerequisites: ["kb-database-isolation-mvcc"]
related: ["kb-database-backups-pitr", "kb-database-recovery-lab", "kb-database-schema-migrations", "kb-distributed-consistency", "kb-api-idempotency", "kb-database-lsm"]
tags: ["postgresql", "wal", "durability"]
---

# WAL 与崩溃恢复：提交后数据页为何还没写完

事务已经返回提交成功，数据库却可能还没有把所有受影响的数据页写回持久存储。这两件事并不矛盾：以 PostgreSQL 18 的普通持久表为例，恢复机制可以依靠先持久化的日志重建相应修改，而不要求每次提交同步写完所有数据页。

前置知识：[事务隔离与 MVCC](isolation-and-mvcc.md)。本文解释本机 [WAL](../../glossary/database.md#database.recovery-log) 与恢复的机制，不把它推广为所有数据库的日志架构，也不提供生产参数调优或断电[可靠性](../../glossary/reliability.md#reliability.availability)证明。

## 预写日志中的“先”约束什么

WAL（Write-Ahead Logging，预写日志）的关键顺序是：把相关数据页写到持久存储之前，描述这些修改的日志必须先持久化。若故障时部分修改还没有体现在数据页中，恢复可以重放必要的日志，也就是 REDO。依据见 [PostgreSQL WAL 原理](https://www.postgresql.org/docs/18/wal-intro.html)。

WAL 不是应用打印的 SQL 日志，也不是把业务请求文字重新发送一次。数据库在恢复时遵守自己的记录格式和事务状态，不会因为重放某段日志就再次调用应用里的支付接口。也不能把 PostgreSQL WAL 当成所有引擎通用的 Undo 日志；事务回滚、行版本可见性和崩溃重放需要分别理解。

用下面的教学流程建立顺序感，不把它当作完整内部执行时序：

```text
业务修改 → 产生相应 WAL 与内存中的页修改
→ 按提交配置等待必要的日志持久化 → 返回提交结果
→ 数据页在后续适当时机写回
故障重启 → 从恢复起点重放必要 WAL → 恢复一致状态
```

因此“数据页还没全部写回”不能单独证明已确认事务一定会丢失；反过来，“调用了写入函数”也不能证明字节已经越过所有易失缓存。

## 提交确认需要带上配置前提

在本机持久化设置成立时，同步提交等待的是必要 WAL 的本地持久化；异步提交则可能先确认，再完成相应持久化，故障时最近确认的事务仍可能丢失。[异步提交文档](https://www.postgresql.org/docs/18/wal-async-commit.html)说明了这种性能与耐久性取舍。

| 观察 | 能据此判断什么 | 仍然不能证明什么 |
| --- | --- | --- |
| 客户端收到 COMMIT 成功 | 数据库已按该事务适用的配置完成提交确认 | 所有数据页已写回、所有副本已重放 |
| 本地 WAL 已持久化 | 对应本机恢复材料达到所记录的持久化位置 | 另一[故障域](../../glossary/reliability.md#reliability.fault-domains)也有可用副本或完整备份 |
| 副本查询到了新值 | 该副本已推进到可见状态 | 可以恢复误删除之前的历史 |
| 客户端提交等待[超时](../../glossary/api.md#api.retries) | 调用方没有及时收到确定结果 | 数据库必然回滚了事务 |

提交附近连接断开仍属于[结果未知与幂等性](../api/idempotency.md)问题。WAL 机制不能替调用方判断一笔业务动作是否已完成，也不会消除重试去重的需要。

## 检查点帮助限定恢复工作

[检查点](../../glossary/database.md#database.checkpoints)用于推进数据库持久化与恢复起点；崩溃恢复并非每次都从建库开始重放全部日志。它也不是“给每个事务做一次全量备份”。检查点、页写回和日志保留的关系见 [PostgreSQL WAL 配置的 Checkpoints 说明](https://www.postgresql.org/docs/18/runtime-config-wal.html)。

教学推演：较早的一批修改已通过检查点相关工作写入，后续又发生一批修改；故障后主要依靠恢复起点之后仍需要的日志推进，而不是要求所有历史文件永远保留在在线日志目录。

在线 WAL 的回收还受归档、复制等用途约束。不能因为一次 CHECKPOINT 成功就手动删除 pg_wal 文件，也不能把“在线目录还有日志”当成已建立长期历史恢复能力。历史恢复需要另外设计备份、归档连续性与保留规则。

## 存储链路决定持久化保证能否兑现

内存、操作系统缓存、控制器和设备之间存在多个层次。数据库能够请求同步写入，但可靠性还依赖底层正确执行这些请求；一次正常重启成功不足以证明断电或设备故障时的行为。[可靠性说明](https://www.postgresql.org/docs/18/wal-reliability.html)讨论了这条存储链路。

与此相关的 fsync、full_page_writes、synchronous_commit 各自控制不同环节，不能因都与“持久化”有关就互相替代。关闭某项设置后的吞吐变化也不是免费的收益，应先明确故障时可能失去什么；本文不建议套用任何关闭参数的性能配方。

## 恢复一致不等于撤销错误业务

如果应用合法提交了一条错误 DELETE，数据库可能完整记录并可靠恢复这条删除。崩溃恢复追求按日志恢复一致状态，不会理解哪条业务操作是误操作。要回到误操作之前，需要可用的[备份与历史恢复材料](backups-and-point-in-time-recovery.md)，并选择正确恢复目标。

同样，复制错误数据的副本、应用版本回退和业务补偿，处理的状态范围不同。检查恢复方案时分别问：物理文件能否恢复、需要哪个业务时间点、数据库之外的动作怎样核对、恢复后的应用是否兼容。

## 自检与证据边界

其他写入组织可对照 [LSM、SSTable 与压缩合并](lsm-sstables-and-compaction.md)，区分 WAL、内存表、Flush 和合并；新文的键值模型不改变本文 PostgreSQL 的适用范围，也没有新增崩溃实验。

为什么提交成功不要求所有数据页都同步写完？WAL 先写是否意味着副本已可读？数据库能够重启，为何仍不能证明误删除可以找回？

本文按 PostgreSQL 18 一手资料核查，流程与检查点情形为教学推演。配套[备份恢复实验](backup-recovery-lab.md)实际验证基础备份与命名 WAL 恢复点，没有实施崩溃、[进程](../../glossary/systems.md#systems.execution-units)强杀或断电测试，也没有测量异步提交的数据丢失窗口。

核查日期：2026-10-19。继续读[备份与时间点恢复](backups-and-point-in-time-recovery.md)和[数据库迁移兼容](schema-migrations-and-compatibility.md)，把本机耐久性、历史恢复和应用数据契约分开设计。
