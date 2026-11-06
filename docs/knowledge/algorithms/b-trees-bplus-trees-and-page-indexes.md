---
id: "kb-algorithms-page-indexes"
title: "B 树、B+ 树与页索引：树高很低，查询为什么仍然慢"
kind: "concept"
domain: "algorithms"
status: "evolving"
summary: "从页访问和扇出解释 B/B+ 树，区分分隔键、叶条目、范围扫描、分裂及真实数据库的回表与可见性成本。"
created: "2026-10-20"
updated: "2026-10-20"
last_verified: "2026-10-20"
verification: "source-checked"
prerequisites: ["kb-algorithms-trees-heaps", "kb-algorithms-sorting-boundaries"]
related: ["kb-algorithms-trie", "kb-cache-search-bloom", "kb-database-indexes-plans", "kb-database-isolation-mvcc", "kb-systems-virtual-memory", "kb-database-lsm", "kb-cache-search-inverted-index"]
tags: ["b-tree", "bplus-tree", "page-index", "range-scan"]
---

# B 树、B+ 树与页索引：树高很低，查询为什么仍然慢

学习入口：索引只有几层，为什么一次范围查询仍要读取很多数据？前置：[树与搜索规则](trees-heaps-and-priority-queues.md)、[有序边界](sorting-binary-search-and-boundaries.md)。本文以典型 [B+ 树](../../glossary/algorithms.md#algorithms.b-tree)教学模型解释页组织，数据库对照限定 PostgreSQL 18；图、容量和操作为纸面推演，没有新增页索引实验。

## 成本单位从一次比较扩展到一页

内存[二叉搜索树](../../glossary/algorithms.md#algorithms.trees)常分析沿路径比较多少次；面向存储的索引还要考虑读取和修改哪些页。一个节点保存多个分隔键和子页引用，可以一次取得较多分支信息。扇出是节点能指向的孩子数量，不是二叉树的“每层两个分支”。

叶子保持相同深度、各节点满足相应容量约束，是典型平衡多路树模型的核心条件。高扇出能缩短路径，但键宽、页内元数据、填充率和布局会影响实际容量；不能给所有数据库套同一个阶数或页大小。概念参照 [NIST B-tree](https://xlinux.nist.gov/dads/HTML/btree.html)和 [CMU 索引讲义](https://15445.courses.cs.cmu.edu/fall2024/notes/08-indexes1.pdf)。

教学估算：若每个叶页恰好容纳 100 项，100 万项需要 1 万个叶页；每个内部页恰好指向 100 个孩子，则上面需要 100 个内部页和 1 个根页，共三层。此处假定填满、等长项且没有额外页面，不是实际数据库页数或三次物理磁盘读取的测量结果。

## B 与 B+ 的区别不只是名字

在经典对照中，B 树的键与关联数据可出现在内部和叶节点；B+ 树将完整的数据条目放在叶层，内部节点用分隔键和子引用导航，叶层通常再相连以支持有序扫描。叶条目可以保存记录位置或记录数据，不要求所有数据库都把整行放进叶子。

内部出现某个分隔键，不表示已找到一份可直接返回的业务记录；还需沿其规则继续定位。名称也有变体：数据库文档常用 B-tree 泛指相应索引家族，不能仅靠名字推断叶载荷和实现细节。上述对照见 [CMU B+Tree](https://15445.courses.cs.cmu.edu/fall2024/notes/08-indexes1.pdf)。

PostgreSQL 18 的 [B-Tree 结构](https://www.postgresql.org/docs/18/btree.html#BTREE-STRUCTURE)说明内部页指向下一层、叶页中的索引条目指向表行，各层还有页链接；因此不能把“B+ 叶保存数据”理解为 PostgreSQL 的普通索引叶必然包含完整表行。

## 范围查询先定位，再沿叶层前进

下面自设唯一整数键，分隔键采用“右孩子范围的下界”，相等时向右。叶子容量最多 3 项，内部最多 4 个孩子；图中叶链从左到右：

```text
                根：[20 | 40]
                 /     |      \
            [5,12] [20,28,35] [40,55]
               └──────→───────→┘
```

查询半开范围 [22,45)：先进入中间叶页，跳过 20，取得 28、35；再沿叶链到右页，取得 40，遇到 55 后停止。结果为 28、35、40。若只报从根到叶的成本，就漏掉后续叶页和结果输出；返回很多项不可能只付出一次定位的代价。

即使索引叶有序，访问其指向的表记录也未必连续；叶链逻辑相邻不保证物理页相邻或必然命中缓存。缓冲池命中可以避免某些存储读取，但查页、页内比较、可见性判断和输出仍需工作。页访问与[虚拟内存缺页](../systems/virtual-memory-pages-and-faults.md)也不是同一种统计事件。

## 更新要同时维护路径和页容量

继续上图，插入 30 后，中间叶暂成 [20,28,30,35]，超过本例容量。可拆成 [20,28] 与 [30,35]，在父页增加分隔键 30 和新子页引用，根成为 [20,30,40]；更新叶链接后为 [5,12] → [20,28] → [30,35] → [40,55]。30 仍保留在叶条目中，父页的副本用于导航；不能把复制分隔键当作业务数据重复插入。

父页若也放不下，分裂可能向上传播，根分裂会增加层级。教学删除模型又需按占用规则借用或合并、更新父引用；本例只给容量上限，未定义最小占用规则，不能据此推演唯一的删除步骤。真实实现可能采用不同清理时机，不能要求每次 SQL DELETE 都立即触发同样合并。操作模型见 [CMU B+Tree 项目说明](https://15445.courses.cs.cmu.edu/fall2024/project2/)，PostgreSQL 的分裂与版本清理分别见其[实现文档](https://www.postgresql.org/docs/18/btree.html#BTREE-IMPLEMENTATION)。

真实[并发](../../glossary/systems.md#systems.concurrency)还涉及页保护、事务锁、日志和崩溃恢复。单次纸面[重排](../../glossary/cache-search.md#cache-search.hybrid)既不是原子持久化实现，也不能证明扫描期间没有遗漏或重复。

## 索引成本仍要接回查询契约

存储写入组织可对照 [LSM 与合并](../database/lsm-sstables-and-compaction.md)，词项到文档的查询可继续读[倒排索引](../cache-search/inverted-indexes-analysis-and-relevance.md)。两者讨论不同层次的组织与访问需求，不根据结构名字直接比较实际耗时；本次关联未新增页索引实验。

| 已知条件 | 还不能推出什么 |
| --- | --- |
| 树高较低 | 查询返回少、表页访问少或耗时固定 |
| 叶中包含查询所需列 | PostgreSQL 必然完全免于表可见性检查 |
| 有序索引存在 | 优化器必选它，或任意列组合都能高效定位 |
| 分裂算法保持结构 | [事务隔离](../../glossary/database.md#database.isolation)和断电恢复已实现 |

PostgreSQL 的[索引仅扫描](https://www.postgresql.org/docs/18/indexes-index-only-scans.html)仍依赖可见性映射等条件；具体计划、联合键、重复值与输出要求继续见[索引与执行计划](../database/indexes-and-query-plans.md)。本例只用唯一键；重复业务键需定义附加标识、条目列表等表示，不能直接沿用本图的唯一性假设。

自检：比较的是树高、页访问还是物理 I/O？分隔键在哪一边包含等号？范围输出还跨哪些页？叶条目保存什么？结构更新、记录可见性和耐久性分别由谁保证？

2026-10-20 核查 NIST、CMU 15-445 Fall 2024 与 PostgreSQL 18 文档，状态为 source-checked。容量、范围及分裂为教学设计；未实现 B/B+ 树、页缓存、合并、并发扫描或故障恢复，未重跑既有[查询计划](../../glossary/database.md#database.plans)实验。
