<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# 缓存、检索与对象存储

建议优先级：P0。目标：设计快速读取、失效、相关性与大对象访问。

下方术语用于知识索引。建议从[实际工程问题](../../problems.md)或本页核心问题进入，结合已有正文理解机制、适用边界与相关概念。

## 一个核心问题

[缓存失效](../../glossary/cache-search.md#cache-search.invalidation)时，如何避免回源请求压垮数据库？

## 已有正文

- [Bloom Filter 与成员判断：可能存在，为什么不能直接当作命中](bloom-filters-membership-and-synchronization.md)：解释位数组、概率误报和插入集合的阴性保证，区分删除、容量估算、过滤器同步及权威数据查询。
- [Cache-Aside 与失效：缓存为什么会返回旧数据](cache-aside-and-invalidation.md)：区分缓存读取、权威写入、失效与过期，分析旧值回填和回源的边界。
- [缓存加载合并与惊群控制：少回源为何仍需容量和回填边界](cache-load-coalescing-and-stampedes.md)：解释同键共享加载的身份、生命周期与作用范围，区分过期错峰、旧值复用、回源容量和迟到回填。
- [混合召回与重排：分数更高，为什么仍救不回遗漏的资料](hybrid-retrieval-fusion-and-reranking.md)：解释多路候选、去重、分数与排名融合、[Cross-Encoder](../../glossary/cache-search.md#cache-search.hybrid) 重排及分阶段评价，明确截断、权限和失败边界。
- [索引重建、增量追赶与切换：怎样覆盖期间的新增和删除](index-rebuild-watermarks-and-cutover.md)：用快照切点和连续应用水位组织重建，解释更新、删除、重放、原子发布、在途请求、回退与旧索引回收。
- [倒排索引与全文检索：词都命中了，为什么仍不是想要的结果](inverted-indexes-analysis-and-relevance.md)：从词项到[倒排表](../../glossary/cache-search.md#cache-search.inverted)解释布尔和短语查询，区分分词契约、[词频](../../glossary/cache-search.md#cache-search.bm25)统计、BM25 排序及文档版本与访问边界。
- [LRU、LFU 与缓存淘汰：最近用过，为什么仍可能被移走](lru-lfu-and-capacity-eviction.md)：比较精确 [LRU](../../glossary/algorithms.md#algorithms.eviction)/LFU 的访问状态、维护成本和适应性，区分容量、接纳、过期、失效与 Redis 近似策略。
- [对象存储与预签名访问：文件上传后怎样成为可用的业务对象](object-storage-versions-uploads-and-presigned-access.md)：区分对象键、版本、校验、上传完成与业务发布，解释单键一致性、条件写、分段上传及预签名访问的[授权](../../glossary/security.md#security.identity)和期限。
- [Redis 数据结构：怎样按操作、容量与原子边界选型](redis-data-types-operations-and-atomicity.md)：从字段更新、去重、排序和消费位置选择 Redis 类型，区分命令[原子性](../../glossary/systems.md#systems.atomicity)、事务错误、过期、集群槽位与恢复责任。
- [向量索引与近似检索：找到了相似项，为什么仍会漏掉近邻](vector-indexes-metrics-and-approximate-search.md)：区分向量空间、距离与精确基线，解释 [HNSW](../../glossary/cache-search.md#cache-search.ann)、IVF、量化、过滤及近邻召回率的保证范围。
- [写穿与异步写回：写入成功究竟确认到了哪里](write-through-write-behind-and-durability.md)：区分同步[写穿](../../glossary/cache-search.md#cache-search.cache-write)与延后写回的确认、持久化和恢复边界，解释写入合并、版本顺序、[排队](../../glossary/performance.md#performance.queueing)容量及数据库可见性。

## 术语范围

| 术语 | 简释 |
| --- | --- |
| [Cache Aside / Read Through](../../glossary/cache-search.md#cache-search.cache-read) | 应用管理缓存或由缓存层加载数据。 |
| [Write Through / Write Behind](../../glossary/cache-search.md#cache-search.cache-write) | 由缓存写路径同步推进后端，或先接纳待写状态再延后推进后端的两种组织方式。 |
| [Cache Invalidation / TTL](../../glossary/cache-search.md#cache-search.invalidation) | 主动失效与按时过期。 |
| [Penetration / Breakdown / Avalanche](../../glossary/cache-search.md#cache-search.cache-failures) | 不存在键回源、[热点](../../glossary/performance.md#performance.contention)失效和大量键或节点失效造成的负载问题。 |
| [Cache Stampede](../../glossary/cache-search.md#cache-search.stampede) | 并发未命中或刷新引发同一结果的重复加载与回源放大。 |
| [Redis Data Structures](../../glossary/cache-search.md#cache-search.redis-types) | 按整值、字段、成员、排名或消费位置组织服务器操作的 Redis 逻辑类型。 |
| [Distributed Lock / Lease](../../glossary/cache-search.md#cache-search.lock-lease) | 跨节点互斥及有期限的持有权。 |
| [Inverted Index](../../glossary/cache-search.md#cache-search.inverted) | 从词项定位文档及可选位置，分析规则、布尔条件与短语匹配分别决定结果。 |
| [BM25 / Full-text Search](../../glossary/cache-search.md#cache-search.bm25) | 全文匹配与相关性排序分别负责候选和次序；正文概述 BM25 的词频、集合及长度因素，不提供完整评分实现。 |
| [Embedding / Similarity Search](../../glossary/cache-search.md#cache-search.vectors) | 用兼容空间中的距离或相似度比较向量，区分编码质量、归一化与精确搜索基线。 |
| [ANN / HNSW](../../glossary/cache-search.md#cache-search.ann) | 通过图探索、分区或量化交换查询/空间成本与近邻覆盖；过滤和精确基线有各自前提。 |
| [Hybrid Search / Reranking](../../glossary/cache-search.md#cache-search.hybrid) | 对齐多路候选身份后融合排名或校准分数，再对有限输入重排；截断、相关性与来源支持分别检查。 |
| [Object Storage / Presigned URL](../../glossary/cache-search.md#cache-search.objects) | 按键和可选版本保存对象，通过有范围与期限的签名请求能力访问。 |
| [Index Rebuild / Index Cutover](../../glossary/cache-search.md#cache-search.index-cutover) | 以快照与增量覆盖明确源状态边界，再发布新的索引代次，并安排在途请求、回退和旧代次回收。 |
| [Request Coalescing / Singleflight](../../glossary/cache-search.md#cache-search.coalescing) | 让可复用结果的同键重叠请求共享一项在途工作。 |

## 练习与验收

选择上面的一个核心问题，先画执行过程或数据边界，再构造一个正常路径和一个失败路径。用原理解释、架构或代码、诊断证据和取舍依据说明保证范围；记录已完成验证与待验证项。

[回到知识地图](../../map.md) · [问题导航](../../problems.md) · [学习路径](../../paths/index.md)
