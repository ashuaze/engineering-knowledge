---
id: "kb-database-cdc"
title: "CDC：快照、变更位置与重放怎样接成连续的数据流"
kind: "concept"
domain: "database"
status: "evolving"
summary: "以 PostgreSQL 18 逻辑解码和 Debezium 3.3 说明快照与日志配对、事务与位点、删除载荷、重复处理及保留与恢复边界。"
created: "2026-10-23"
updated: "2026-10-23"
last_verified: "2026-10-23"
verification: "source-checked"
prerequisites: ["kb-database-wal-recovery", "kb-database-isolation-mvcc", "kb-messaging-delivery-semantics"]
related: ["kb-cache-search-index-cutover", "kb-database-schema-migrations", "kb-messaging-outbox", "kb-messaging-partitions-offsets", "kb-messaging-event-evolution", "kb-database-backups-pitr", "kb-security-secret-lifecycle"]
tags: ["cdc", "logical-decoding", "snapshot", "replication-slot", "replay"]
---

# CDC：快照、变更位置与重放怎样接成连续的数据流

学习入口：先把表复制出去，再启动订阅，为什么会永久漏掉中间一次删除？即使捕获器没有丢消息，目标汇总仍可能重复增加。[变更数据捕获](../../glossary/database.md#database.migration)（Change Data Capture，CDC）提供来源变化的持续输入；连续覆盖、事务边界、恢复位置和目标业务效果需要共同设计。

前置：[WAL 与恢复](wal-and-crash-recovery.md)、[隔离与快照](isolation-and-mvcc.md)、[消息确认](../messaging/delivery-acknowledgements-and-idempotency.md)。本文选 PostgreSQL 18 逻辑解码作为来源机制，以 Debezium 3.3 PostgreSQL 连接器说明事件形态。说明性流程不是部署教程，未启动数据库、连接器或 Kafka，也未执行故障实验。

## 先明确捕获的是哪一种事实

轮询当前表、触发器记录变化和日志型 CDC 是不同机制。轮询若只筛选 `updated_at`，要额外处理并发提交、时间精度、分页和删除；源表里已消失的行，不能单靠“再扫描一次当前值”还原删除事件。日志型也受保留范围、解码协议和订阅过滤限制，不是无限历史。

[PostgreSQL 18 逻辑解码](https://www.postgresql.org/docs/18/logicaldecoding-explanation.html)将 [WAL](../../glossary/database.md#database.recovery-log) 内部变化转换成消费者可解释的内容。物理 WAL、逻辑输出、连接器事件和目标业务操作有不同表示；行 `status` 由 pending 变 paid 不一定包含支付主体、业务原因或外部支付结果。业务事件可通过[Outbox](../messaging/transactional-outbox.md)显式表达，CDC 可以搬运它，但不会从任意表变化自动推断完整业务意图。

范围也要固定：哪个源实例与数据库、哪些表/字段、哪些租户、是否包括删除与截断、如何处理结构变化？改变过滤规则后，“从当前位置继续”不会补回过去未捕获的数据。需要另行补数据或建立新的覆盖边界，不能把新过滤配置当作历史已经完整。

## 快照要与后续变更流配对

全量快照回答某个一致读取视图中的当前状态，增量回答后续变化。以下先用教学日志位置 100、101、102 表示同一来源的有序已提交变化，不是 PostgreSQL LSN 的真实格式。

| 错误顺序 | 具体历史 | 结果 |
| --- | --- | --- |
| 扫完表后才建立增量起点 | 扫描时 x 存在；位置 101 删除 x；订阅从 102 之后开始 | x 在目标永久残留，101 未覆盖 |
| 每页各用新读取视图 | 扫完前半段后发生跨页修改或删除，再读后半段 | 得到混合时点，不能据此证明一个完整快照 |
| 快照与增量无序写同一目标 | 增量已删除 x，旧快照任务迟到写入 x | 已删数据复活 |

一种容易核对的方案是：建立与增量源配对的快照 S，保留所需日志；完整读取 S；再按源协议应用 S 之后的变化。示例令 S 对应位置 100，此时 x=7；之后 101 把 x 改为 8，102 删除 x。先装载 x=7，再应用 101、102，最终无 x；三步需要覆盖完整，没有要求它们在真实时间上同时执行。

PostgreSQL 18 [导出快照机制](https://www.postgresql.org/docs/18/logicaldecoding-explanation.html#LOGICALDECODING-EXPLANATION-EXPORTEDSNAPSHOT)提供具体衔接：通过流复制接口创建逻辑槽时可导出与该变更流配套的快照。它来自数据库协议，不能用“先记当前时间，再开始 SELECT”代替。

使用者还要守住接口生命周期。[复制协议](https://www.postgresql.org/docs/18/protocol-replication.html)分别返回 consistent_point 与 snapshot_name，导出标识的可用期受创建连接后续命令及关闭影响；[SET TRANSACTION SNAPSHOT](https://www.postgresql.org/docs/18/sql-set-transaction.html)要求在适当[隔离级别](../../glossary/database.md#database.isolation)、首次查询之前导入。任意复制一个旧 snapshot_name 字符串，或在每页重新建立默认读事务，都不能证明使用了同一视图。

这是 PostgreSQL 原生机制的说明，不声称所有连接器按完全相同的命令序列实现初始化。Debezium 3.3 的[初始快照流程](https://debezium.io/documentation/reference/3.3/connectors/postgresql.html#postgresql-snapshots)把读取视图、日志位置、逐行 READ 事件和快照完成进度配套管理；具体保证取决于所选模式与配置，不能把 `initial_only` 或不做快照的模式都当作“全量加持续增量”。

## 位置记录必须带着范围和事务语义

LSN 是源日志位置，Kafka offset 是某个 [topic](../../glossary/messaging.md#messaging.positions) partition 的位置，目标检查点是目标已完成工作的边界。三个数字相近也没有可直接相减的共同单位。位置还要绑定源实例/流身份和配置；重建槽、切换来源或恢复旧备份时，不得仅凭名字相同继续解释旧位置。

一项源事务可以修改多行、多张表。PostgreSQL 18 [普通输出回调](https://www.postgresql.org/docs/18/logicaldecoding-output-plugin.html#LOGICALDECODING-OUTPUT-PLUGIN-CALLBACKS)按提交次序解码已提交事务，并提供 begin/change/commit；支持大事务流式处理或两阶段事务的插件另有未提交片段及结束/中止回调。消费者不能看见任意一条 row 消息就立刻认定事务已经成功。

如果目标承诺保留一笔源事务的共同可见性，就要识别事务、暂存必要变化、在源提交确定后按目标能力共同发布。若拆到多条消息、目标的不同[消息分区](../messaging/partitions-consumer-groups-and-offsets.md)并立即写入，源事务[原子性](../../glossary/systems.md#systems.atomicity)并不会自动传过去；有意接受中间状态时也要明说。Debezium 的[事务元数据](https://debezium.io/documentation/reference/3.3/connectors/postgresql.html#postgresql-transaction-metadata)提供相关信息，是否开启、何时能取得和怎样使用均需配置与目标协议，不能仅凭“有 transaction 字段”宣称端到端原子。

同一个 LSN 还不能笼统当作任意连接器中每条行事件的唯一 ID。事务内可能有多条记录，快照 READ 也有自己的阶段与定位；去重身份须按实际事件封装区分来源、事务内位置、键及阶段。随机生成的新 [UUID](../../glossary/distributed.md#distributed.uuid) 只会让同一条重放变成另一身份，不能解决重复。

## 旧值、键、删除和结构并非总是齐全

捕获器是否能提供删除或更新前的完整行，取决于源端 replica identity、插件、列类型及连接器约定。PostgreSQL 的[逻辑复制限制](https://www.postgresql.org/docs/18/logical-replication-restrictions.html)和 Debezium 3.3 的 replica identity / 更新章节分别限定这些内容；不能把“有 before 字段”理解成所有历史字段都有值。

目标至少需要稳定地定位受影响的对象。主键变化也不是普通非键字段更新，应处理旧键与新键；无键表、未变化的大值、过滤字段以及序列/DDL 的传播都须按所用协议核对。结构兼容和目标表建模另见[数据库迁移](schema-migrations-and-compatibility.md)，不能把自动行复制当作完整模式迁移。

Debezium 的[删除事件与 tombstone](https://debezium.io/documentation/reference/3.3/connectors/postgresql.html#postgresql-delete-events)还要区分：delete 事件描述源行删除；配置为发送 tombstone 时，随后可有同键、空 value 的 Kafka 记录，以服务日志压缩。空值 tombstone 不是包含所有删除前字段的业务事件，也不是“目标数据库已经删除成功”的确认。目标仍须执行并记录自己的删除结果。

## 重放安全依赖目标与进度共同恢复

PostgreSQL 逻辑槽在故障恢复后可能重发近期变化；连接器也有自己的记录与提交窗口。不能从正常时一次输出推断故障后[恰好一次](../../glossary/messaging.md#messaging.exactly-once)。纸面例：目标统计总数初始为 10，事件 e 使它加 5；目标写成 15，消费者尚未保存 e 的进度便退出；重放后又加一次，变成 20。

| 接受方式 | 需要守住的恢复条件 |
| --- | --- |
| 在同一目标事务内写入投影与已处理事件身份 | 两者共同提交；重复身份不再次产生效果 |
| 以源端可比较版本覆盖完整对象状态 | 同一对象按协议拒绝旧版本；相同版本载荷须一致；删除也纳入版本规则 |
| 调用目标事务之外的支付、邮件或远程 API | 使用对方支持的[幂等](../../glossary/api.md#api.idempotency)/结果查询或业务补偿；本地检查点不覆盖外部接受点 |

先确认进度后写目标，会在崩溃时永久跳过变化；先写目标后确认进度，允许重放但需安全重复。所谓 exactly-once 必须点名哪两处状态共同提交、失败时怎样恢复。位点“已接收”尤其不能自动解释为目标持久完成或可查询，见[索引重建的连续应用水位](../cache-search/index-rebuild-watermarks-and-cutover.md)。

## 保留预算决定能否继续恢复

逻辑槽帮助保留所需来源材料，也会占用 WAL 与目录版本资源。PostgreSQL 18 [`pg_replication_slots`](https://www.postgresql.org/docs/18/view-pg-replication-slots.html)区分 restart_lsn、confirmed_flush_lsn 与 WAL 可用状态；确认接收的位置不是目标完成证明，保留上限和其他失效条件也可能使槽不可用。看到槽名存在，不等于它能从任意旧位置重放。

假设积压新增速率恒为 20 MiB/s，消费完全停止 600 秒，不考虑压缩、段粒度或其他保留因素，仅这段新增就有 `20×600=12000 MiB`，约 11.72 GiB。它是教学预算，不是产品容量结论；实际需同时观察来源增长、可用磁盘、事务跨度、保留限制和恢复追赶能力。

如果所需日志已丢失，不能把检查点改到最新位置后宣布无损恢复。需要重新建立与增量配对的快照、核对覆盖并重建或协调目标；来源切换还需验证槽同步、来源身份与旧主隔离，不能只改连接地址。CDC 捕获器不是独立历史备份，恢复链另见[备份与 PITR](backups-and-point-in-time-recovery.md)。

## 五道自检与核查范围

1. 行变更、物理 WAL、业务事件各包含什么？为什么只轮询更新时间或改变表过滤规则不能保证历史完整？
2. S=100、更新 101、删除 102 的例子怎样衔接？导出快照标识为什么不能脱离连接生命周期与导入条件使用？
3. 源事务原子性、LSN、[消息分区偏移](../messaging/partitions-consumer-groups-and-offsets.md)、目标检查点分别属于哪里？为何一条 row 或一个相同 LSN 不能当作全部提交/去重依据？
4. before、主键变更、delete 与空值 tombstone 分别需要怎样解释？它们是否证明目标已完成删除？
5. 加 5 的重放为何会变成 20？怎样保护目标与进度，停 600 秒的理想积压是多少，所需日志丢失又怎样恢复覆盖？

核查日期：2026-10-23。实际读取 PostgreSQL 18 的逻辑槽/导出快照、复制协议、SET TRANSACTION SNAPSHOT、普通及流式输出回调、复制限制与槽状态；Debezium 3.3 PostgreSQL 页的快照、事务元数据、事件/键/replica identity、删除/tombstone 与故障重发相关段。文档按明确版本及核查日文本限定，不从 stable/newest 页面推定所有配置一致。100/101/102、重复加 5 与 12000 MiB 都是纸面模型，未创建复制槽、快照、解码器或连接器，未执行删除/DDL、[故障切换](../../glossary/reliability.md#reliability.dr)、重放或容量实验。
