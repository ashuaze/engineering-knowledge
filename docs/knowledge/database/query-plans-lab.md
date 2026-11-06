---
id: "kb-database-query-plans-lab"
title: "实验：观察 PostgreSQL 索引、扫描与回表"
kind: "lab"
domain: "database"
status: "evolving"
summary: "用 20 万行临时数据记录六组真实查询计划，区分联合索引、顺序扫描与可见性检查。"
created: "2026-10-19"
updated: "2026-10-20"
last_verified: "2026-10-19"
verification: "tested"
prerequisites: ["kb-database-indexes-plans"]
related: ["kb-database-indexes-plans", "kb-database-isolation-mvcc", "kb-performance-slow-api", "kb-api-contracts-pagination"]
tags: ["postgresql", "query-plans", "testing"]
---

# 实验：观察 PostgreSQL 索引、扫描与回表

## 要验证什么

建了联合索引，哪些查询会用它？计划写着 [Index](../../glossary/database.md#database.indexes) Only Scan，为什么仍有 Heap Fetches？本实验把这两个问题放进同一个受控数据集，保存 `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)` 的完整输出，并校验查询前后返回同样的 20 个订单 id。机制先读[索引与执行计划](indexes-and-query-plans.md)。

这是单机临时表实验。它没有复现库存竞争、分页期间的[并发](../../glossary/systems.md#systems.concurrency)修改、生产表缓存与 [WAL](../../glossary/database.md#database.recovery-log) 开销，也不测吞吐容量。[执行计划](../../glossary/database.md#database.plans)选择是当前环境的观察，不能作为所有 PostgreSQL 18 环境的固定断言。

## 环境与复现

2026-10-19 实际环境：Windows x64、PostgreSQL **18.0**（MSVC 19.44.35215）、Python **3.13.13**。使用 PostgreSQL 官方 Windows 下载页所指向的 EDB 二进制分发；本次固定包版本，不把文档的 18 系列版本当作实际运行补丁号。分发包地址、校验和及源码/记录摘要见[证据清单](../../../examples/query_plans/results/manifest.json)。

需要 Python 3.10+ 和 PostgreSQL 18 的 `psql`、`initdb`、`pg_ctl`、`createdb`。准备好工具后，从仓库根目录运行（将目录换成自己的路径）：

```bash
python examples/query_plans/lab.py --pg-bin /path/to/pgsql/bin
# 也可运行 npm run lab:query-plans -- --pg-bin /path/to/pgsql/bin
```

默认在仓库 `.cache` 内创建独立集群，只监听 `127.0.0.1` 的临时端口，建立 `kb_query_plan_lab` 数据库；实验结束停止集群并移除其数据目录，记录留在 `.cache/query-plans/`。初始化使用仅适合本机实验的 trust [认证](../../glossary/security.md#security.identity)。Unix 环境请以可运行 PostgreSQL 的普通用户执行。运行器不会下载或安装数据库。

已有专用本机实验库时，可用 `--external --port 5432 --user postgres`；此模式固定连接回环地址和 `kb_query_plan_lab`，只创建会话临时表，不负责启动或停止外部实例。需要密码时按本机 PostgreSQL 凭据配置处理，不把密码写入命令或结果。

实现见[Python 运行器](../../../examples/query_plans/lab.py)和[完整 SQL](../../../examples/query_plans/lab.sql)。默认每条语句[超时](../../glossary/api.md#api.retries) 60 秒、锁等待超时 3 秒；关闭并行查询和 [JIT](../../glossary/runtime.md#runtime.compilation) 以简化节点解释，没有关闭顺序扫描或强制某种计划。

## 数据与六组步骤

临时表有 200,000 行，`id` 为主键，`created_at` 非空，另有客户 id 和 200 字符 payload。客户 1 占 160,000 行（80%）；客户 42 占 40 行（0.02%）。每个阶段都保留相同的稀疏客户查询：按 `created_at DESC, id DESC` 取前 20 行。

1. 插入数据并 VACUUM ANALYZE，记录尚无客户联合索引时的查询。
2. 建立 `(customer_id, created_at, id)` 联合索引并 VACUUM ANALYZE，再查同一客户。
3. 保留索引，改查客户 1 的 `sum(length(payload))`，观察大量命中且需要 payload 时的访问路径。
4. 只更新客户 42 的 payload，再运行原来的前 20 行查询，观察可见性检查。
5. 默认 VACUUM（VERBOSE, ANALYZE）后再次观察。
6. 再做 VACUUM（VERBOSE, ANALYZE, INDEX_CLEANUP ON），比较回表和清理记录。

宽过滤查询的输出与前 20 行查询不同，不能用两者耗时计算索引收益。前 20 行查询只返回 id 与时间，payload 更新不会改变其预期结果。

## 本次实际记录

下表从[完整 JSON 记录](../../../examples/query_plans/results/results.json)摘出。节点按根到子节点列出；时间是各场景一次 EXPLAIN ANALYZE 的 Execution Time，含测量开销，缓存状态也随步骤变化。

| 场景 | 实际节点 | Heap Fetches | Execution Time（ms） |
| --- | --- | --- | --- |
| 建联合索引前 | Limit → Sort → Seq Scan | 不适用 | 130.939 |
| 建索引并 VACUUM 后 | Limit → Index Only Scan | 0 | 0.153 |
| 命中 80% 且读取 payload | Aggregate → Seq Scan | 不适用 | 349.862 |
| payload 更新后 | Limit → Index Only Scan | 40 | 0.265 |
| 默认 VACUUM 后 | Limit → Index Only Scan | 14 | 0.288 |
| 指定索引清理后 | Limit → Index Only Scan | 0 | 0.551 |

稀疏查询建索引前的扫描估计与实际均输出 40 行；Limit 返回其中 20 行。联合索引后的扫描方向为 Backward，不再出现独立 Sort。宽过滤场景估计 159,860 行、实际扫描输出 160,000 行；它说明顺序扫描可以出现在估计相当接近实际的计划中。

更新后虽然仍叫 Index Only Scan，Heap Fetches 却变为 40，说明节点名称不能替代可见性检查记录。返回 20 行也不表示最多检查 20 个表版本。

默认 VACUUM 后没有降到零。[psql 原始输出](../../../examples/query_plans/results/results.psql.txt)明确记录了 `index scan bypassed`：40 个页有 40 个 dead item identifiers；随后显式索引清理记录 `index scan needed`，本次再查询回表为零。官方 [VACUUM 文档](https://www.postgresql.org/docs/18/sql-vacuum.html)说明默认 AUTO 可能在死元组很少时跳过索引清理。这个对照支持对本次记录的解释，并不意味着生产中应该一律强制清理，或 VACUUM 必然让任意查询零回表。

## 断言与结果边界

运行器的 5 组检查均通过：服务端为 18 系列；三项数据行数符合设定；各个稀疏查询返回同样的 20 个 id；每组计划含实际执行信息；六个场景全部记录。计划是否使用联合索引、宽过滤是否顺序扫描及回表次数另列为观察，不写成跨环境[不变量](../../glossary/systems.md#systems.atomicity)。

本次是 TEMP 表，Buffers 中主要出现 Local Blocks；不能把它当作生产普通表的 Shared Buffers 或持久化写入成本。没有独立控制冷热缓存、重复采样、并发负载或硬件状态，因此不报告“提速多少倍”，也不把毫秒值设成测试门槛。输出中的 cost 是模型单位，read 计数也不能直接证明物理磁盘读取。

复现时先核对相同行集，再解释节点、估计和实际行数、缓冲页及清理日志。若计划不同，应保存完整输出并核对版本、数据、参数与统计信息；不要为凑齐上表而关闭扫描方式。

## 自检与来源

自检：为什么宽过滤查询即使有索引仍可能扫描表？为什么只更新未返回的 payload，也能改变回表次数？如果默认 VACUUM 后仍有回表，需要查看哪些证据，而不是先把实验判成失败？

来源核查日期：2026-10-19。实际运行记录与机制来源分别保留。

- [PostgreSQL 18：Using EXPLAIN](https://www.postgresql.org/docs/18/using-explain.html)
- [PostgreSQL 18：Index-Only Scans](https://www.postgresql.org/docs/18/indexes-index-only-scans.html)
- [PostgreSQL 18：VACUUM](https://www.postgresql.org/docs/18/sql-vacuum.html)
- [PostgreSQL：Windows 分发与下载](https://www.postgresql.org/download/windows/)
- [事务隔离与 MVCC](isolation-and-mvcc.md)：本实验的可见性观察不能替代两会话隔离实验。
- [慢 API 排查](../performance/slow-api-investigation.md)：把数据库内部执行与连接等待、网络及[序列化](../../glossary/runtime.md#runtime.serialization)分开。
