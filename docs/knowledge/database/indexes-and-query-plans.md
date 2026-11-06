---
id: "kb-database-indexes-plans"
title: "索引与执行计划：为什么建了索引仍然扫描全表"
kind: "concept"
domain: "database"
status: "evolving"
summary: "以 PostgreSQL 18 的 B-tree 查询解释访问路径、行数估计、联合索引与 EXPLAIN 的证据边界。"
created: "2026-10-19"
updated: "2026-10-22"
last_verified: "2026-10-19"
verification: "source-checked"
prerequisites: []
related: ["kb-algorithms-complexity", "kb-database-isolation-mvcc", "kb-performance-slow-api", "kb-reliability-telemetry", "kb-api-contracts-pagination", "kb-database-query-plans-lab", "kb-algorithms-hash-tables", "kb-algorithms-trees-heaps", "kb-algorithms-sorting-boundaries", "kb-algorithms-page-indexes", "kb-database-lsm", "kb-cache-search-inverted-index", "kb-security-sql-injection", "kb-database-models-access-patterns", "kb-database-partitioning-sharding"]
tags: ["indexes", "query-plans", "postgresql"]
---

# 索引与执行计划：为什么建了索引仍然扫描全表

学习入口：WHERE 用到了索引列，数据库为什么仍选全表扫描？前置知识：基本 SELECT、WHERE、ORDER BY 与事务。本文限定 PostgreSQL 18、普通表上的 [B-tree](../../glossary/algorithms.md#algorithms.b-tree) 与单机[查询计划](../../glossary/database.md#database.plans)；其他索引类型、数据库和分布式优化器应分别核查。

## 索引改变访问路径，也增加维护成本

把表想成保存完整记录的区域，把索引想成按某种规则组织的另一份访问结构。B-tree 可用于等值、范围和特定排序访问；它帮助跳过不相关区域，但读索引、定位表记录、检查可见性和返回数据都可能有成本。[PostgreSQL 的索引类型说明](https://www.postgresql.org/docs/18/indexes-types.html)列出了不同访问方法支持的操作，不能把所有索引都理解为同一棵树。

一次查询可能采用顺序扫描（Seq Scan）、索引扫描（[Index](../../glossary/database.md#database.indexes) Scan），或先生成位置位图再访问表页的 Bitmap Heap Scan。匹配大部分记录时，反复沿索引找到分散的表记录可能比连续读取表更贵；小表也可能根本不值得走索引。顺序扫描因此是需要解释的选择，而不是自动成立的故障证据。

索引还占用空间，并随相关写入更新。为每个过滤列都建一个索引，会增加写入和维护负担，也不保证一次查询能同时利用它们。应先明确常见访问模式、返回规模与写入成本，再评估候选结构。

## 选择率、行数估计与代价

本文把[选择率](../../glossary/database.md#database.selectivity)称为满足条件的行占输入行的比例：比例越小，过滤越有选择性。行数估计则是优化器预计某节点输出多少行。例如同样查一个客户，大客户与普通客户的匹配量可能相差很大，不能用“等值条件”直接推导“只返回少量行”。

优化器用统计信息和成本参数估计不同计划。[统计信息文档](https://www.postgresql.org/docs/18/planner-stats.html)说明了常见值、分布与多列统计等信息：数据刚发生大幅变化、分布偏斜或列之间相关，都可能让简单估计失准。ANALYZE 用于更新统计信息，但不保证任意参数下的估计都准确，也不会替查询补上缺失的访问结构。

排查时先区分两个问题：计划是否误判了行数，以及实际执行是否昂贵。估计很准但需要读取大量数据，可能是访问需求本身很重；估计严重偏小，则可能使连接方式等后续选择偏离实际。不能仅凭索引名称或一条耗时判断该改哪一项。

## 联合索引从查询约束出发

教学设定：orders 表的 id 为主键（唯一且非空），另有 customer_id 和非空 created_at，希望按稳定顺序读取某客户较新的 20 笔订单。以下 orders 命名的 SQL 说明候选设计；[配套实验](query-plans-lab.md)已在独立临时表上执行同一访问模式并保存实际计划，不代表已经测试你的业务 orders 表。

```sql
CREATE INDEX orders_customer_created_id
    ON orders (customer_id, created_at, id);

EXPLAIN
SELECT id, created_at
FROM orders
WHERE customer_id = 42
  AND created_at >= TIMESTAMPTZ '2026-10-01 00:00:00+00'
ORDER BY created_at DESC, id DESC
LIMIT 20;
```

索引先按客户分组，再按时间与 id 排列；客户等值约束与后续时间范围为缩小扫描范围提供条件。B-tree 的反向扫描也可能帮助满足这里的排序。唯一 id 作为同一时间下的次序补充，避免把时间相同的记录当成天然有固定顺序。最终计划仍取决于数据、统计信息和代价，不能宣称建完后必然采用某个节点。

联合索引的列顺序影响能有效缩小的扫描区域。“缺少最左列条件就完全不能使用索引”过于绝对：[PostgreSQL 18 的多列索引说明](https://www.postgresql.org/docs/18/indexes-multicolumn.html)还描述了 skip scan，在前导列不同值较少等合适条件下，可通过重复搜索利用后续列约束。这不是任意缺失前缀都高效的保证。把客户条件移除后，应重新分析查询，不能沿用原来的收益判断。

## 读 EXPLAIN 时分别问什么

EXPLAIN 展示估计计划；EXPLAIN ANALYZE 会实际执行查询并附带观测信息。下面是阅读提示，不是本仓库的测量结果。

| 信息 | 要问的问题 | 容易误读之处 |
| --- | --- | --- |
| cost、rows | 优化器认为要付出多少代价、输出多少行 | cost 是模型单位，不是毫秒；rows 是节点输出估计 |
| actual time、rows、loops | 实际处理规模与重复执行次数是否符合预期 | 多次执行时，时间与行数通常按每次执行平均展示 |
| Index Cond、Filter | 哪些条件约束索引访问，哪些在取出候选后过滤 | 使用了索引仍可能读取大量无用候选 |
| Buffers、排序信息 | 访问了哪些缓冲页，排序是否产生额外工作 | 页计数不等于独立页数；read 不足以证明物理磁盘慢 |

这些字段的口径见 [Using EXPLAIN](https://www.postgresql.org/docs/18/using-explain.html)。父节点的时间和缓冲统计可包含子节点工作；不要把整棵树逐项相加当作请求总耗时。遇到循环节点应结合 loops 解释实际工作量；LIMIT 等提前停止也会影响实际读取规模。

需要执行分析时，可在受控测试数据上把示例改为 `EXPLAIN (ANALYZE, BUFFERS)`，同时保存版本、参数、数据分布、统计更新时间和缓存状态。ANALYZE 选项会执行动作；写语句、调用函数及外部副作用必须另行评估，不能把 EXPLAIN ANALYZE 当作仅预览计划，或认为数据库回滚能撤销所有外部动作。

## 覆盖索引不等于一定不访问表

如果索引保存了查询需要的列，就具备尝试 Index Only Scan 的部分条件。PostgreSQL 仍需判断记录对当前快照是否可见：可见性映射的相应页若不满足条件，就需要访问表记录。因而计划出现 Index Only Scan 时，Heap Fetches 仍可能非零。[索引仅扫描文档](https://www.postgresql.org/docs/18/indexes-index-only-scans.html)解释了这一限制。

这也连接到 [MVCC](isolation-and-mvcc.md)：索引中的值并不自动证明当前事务可以看到对应版本。把大量列加入覆盖索引，还会扩大索引并增加维护成本，不能只按一次只读查询的收益作决定。

## 自检与后续验证

先回答三个问题：命中大部分行时，为什么顺序扫描可能合理？同一个[参数化查询](../../glossary/security.md#security.sql-injection)面对冷热客户时，为何需要比较不同参数？Index Only Scan 为何仍可能访问表？

再为一次真实慢查询留下诊断记录：原始问题与返回要求、代表性参数、估计与实际行数差异、读取与排序证据、候选改动，以及同样工作负载下的前后对照。若时间主要花在[连接池](../../glossary/api.md#api.pool)等待，数据库内部计划不能单独解释接口[延迟](../../glossary/performance.md#performance.latency-throughput)。

本文机制核查日期为 2026-10-19，依据 PostgreSQL 18 文档。[PostgreSQL 查询计划实验](query-plans-lab.md)已记录 20 万行临时数据上的六组对照，包括联合索引、宽过滤顺序扫描、更新与 VACUUM 后的回表变化。实验仅覆盖所述本机环境；本文的通用机制范围仍标为来源核查，不把单次耗时外推为性能承诺。

参数化与服务端准备、执行计划复用各有范围，且输入安全不能仅凭计划缓存判断，继续见[SQL 注入与参数化查询](../security/sql-injection-parameters-and-query-structure.md)。

索引之前的事实与约束选择见[数据模型与访问模式](data-models-and-access-patterns.md)，查询会访问哪些[分区](../../glossary/database.md#database.partitioning)或节点见[分区、分片与数据路由](partitioning-sharding-and-data-routing.md)。访问路径与分布设计各有成本，不由单一索引代替。

## 关联阅读与来源

其他机制可对照 [LSM 与合并](lsm-sstables-and-compaction.md)及[倒排索引与全文检索](../cache-search/inverted-indexes-analysis-and-relevance.md)，分别理解存储写入与词项访问；并不表示本文的 PostgreSQL B-tree 示例采用 [LSM](../../glossary/database.md#database.lsm)，也未重跑既有执行计划实验。

内存访问基础可配套读[哈希表](../algorithms/hash-tables-collisions-and-key-contracts.md)、[树与堆](../algorithms/trees-heaps-and-priority-queues.md)及[排序与二分](../algorithms/sorting-binary-search-and-boundaries.md)，比较精确、有序与极值需求。页组织继续见 [B/B+ 树与页索引](../algorithms/b-trees-bplus-trees-and-page-indexes.md)，区分分隔键、叶载荷与范围扫描。本次关联不把内存树模型等同于数据库索引，也未重跑既有查询计划实验。

- [HTTP 契约与分页](../api/contracts-and-pagination.md)：从[稳定排序](../../glossary/algorithms.md#algorithms.sorting-search)与位置边界设计访问，再验证索引成本。

- [复杂度与数据结构](../algorithms/complexity-and-data-structures.md)：理解访问结构与成本模型，避免把渐进复杂度当成实测耗时。
- [事务隔离与 MVCC](isolation-and-mvcc.md)：理解快照与记录可见性。
- [慢 API 排查](../performance/slow-api-investigation.md)：区分数据库执行与请求其他阶段的等待。
- [日志、指标与链路](../reliability/logs-metrics-and-traces.md)：把查询证据关联到请求与总体异常。

机制来源已在相应段落链接：PostgreSQL 18 的索引类型、多列索引、统计信息、EXPLAIN 与索引仅扫描文档。
