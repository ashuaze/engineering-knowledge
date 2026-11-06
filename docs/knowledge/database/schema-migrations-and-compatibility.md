---
id: "kb-database-schema-migrations"
title: "数据库迁移兼容：回退代码为什么救不回数据"
kind: "concept"
domain: "database"
status: "evolving"
summary: "从混合版本的读写契约安排扩展、回填、切换与收缩，识别锁成本和不可逆边界。"
created: "2026-10-19"
updated: "2026-10-23"
last_verified: "2026-10-19"
verification: "source-checked"
prerequisites: ["kb-devops-delivery-lifecycle"]
related: ["kb-database-backups-pitr", "kb-database-wal-recovery", "kb-database-recovery-lab", "kb-systems-deadlocks-recovery", "kb-api-contracts-pagination", "kb-engineering-test-scopes", "kb-database-partitioning-sharding", "kb-database-cdc"]
tags: ["schema", "migrations", "compatibility"]
---

# 数据库迁移兼容：回退代码为什么救不回数据

新版本把某个字段删掉后，即使回退应用[镜像](../../glossary/devops.md#devops.containers)，旧程序也可能继续报错。数据库结构、已写入的数据和在线消费者都有自己的演进状态，不能把它们视为随应用制品一起倒退。

前置知识：[构建、部署与回滚](../devops/build-deploy-rollback.md)。本文讨论[关系数据库](../../glossary/database.md#database.db-models)迁移的兼容设计，以 PostgreSQL 18 DDL 为机制参照。示例是教学方案，未执行结构变更、批量回填或混合版本部署实验。

## 迁移首先改变读写契约

[Schema migration](../../glossary/database.md#database.migration) 不只是一段 ALTER TABLE。字段的存在、类型、约束、默认值和业务含义都会约束读者与写者。参与者还可能包括后台任务、离线报表、消息消费者与旧客户端，不能只检查正在放量的新接口。

先为每个参与者记录“能读什么、会写什么、是否仍在线”。再问两件事：新结构是否仍接受旧写法，旧读者是否能解释新写入的数据。兼容是具体方向的关系，不是“新版本已上线”的附赠属性。

## 用扩展、回填和收缩组织变更

教学目标：原来以 display_name 保存名称，希望转到 full_name；这里不涉及名称拆分或格式转换，两个字段在过渡期代表同一业务值。

| 阶段 | 数据与结构 | 参与者要求 |
| --- | --- | --- |
| 扩展 | 保留旧字段，增加允许过渡状态的新字段 | 旧程序仍可按原契约工作 |
| 准备 | 部署理解两种状态的代码，明确权威值与同步协议 | 所有写入口遵守同一过渡规则 |
| 回填 | 把旧数据补入新字段，并处理期间的[并发](../../glossary/systems.md#systems.concurrency)修改 | 可分批、[重试](../../glossary/api.md#api.retries)、核对进度；旧值不能覆盖较新的值 |
| 切换 | 在验证后启用新读写路径，保留约定回退窗口 | 仍存在的旧读者/写者必须兼容或已退出 |
| 收缩 | 清理旧字段与过渡代码 | 已确认所有依赖退出，明确不可直接回退的版本 |

这是针对本教学模型的建议，不是某个迁移框架的自动保证。准备和启用分阶段的思路可参照 [AWS 的回滚安全说明](https://aws.amazon.com/builders-library/ensuring-rollback-safety-during-deployments/)。

“新字段为空就读旧字段”也必须与写入协议配合。如果旧版本只更新旧列，而新版本优先读已有的新列，就可能读到陈旧名称。可以分阶段[延迟](../../glossary/performance.md#performance.latency-throughput)新列成为权威，或设计覆盖所有写入口的兼容同步机制；没有具体协议时，不能仅凭“双读双写”四个字宣布兼容完成。

## 回填也会遇到并发与失败

后台先读旧值、用户随后更新、后台再写回旧值，可能覆盖更晚修改。回填应围绕主键范围、版本或条件更新设计，并说明失败后从哪里继续。断点只说明扫描进度，不单独证明所有记录都满足目标[不变量](../../glossary/systems.md#systems.atomicity)。

下面是未执行的流程伪代码，不是可直接运行的迁移脚本：

```text
选择一批候选主键与对应版本
按已定义的权威数据转换
仅当版本/过渡条件仍成立时写入
记录完成与冲突；冲突重新读取或交给后续处理
核对目标字段与业务规则，再推进下一批
```

回填批次还会占用事务、锁、I/O 并产生日志。需要观察与停止条件，而不是只看后台任务是否仍活着。这里的版本字段和条件只是协议形状，具体 SQL 要按数据模型和隔离规则验证。

## DDL 的执行成本需要单独核对

同样叫 ALTER TABLE，不同子命令的锁、扫描和重写成本可能不同。新增约束还需要考虑历史数据是否满足，以及验证期间的并发行为；类型转换也可能改变表示和业务含义。机制依据见 [PostgreSQL 表结构变更](https://www.postgresql.org/docs/18/ddl-alter.html)。

“语句很短”“空表上执行很快”或“数据库支持事务性 DDL”，都不能证明在目标大表上没有[阻塞](../../glossary/systems.md#systems.blocking)。上线前应核对具体版本、语句、数据规模、长事务、锁等待和工具事务边界，必要时在代表性环境演练。[锁与死锁](../systems/deadlocks-and-recovery.md)帮助分析等待，不能代替对该 DDL 的实测。

同理，批量修改的日志量和副本负担需要与[WAL](wal-and-crash-recovery.md)及[复制](../distributed/consistency-and-replication.md)一起考虑。不要把一次本地小表变更的毫秒数直接用作生产放量依据。

## 回退、恢复备份与向前修复

| 选择 | 改变的对象 | 需要先回答 |
| --- | --- | --- |
| 回退应用 | 应用制品与相关配置 | 旧程序还能处理当前结构和数据吗？ |
| 执行逆向迁移 | 结构或数据表示 | 新信息能否无损转换，当前写入如何处理？ |
| 恢复历史备份 | 恢复范围内的数据库状态 | 会丢掉哪些后来正确的修改，外部动作如何核对？ |
| 向前修复 | 以新变更解决当前错误 | 怎样限制继续影响并验证修复？ |

删除旧字段时已经丢掉的信息，不会因为执行一个同名 ADD COLUMN 就回来。逆向脚本能够执行，也不证明业务语义可逆。恢复旧数据库还可能使外部支付、消息和缓存与当前数据库不一致，需要额外核对和补偿流程。

因此每个阶段都应写清可回退到哪些版本、什么条件下停止、何时必须改走向前修复或历史恢复。配套[备份恢复实验](backup-recovery-lab.md)只验证指定本机行集的恢复，不验证这一整套迁移协议。

迁移跨越[分片](../../glossary/database.md#database.partitioning)边界时，还需联结[分片键](../../glossary/database.md#database.shard-key)、路由视图与写入归属，继续见[分区、分片与数据路由](partitioning-sharding-and-data-routing.md)。回填完成与入口切换仍需各自的证据。

从源端建立配对快照、保留日志并按事务/位置恢复，继续见[CDC](cdc-snapshots-log-positions-and-replay.md)。捕获到行变化不等于结构、目标约束或历史过滤范围已经迁移；源位置与目标持久完成仍分别核对。

## 自检与证据边界

自检：旧程序仍会写旧列，新程序开始优先读新列，什么时序会使它读到旧值？回填完成率为 100% 后，为什么还需要业务核对？删列后恢复列名是否等于恢复原数据？

核查日期：2026-10-19。本文的一手资料支持 PostgreSQL DDL 边界与分阶段兼容思路；名称字段、回填流程和选择表为教学设计。迁移框架、并发回填、DDL 锁耗时与真实版本回退均未执行实验。
