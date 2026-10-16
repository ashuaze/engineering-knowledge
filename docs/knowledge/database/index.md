<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# 数据库与存储

建议优先级：P0。目标：围绕数据约束、访问路径和恢复理解数据库。

下方术语用于知识索引。建议从[实际工程问题](../../problems.md)或本页核心问题进入，结合已有正文理解机制、适用边界与相关概念。

## 一个核心问题

同一业务约束在并发下为何可能被两个成功事务破坏？

## 已有正文

- [库存并发：两个成功事务为何仍可能超卖](concurrent-inventory.md)：从陈旧读取和单行条件更新理解事务隔离、数据库约束与业务不变量的分工。

## 术语范围

| 术语 | 简释 |
| --- | --- |
| RDBMS / NoSQL | 关系模型及多种非关系数据模型。 |
| OLTP / OLAP | 在线事务与分析型访问模式。 |
| ACID | 事务原子性、约束一致性、隔离性和持久性。 |
| Transaction / Isolation Level | 事务边界及并发可见性保证。 |
| Dirty / Non-repeatable / Phantom Read | 读取未提交数据、重复读取变化和结果集变化。 |
| MVCC | 用数据版本协调读写并发。 |
| Optimistic / Pessimistic Lock | 检测冲突后处理与提前限制竞争。 |
| Index / Covering Index | 缩小访问范围及从索引满足查询。 |
| Query Plan / EXPLAIN | 数据库执行路径、估算与实际执行信息。 |
| WAL / Redo / Undo | 预写、重放与回滚相关日志机制，细节因引擎而异。 |
| Normalization / Denormalization | 减少冗余与按访问需求引入冗余。 |
| Replication / Read Replica | 复制状态并提供副本读取。 |
| Partitioning / Sharding | 在逻辑或节点间拆分数据。 |
| Prepared Statement | 参数化执行与可能的计划复用，依驱动和数据库而异。 |
| Schema Migration / CDC | 结构演进与数据变更捕获。 |
| Unique Constraint / Foreign Key | 由数据库维护唯一性和引用关系。 |

## 练习与验收

选择上面的一个核心问题，先画执行过程或数据边界，再构造一个正常路径和一个失败路径。用原理解释、架构或代码、诊断证据和取舍依据说明保证范围；记录已完成验证与待验证项。

[回到知识地图](../../map.md) · [问题导航](../../problems.md) · [学习路径](../../paths/index.md)
