<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# 数据库与存储

建议优先级：P0。目标：围绕数据约束、访问路径和恢复理解数据库。

下方术语用于知识索引。建议从[实际工程问题](../../problems.md)或本页核心问题进入，结合已有正文理解机制、适用边界与相关概念。

## 一个核心问题

同一业务约束在并发下为何可能被两个成功事务破坏？

## 已有正文

- [实验：从基础备份恢复到指定恢复点](backup-recovery-lab.md)：在独立 PostgreSQL 18.0 集群制作基础备份、归档 [WAL](../../glossary/database.md#database.recovery-log)，并实际重放到命名恢复点核对行集。
- [备份与时间点恢复：备份成功为何还不够](backups-and-point-in-time-recovery.md)：区分逻辑与[物理备份](../../glossary/database.md#database.backups)、归档链和恢复目标，用数据验收说明可恢复性的证据。
- [CDC：快照、变更位置与重放怎样接成连续的数据流](cdc-snapshots-log-positions-and-replay.md)：以 PostgreSQL 18 逻辑解码和 Debezium 3.3 说明快照与日志配对、事务与位点、删除载荷、重复处理及保留与恢复边界。
- [库存并发：两个成功事务为何仍可能超卖](concurrent-inventory.md)：从陈旧读取和单行条件更新理解[事务隔离](../../glossary/database.md#database.isolation)、数据库约束与[业务不变量](../../glossary/architecture.md#architecture.domain-model)的分工。
- [数据模型与访问模式：先确定怎样读写，再决定怎样存](data-models-and-access-patterns.md)：以客户与订单为例，区分模型、存储、索引和分布，说明[函数依赖](../../glossary/database.md#database.functional-dependency)、约束、历史快照与复制维护，并从事务和分析访问反推设计。
- [索引与执行计划：为什么建了索引仍然扫描全表](indexes-and-query-plans.md)：以 PostgreSQL 18 的 [B-tree](../../glossary/algorithms.md#algorithms.b-tree) 查询解释访问路径、[行数估计](../../glossary/database.md#database.selectivity)、联合索引与 [EXPLAIN](../../glossary/database.md#database.plans) 的证据边界。
- [实验：验证库存并发、回滚与锁失败](inventory-concurrency-lab.md)：用两个真实 PostgreSQL 会话与观察会话，执行七类库存、[死锁](../../glossary/systems.md#systems.race-deadlock)和锁超时场景各三次。
- [事务隔离与 MVCC：同一事务到底能看到什么](isolation-and-mvcc.md)：以 PostgreSQL 18 的普通查询解释语句快照、事务快照与[写偏斜](../../glossary/database.md#database.write-skew)，明确[可串行化](../../glossary/distributed.md#distributed.linear-serial)和重试边界。
- [LSM、SSTable 与压缩合并：写入返回后，后台为什么仍然忙](lsm-sstables-and-compaction.md)：解释内存写入、不可变有序文件与多路合并，区分快照、删除标记、读写空间放大和持续写入能力。
- [分区、分片与数据路由：一次查询需要访问哪些数据](partitioning-sharding-and-data-routing.md)：沿拆分规则、[分片键](../../glossary/database.md#database.shard-key)与查询谓词确定目标数据，解释[热点](../../glossary/performance.md#performance.contention)、跨片约束、结果合并和扩容迁移的边界。
- [实验：观察 PostgreSQL 索引、扫描与回表](query-plans-lab.md)：用 20 万行临时数据记录六组真实查询计划，区分联合索引、顺序扫描与可见性检查。
- [数据库迁移兼容：回退代码为什么救不回数据](schema-migrations-and-compatibility.md)：从混合版本的读写契约安排扩展、回填、切换与收缩，识别锁成本和不可逆边界。
- [WAL 与崩溃恢复：提交后数据页为何还没写完](wal-and-crash-recovery.md)：区分[日志持久化](../../glossary/database.md#database.checkpoints)、数据页写回、检查点与恢复，说明提交确认和存储故障的边界。

## 术语范围

| 术语 | 简释 |
| --- | --- |
| [RDBMS / NoSQL](../../glossary/database.md#database.db-models) | 关系模型及多种非关系数据模型。 |
| [OLTP / OLAP](../../glossary/database.md#database.workloads) | 在线事务与分析型访问模式。 |
| [ACID](../../glossary/database.md#database.acid) | 事务[原子性](../../glossary/systems.md#systems.atomicity)、约束一致性、隔离性和持久性。 |
| [Transaction / Isolation Level](../../glossary/database.md#database.isolation) | 事务边界及并发可见性保证。 |
| [Dirty / Non-repeatable / Phantom Read](../../glossary/database.md#database.anomalies) | 读取未提交数据、重复读取变化和结果集变化。 |
| [MVCC](../../glossary/database.md#database.mvcc) | 用数据版本协调读写并发。 |
| [Optimistic / Pessimistic Lock](../../glossary/database.md#database.locking) | 检测冲突后处理与提前限制竞争。 |
| [Index / Covering Index](../../glossary/database.md#database.indexes) | 缩小访问范围及从索引满足查询。 |
| [Query Plan / EXPLAIN](../../glossary/database.md#database.plans) | 数据库执行路径、估算与实际执行信息。 |
| [WAL / Redo / Undo](../../glossary/database.md#database.recovery-log) | 预写、重放与回滚相关日志机制，细节因引擎而异。 |
| [LSM / SSTable / Compaction](../../glossary/database.md#database.lsm) | 以内存积累、有序文件与后台合并组织键值更新，区分版本、删除及读写空间放大。 |
| [Normalization / Denormalization](../../glossary/database.md#database.normalization) | 减少冗余与按访问需求引入冗余。 |
| [Replication / Read Replica](../../glossary/database.md#database.replication) | 复制状态并提供副本读取。 |
| [Partitioning / Sharding](../../glossary/database.md#database.partitioning) | 在逻辑或节点间拆分数据。 |
| [Prepared Statement](../../glossary/database.md#database.prepared) | 参数化执行与可能的计划复用，依驱动和数据库而异。 |
| [Schema Migration / CDC](../../glossary/database.md#database.migration) | 结构演进与数据变更捕获。 |
| [Unique Constraint / Foreign Key](../../glossary/database.md#database.constraints) | 由数据库维护唯一性和引用关系。 |
| [Write Skew](../../glossary/database.md#database.write-skew) | 并发事务依据各自快照做出相关判断、更新不同记录，合并结果可能违反跨记录约束的异常。 |
| [Selectivity / Row Estimate](../../glossary/database.md#database.selectivity) | 条件匹配比例与计划节点预计输出行数，用于分析访问路径和估计误差。 |
| [Logical Backup / Physical Backup / PITR](../../glossary/database.md#database.backups) | 按对象或集群保存恢复材料，并用基础备份与连续日志到达所选历史边界。 |
| [Checkpoint / WAL Flush](../../glossary/database.md#database.checkpoints) | 区分日志持久化、数据页写回与恢复起点，不把提交确认当作所有页已同步写回。 |
| [Functional Dependency](../../glossary/database.md#database.functional-dependency) | 关系中的 X→Y 要求所有合法状态中，任意两行的 X 值相同就有相同的 Y 值。 |
| [Shard Key](../../glossary/database.md#database.shard-key) | 参与数据放置及目标选择的字段组合，其分布和查询使用方式影响热点、扇出与跨片约束。 |
| [Partition Pruning](../../glossary/database.md#database.partition-pruning) | 根据查询条件和分区边界，排除不可能包含匹配数据的分区，再在留下的范围内选择访问路径。 |

## 练习与验收

选择上面的一个核心问题，先画执行过程或数据边界，再构造一个正常路径和一个失败路径。用原理解释、架构或代码、诊断证据和取舍依据说明保证范围；记录已完成验证与待验证项。

[回到知识地图](../../map.md) · [问题导航](../../problems.md) · [学习路径](../../paths/index.md)
