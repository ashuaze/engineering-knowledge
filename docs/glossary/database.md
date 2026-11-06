<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# 数据库与存储词汇表

本页解释 24 组术语，按[完整术语索引](../glossary.md#database)中的顺序排列。示例为说明性场景；具体技术版本与验证范围见各条深入阅读。

[分类词汇表](index.md) · [数据库与存储文章](../knowledge/database/index.md)

## 本页术语

- [RDBMS / NoSQL](#database.db-models)
- [OLTP / OLAP](#database.workloads)
- [ACID](#database.acid)
- [Transaction / Isolation Level](#database.isolation)
- [Dirty / Non-repeatable / Phantom Read](#database.anomalies)
- [MVCC](#database.mvcc)
- [Optimistic / Pessimistic Lock](#database.locking)
- [Index / Covering Index](#database.indexes)
- [Query Plan / EXPLAIN](#database.plans)
- [WAL / Redo / Undo](#database.recovery-log)
- [LSM / SSTable / Compaction](#database.lsm)
- [Normalization / Denormalization](#database.normalization)
- [Replication / Read Replica](#database.replication)
- [Partitioning / Sharding](#database.partitioning)
- [Prepared Statement](#database.prepared)
- [Schema Migration / CDC](#database.migration)
- [Unique Constraint / Foreign Key](#database.constraints)
- [Write Skew](#database.write-skew)
- [Selectivity / Row Estimate](#database.selectivity)
- [Logical Backup / Physical Backup / PITR](#database.backups)
- [Checkpoint / WAL Flush](#database.checkpoints)
- [Functional Dependency](#database.functional-dependency)
- [Shard Key](#database.shard-key)
- [Partition Pruning](#database.partition-pruning)

<a id="database.db-models"></a>

## RDBMS / NoSQL

**ID：** `database.db-models` · **建议优先级：** P0

**别名 / 检索词：** RDBMS、NoSQL、关系数据库、非关系数据库

**简释：** 关系模型及多种非关系数据模型。

RDBMS 围绕关系、约束和查询组织数据；NoSQL 是键值、文档、图等多种模型的统称。是否支持事务、索引或分布式能力应按具体产品和配置判断。

**例子：** 文档数据库适合某种聚合读取，并不意味着无需模式或数据约束。

**深入阅读：** [数据模型与访问模式：先确定怎样读写，再决定怎样存](../knowledge/database/data-models-and-access-patterns.md)

<a id="database.workloads"></a>

## OLTP / OLAP

**ID：** `database.workloads` · **建议优先级：** P0

**别名 / 检索词：** OLTP、OLAP、在线事务、在线分析

**简释：** 在线事务与分析型访问模式。

OLTP 侧重较短、较频繁的事务操作，OLAP 侧重跨大量数据的分析。二者是负载特征，可在同一业务中并存，需按扫描、更新和时效需求设计。

**例子：** 下单属于事务路径，按月汇总销售趋势属于分析路径。

**深入阅读：** [数据模型与访问模式：先确定怎样读写，再决定怎样存](../knowledge/database/data-models-and-access-patterns.md)

<a id="database.acid"></a>

## ACID

**ID：** `database.acid` · **建议优先级：** P0

**别名 / 检索词：** ACID、事务特性

**简释：** 事务原子性、约束一致性、隔离性和持久性。

ACID 分别指原子性、一致性、隔离性和持久性。一致性依赖已表达的业务约束，隔离级别和持久化配置决定具体保证，不表示自动解决全部分布式一致性。

**例子：** 事务整体提交仍可能遗漏未编码的跨记录业务规则。

**深入阅读：** [事务隔离与 MVCC：同一事务到底能看到什么](../knowledge/database/isolation-and-mvcc.md)

<a id="database.isolation"></a>

## Transaction / Isolation Level

**ID：** `database.isolation` · **建议优先级：** P0

**别名 / 检索词：** Transaction、Isolation Level、事务隔离、隔离级别、数据库事务

**简释：** 事务边界及并发可见性保证。

事务定义一组操作的提交边界，隔离级别限定与并发事务的可见性及异常。级别名称相同也应核对数据库实现、快照时点和冲突处理。

**例子：** 同一事务两次查询能否看到新提交记录，要按实际隔离级别判断。

**深入阅读：** [库存并发：两个成功事务为何仍可能超卖](../knowledge/database/concurrent-inventory.md) · [事务隔离与 MVCC：同一事务到底能看到什么](../knowledge/database/isolation-and-mvcc.md) · [实验：验证库存并发、回滚与锁失败](../knowledge/database/inventory-concurrency-lab.md) · [数据模型与访问模式：先确定怎样读写，再决定怎样存](../knowledge/database/data-models-and-access-patterns.md)

<a id="database.anomalies"></a>

## Dirty / Non-repeatable / Phantom Read

**ID：** `database.anomalies` · **建议优先级：** P0

**别名 / 检索词：** Dirty、Non-repeatable、Phantom Read、脏读、不可重复读、幻读

**简释：** 读取未提交数据、重复读取变化和结果集变化。

脏读读取尚未提交的数据，不可重复读指同一记录重读变化，幻读涉及条件查询结果集变化。避免这些命名异常仍不一定满足所有业务串行化要求。

**例子：** 两次按条件查询出现新增行，应结合隔离实现分析，而非仅看行锁数量。

**深入阅读：** [事务隔离与 MVCC：同一事务到底能看到什么](../knowledge/database/isolation-and-mvcc.md)

<a id="database.mvcc"></a>

## MVCC

**ID：** `database.mvcc` · **建议优先级：** P0

**别名 / 检索词：** MVCC、多版本并发控制

**简释：** 用数据版本协调读写并发。

MVCC 为数据维护多个可见版本，读者按快照规则选择版本。它减少部分读写阻塞，但仍有写写冲突、版本回收成本与隔离边界。

**例子：** 长事务持有旧快照，可能使旧版本迟迟不能清理。

**深入阅读：** [事务隔离与 MVCC：同一事务到底能看到什么](../knowledge/database/isolation-and-mvcc.md) · [CDC：快照、变更位置与重放怎样接成连续的数据流](../knowledge/database/cdc-snapshots-log-positions-and-replay.md)

<a id="database.locking"></a>

## Optimistic / Pessimistic Lock

**ID：** `database.locking` · **建议优先级：** P0

**别名 / 检索词：** Optimistic、Pessimistic Lock、乐观锁、悲观锁

**简释：** 检测冲突后处理与提前限制竞争。

乐观策略在提交更新时检验版本等冲突条件，悲观策略提前获取锁以约束竞争。两者都需处理失败与重试，锁范围也必须覆盖业务不变量。

**例子：** 库存更新带版本条件，未更新到行时重新读取或报告冲突。

**深入阅读：** [库存并发：两个成功事务为何仍可能超卖](../knowledge/database/concurrent-inventory.md) · [锁与同步原语：保护范围比加锁动作更重要](../knowledge/systems/locks-and-synchronization.md) · [死锁与失败恢复：等待为什么无法自行结束](../knowledge/systems/deadlocks-and-recovery.md) · [实验：验证库存并发、回滚与锁失败](../knowledge/database/inventory-concurrency-lab.md)

<a id="database.indexes"></a>

## Index / Covering Index

**ID：** `database.indexes` · **建议优先级：** P0

**别名 / 检索词：** Index、Covering Index、覆盖索引、数据库索引

**简释：** 缩小访问范围及从索引满足查询。

索引用额外结构加快某些访问，覆盖索引包含查询所需信息。是否能避免回表还受可见性和引擎机制影响；索引也增加写入、空间和维护成本。

**例子：** 联合索引列序影响可用查询范围，不能只看查询字段都在索引里。

**深入阅读：** [索引与执行计划：为什么建了索引仍然扫描全表](../knowledge/database/indexes-and-query-plans.md) · [实验：观察 PostgreSQL 索引、扫描与回表](../knowledge/database/query-plans-lab.md) · [数据模型与访问模式：先确定怎样读写，再决定怎样存](../knowledge/database/data-models-and-access-patterns.md)

<a id="database.plans"></a>

## Query Plan / EXPLAIN

**ID：** `database.plans` · **建议优先级：** P0

**别名 / 检索词：** Query Plan、EXPLAIN、查询计划、执行计划

**简释：** 数据库执行路径、估算与实际执行信息。

执行计划描述扫描、连接、排序等算子及估算；实际分析可补充行数与耗时。带执行的分析会真正运行语句，读取计划时需区分累计、自身和循环次数。

**例子：** 估算只返回十行却实际返回百万行时，先检查数据分布和统计信息。

**深入阅读：** [索引与执行计划：为什么建了索引仍然扫描全表](../knowledge/database/indexes-and-query-plans.md) · [实验：观察 PostgreSQL 索引、扫描与回表](../knowledge/database/query-plans-lab.md)

<a id="database.recovery-log"></a>

## WAL / Redo / Undo

**ID：** `database.recovery-log` · **建议优先级：** P0

**别名 / 检索词：** WAL、Redo、Undo、预写日志

**简释：** 预写、重放与回滚相关日志机制，细节因引擎而异。

WAL 要求相关日志先于对应数据页持久化；Redo 用于重放，Undo 用于回滚或旧版本管理，具体机制依引擎而异。提交成功不意味着全部数据页已写回。

**例子：** 进程在提交后崩溃，恢复可根据持久日志重建尚未刷出的已提交变更。

**深入阅读：** [WAL 与崩溃恢复：提交后数据页为何还没写完](../knowledge/database/wal-and-crash-recovery.md) · [备份与时间点恢复：备份成功为何还不够](../knowledge/database/backups-and-point-in-time-recovery.md) · [实验：从基础备份恢复到指定恢复点](../knowledge/database/backup-recovery-lab.md) · [写穿与异步写回：写入成功究竟确认到了哪里](../knowledge/cache-search/write-through-write-behind-and-durability.md)

<a id="database.lsm"></a>

## LSM / SSTable / Compaction

**ID：** `database.lsm` · **建议优先级：** P1

**别名 / 检索词：** LSM、LSM Tree、Log-Structured Merge、SSTable、MemTable、Compaction、压缩合并、写放大

**简释：** 以内存积累、有序文件与后台合并组织键值更新，区分版本、删除及读写空间放大。

LSM 在内存中积累写入，刷成有序文件并通过合并整理版本。读放大、写放大和空间放大互相影响；删除标记需等安全条件满足后才可移除。

**例子：** 后台合并跟不上写入时，文件层数和读放大可能上升，最终触发写入停顿。

**深入阅读：** [LSM、SSTable 与压缩合并：写入返回后，后台为什么仍然忙](../knowledge/database/lsm-sstables-and-compaction.md)

<a id="database.normalization"></a>

## Normalization / Denormalization

**ID：** `database.normalization` · **建议优先级：** P0

**别名 / 检索词：** Normalization、Denormalization、范式、反范式

**简释：** 减少冗余与按访问需求引入冗余。

规范化围绕依赖关系减少冗余和更新异常；反规范化为访问需求保留派生或重复数据。引入冗余后要明确唯一事实来源、更新方式与修复路径。

**例子：** 在订单中保存成交时商品名是历史快照需求，不能简单随商品现名覆盖。

**深入阅读：** [数据模型与访问模式：先确定怎样读写，再决定怎样存](../knowledge/database/data-models-and-access-patterns.md)

<a id="database.replication"></a>

## Replication / Read Replica

**ID：** `database.replication` · **建议优先级：** P0

**别名 / 检索词：** Replication、Read Replica、数据库复制、只读副本

**简释：** 复制状态并提供副本读取。

复制传播状态，只读副本可承担查询；接收、落盘、回放和查询快照是不同阶段。同步确认仅覆盖约定副本和阶段，旧快照不自动更新，复制也不替代独立历史备份及安全切主。

**例子：** 用户刚写入主库就读落后副本，可能暂时看不到刚提交的记录。

**深入阅读：** [一致性与复制：写入成功后为什么仍可能读到旧值](../knowledge/distributed/consistency-and-replication.md)

<a id="database.partitioning"></a>

## Partitioning / Sharding

**ID：** `database.partitioning` · **建议优先级：** P0

**别名 / 检索词：** Partitioning、Sharding、分区、分片

**简释：** 在逻辑或节点间拆分数据。

分区把数据按规则拆成片段，分片通常还涉及跨节点分布。路由键影响热点、跨片查询、唯一约束及迁移成本；拆分不自动解决容量倾斜。

**例子：** 按租户分片便于租户内访问，但超大租户仍可能成为单片热点。

**深入阅读：** [分区、分片与数据路由：一次查询需要访问哪些数据](../knowledge/database/partitioning-sharding-and-data-routing.md)

<a id="database.prepared"></a>

## Prepared Statement

**ID：** `database.prepared` · **建议优先级：** P0

**别名 / 检索词：** Prepared Statement、预处理语句

**简释：** 参数化执行与可能的计划复用，依驱动和数据库而异。

预处理语句把语句准备与参数执行分开，可能复用解析或计划。服务端准备、驱动模拟及计划选择依实现而异，参数化也不自动保证最优计划。

**例子：** 同一查询模板对极少见值与热门值执行时，合适的访问路径可能不同。

**深入阅读：** [SQL 注入与参数化查询：值怎样与查询结构分开](../knowledge/security/sql-injection-parameters-and-query-structure.md)

<a id="database.migration"></a>

## Schema Migration / CDC

**ID：** `database.migration` · **建议优先级：** P0

**别名 / 检索词：** Schema Migration、CDC、模式迁移、变更数据捕获

**简释：** 结构演进与数据变更捕获。

Schema Migration 修改结构与约束；CDC 捕获数据变化，常用于同步或迁移。在线演进需兼容同时存在的新旧应用，回填完成也需验证增量追平。

**例子：** 先添加兼容字段，再迁移读写，最后在旧版本退出后删除旧字段。

**深入阅读：** [数据库迁移兼容：回退代码为什么救不回数据](../knowledge/database/schema-migrations-and-compatibility.md) · [索引重建、增量追赶与切换：怎样覆盖期间的新增和删除](../knowledge/cache-search/index-rebuild-watermarks-and-cutover.md) · [CDC：快照、变更位置与重放怎样接成连续的数据流](../knowledge/database/cdc-snapshots-log-positions-and-replay.md)

<a id="database.constraints"></a>

## Unique Constraint / Foreign Key

**ID：** `database.constraints` · **建议优先级：** P0

**别名 / 检索词：** Unique Constraint、Foreign Key、唯一约束、外键

**简释：** 由数据库维护唯一性和引用关系。

唯一约束在数据库中防止重复键值，外键维护引用关系。NULL、延迟检查及跨分区支持依实现而异；应用先查再写不能替代并发下的约束。

**例子：** 创建订单号时使用唯一约束，并把并发冲突转换为明确业务结果。

**深入阅读：** [幂等性：给重复请求一个稳定的业务结果](../knowledge/api/idempotency.md) · [库存并发：两个成功事务为何仍可能超卖](../knowledge/database/concurrent-inventory.md) · [实验：验证库存并发、回滚与锁失败](../knowledge/database/inventory-concurrency-lab.md) · [Webhook 签名与重放：验签成功，为什么还不能直接执行业务](../knowledge/api/webhook-signatures-replay-and-delivery.md) · [数据模型与访问模式：先确定怎样读写，再决定怎样存](../knowledge/database/data-models-and-access-patterns.md)

<a id="database.write-skew"></a>

## Write Skew

**ID：** `database.write-skew` · **建议优先级：** P1

**别名 / 检索词：** Write Skew、写偏斜

**简释：** 并发事务依据各自快照做出相关判断、更新不同记录，合并结果可能违反跨记录约束的异常。

写偏斜中，事务依据相同或相关快照判断后分别更新不同记录，合并结果破坏共同规则。单行更新原子或避免写同一行并不足以防止这种异常。

**例子：** 两名值班医生分别看到对方在岗并同时离岗，最终无人值班。

**深入阅读：** [事务隔离与 MVCC：同一事务到底能看到什么](../knowledge/database/isolation-and-mvcc.md)

<a id="database.selectivity"></a>

## Selectivity / Row Estimate

**ID：** `database.selectivity` · **建议优先级：** P1

**别名 / 检索词：** Selectivity、Row Estimate、选择率、行数估计

**简释：** 条件匹配比例与计划节点预计输出行数，用于分析访问路径和估计误差。

选择性描述条件匹配的数据比例，行数估计预测算子输出规模。数据倾斜、列相关性和统计过期可造成误差，进而影响连接顺序和访问路径。

**例子：** 城市与邮编高度相关时，独立估计可能低估组合条件的匹配行数。

**深入阅读：** [索引与执行计划：为什么建了索引仍然扫描全表](../knowledge/database/indexes-and-query-plans.md)

<a id="database.backups"></a>

## Logical Backup / Physical Backup / PITR

**ID：** `database.backups` · **建议优先级：** P0

**别名 / 检索词：** Logical Backup、Physical Backup、PITR、逻辑备份、物理备份、时间点恢复

**简释：** 按对象或集群保存恢复材料，并用基础备份与连续日志到达所选历史边界。

逻辑备份保存对象与数据的逻辑表示，物理备份保存恢复所需的数据文件状态。PITR 依靠可用基础备份和连续日志恢复到选定边界，必须通过实际恢复验证。

**例子：** 基础备份存在但中间 WAL 缺失时，不能保证到达目标恢复点。

**深入阅读：** [备份与时间点恢复：备份成功为何还不够](../knowledge/database/backups-and-point-in-time-recovery.md) · [实验：从基础备份恢复到指定恢复点](../knowledge/database/backup-recovery-lab.md)

<a id="database.checkpoints"></a>

## Checkpoint / WAL Flush

**ID：** `database.checkpoints` · **建议优先级：** P1

**别名 / 检索词：** Checkpoint、WAL Flush、检查点、日志持久化

**简释：** 区分日志持久化、数据页写回与恢复起点，不把提交确认当作所有页已同步写回。

Checkpoint 推进恢复可从何处开始，WAL Flush 把日志推进到持久边界；数据页写回是相关但不同的动作。各系统的确认和刷盘策略需分别核对。

**例子：** 提交日志已持久化而数据页仍在内存，并不必然违反 WAL 恢复机制。

**深入阅读：** [WAL 与崩溃恢复：提交后数据页为何还没写完](../knowledge/database/wal-and-crash-recovery.md)

<a id="database.functional-dependency"></a>

## Functional Dependency

**ID：** `database.functional-dependency` · **建议优先级：** P1

**别名 / 检索词：** Functional Dependency、函数依赖

**简释：** 关系中的 X→Y 要求所有合法状态中，任意两行的 X 值相同就有相同的 Y 值。

函数依赖表达业务语义对合法关系状态的约束，不能由少量样本碰巧满足推导成立。规范化可按依赖识别重复当前事实并设计分解；决定字段是否相同事实时还要包括时间语义。

**例子：** customer_id 可以决定同一状态下的客户当前地址，但不能决定所有订单各自的下单时地址快照；同一客户在不同订单中可以有不同历史快照。

**深入阅读：** [数据模型与访问模式：先确定怎样读写，再决定怎样存](../knowledge/database/data-models-and-access-patterns.md)

<a id="database.shard-key"></a>

## Shard Key

**ID：** `database.shard-key` · **建议优先级：** P1

**别名 / 检索词：** Shard Key、分片键

**简释：** 参与数据放置及目标选择的字段组合，其分布和查询使用方式影响热点、扇出与跨片约束。

分片键通过范围、哈希或目录等放置规则关联到数据归属，路由器还需要有效的归属元数据。选键需同时检查不同值数量、重复频率、单调写入及常见查询条件。主键、索引、分片键和权限条件可使用相同字段但职责不同；拥有路由字段不能代替授权，高基数也不保证负载均匀。

**例子：** 按 tenant_id 放置后，包含该租户条件的查询可能缩小目标，但一个占70%请求的租户仍可能集中在单片；仅带 order_id 的查询不一定知道目标片。

**深入阅读：** [分区、分片与数据路由：一次查询需要访问哪些数据](../knowledge/database/partitioning-sharding-and-data-routing.md)

<a id="database.partition-pruning"></a>

## Partition Pruning

**ID：** `database.partition-pruning` · **建议优先级：** P1

**别名 / 检索词：** Partition Pruning、分区裁剪

**简释：** 根据查询条件和分区边界，排除不可能包含匹配数据的分区，再在留下的范围内选择访问路径。

分区裁剪先减少需要访问的数据单元，索引则影响剩余单元内部怎样查找。PostgreSQL 18 的声明式分区裁剪使用分区键隐含的边界约束，不依赖索引存在，且可发生在计划或执行阶段。谓词、参数可知时间和产品优化器规则影响能否裁剪；不能仅凭 WHERE 出现分区列就保证任意表达式可裁剪。

**例子：** P0=[0,100)、P1=[100,200)、P2=[200,300) 时，100≤k<200 只需P1；90≤k<210 则三者都不能排除。留下P1也不代表一定使用索引扫描。

**深入阅读：** [分区、分片与数据路由：一次查询需要访问哪些数据](../knowledge/database/partitioning-sharding-and-data-routing.md)

## 资料与延伸

下列资料提供相关机制的进一步说明，并不表示覆盖本页所有术语。各条已关联的专题文章另列具体来源、适用版本与验证边界。

- [PostgreSQL：并发控制](https://www.postgresql.org/docs/18/mvcc.html)
- [PostgreSQL：备份与恢复](https://www.postgresql.org/docs/18/backup.html)
- [PostgreSQL18：PREPARE 与通用/定制计划](https://www.postgresql.org/docs/18/sql-prepare.html)
- [Database System Concepts 第7版：函数依赖、键与规范化](https://www.db-book.com/slides-dir/PDF-dir/ch7.pdf)
- [PostgreSQL18：主键、唯一约束、外键与检查范围](https://www.postgresql.org/docs/18/ddl-constraints.html)
- [MongoDB8.0：嵌入、引用与重复数据含义](https://www.mongodb.com/docs/v8.0/data-modeling/best-practices/)
- [DynamoDB：先列访问模式再设计键](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-modeling-nosql.html)
- [DuckDB2.0：工作负载与执行目标](https://duckdb.org/docs/2.0/guides/performance/how_to_tune_workloads)
- [PostgreSQL 18：Table Partitioning](https://www.postgresql.org/docs/18/ddl-partitioning.html)
- [MongoDB 8.0：Choose a Shard Key](https://www.mongodb.com/docs/v8.0/core/sharding-choose-a-shard-key/)
- [MongoDB 8.0：Routing with mongos](https://www.mongodb.com/docs/v8.0/core/sharded-cluster-query-router/)
- [MongoDB 8.0：Shard Keys and Unique Indexes](https://www.mongodb.com/docs/v8.0/core/sharding-shard-key/)
- [MongoDB 8.0：Transactions](https://www.mongodb.com/docs/v8.0/core/transactions/)
- [MongoDB 8.0：Sharded Cluster Balancer](https://www.mongodb.com/docs/v8.0/core/sharding-balancer-administration/)
- [PostgreSQL18：Logical Decoding Concepts](https://www.postgresql.org/docs/18/logicaldecoding-explanation.html)
- [PostgreSQL18：Streaming Replication Protocol](https://www.postgresql.org/docs/18/protocol-replication.html)
- [PostgreSQL18：SET TRANSACTION SNAPSHOT](https://www.postgresql.org/docs/18/sql-set-transaction.html)
- [PostgreSQL18：Logical Decoding Output Plugins](https://www.postgresql.org/docs/18/logicaldecoding-output-plugin.html)
- [PostgreSQL18：Logical Replication Restrictions](https://www.postgresql.org/docs/18/logical-replication-restrictions.html)
- [PostgreSQL18：pg_replication_slots](https://www.postgresql.org/docs/18/view-pg-replication-slots.html)
- [Debezium3.3 PostgreSQL：快照、事件、事务与恢复](https://debezium.io/documentation/reference/3.3/connectors/postgresql.html)
- [Jepsen 的线性一致性定义](https://jepsen.io/consistency/models/linearizable)
- [PostgreSQL 18 复制文档](https://www.postgresql.org/docs/18/warm-standby.html)
- [DynamoDB 读取一致性说明](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.ReadConsistency.html)
- [PostgreSQL18 Hot Standby](https://www.postgresql.org/docs/18/hot-standby.html)

[返回分类词汇表](index.md) · [完整术语索引](../glossary.md)
