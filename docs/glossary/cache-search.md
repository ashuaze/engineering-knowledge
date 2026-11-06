<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# 缓存、检索与对象存储词汇表

本页解释 15 组术语，按[完整术语索引](../glossary.md#cache-search)中的顺序排列。示例为说明性场景；具体技术版本与验证范围见各条深入阅读。

[分类词汇表](index.md) · [缓存、检索与对象存储文章](../knowledge/cache-search/index.md)

## 本页术语

- [Cache Aside / Read Through](#cache-search.cache-read)
- [Write Through / Write Behind](#cache-search.cache-write)
- [Cache Invalidation / TTL](#cache-search.invalidation)
- [Penetration / Breakdown / Avalanche](#cache-search.cache-failures)
- [Cache Stampede](#cache-search.stampede)
- [Redis Data Structures](#cache-search.redis-types)
- [Distributed Lock / Lease](#cache-search.lock-lease)
- [Inverted Index](#cache-search.inverted)
- [BM25 / Full-text Search](#cache-search.bm25)
- [Embedding / Similarity Search](#cache-search.vectors)
- [ANN / HNSW](#cache-search.ann)
- [Hybrid Search / Reranking](#cache-search.hybrid)
- [Object Storage / Presigned URL](#cache-search.objects)
- [Index Rebuild / Index Cutover](#cache-search.index-cutover)
- [Request Coalescing / Singleflight](#cache-search.coalescing)

<a id="cache-search.cache-read"></a>

## Cache Aside / Read Through

**ID：** `cache-search.cache-read` · **建议优先级：** P0

**别名 / 检索词：** Cache Aside、Read Through、旁路缓存、读穿

**简释：** 应用管理缓存或由缓存层加载数据。

Cache Aside 由应用查缓存、未命中后查主存储并回填；Read Through 由缓存层代为加载。二者都需约定键、加载失败、并发回填与一致性窗口。

**例子：** 旧查询迟到回填时，可能把已更新值覆盖成旧缓存，需要版本或失效协调。

**深入阅读：** [Cache-Aside 与失效：缓存为什么会返回旧数据](../knowledge/cache-search/cache-aside-and-invalidation.md) · [缓存加载合并与惊群控制：少回源为何仍需容量和回填边界](../knowledge/cache-search/cache-load-coalescing-and-stampedes.md) · [写穿与异步写回：写入成功究竟确认到了哪里](../knowledge/cache-search/write-through-write-behind-and-durability.md)

<a id="cache-search.cache-write"></a>

## Write Through / Write Behind

**ID：** `cache-search.cache-write` · **建议优先级：** P0

**别名 / 检索词：** Write Through、Write Behind、写穿、异步写回

**简释：** 由缓存写路径同步推进后端，或先接纳待写状态再延后推进后端的两种组织方式。

Write Through把writer后端写入纳入同步调用路径；Write Behind先接纳状态和待写责任，再由后台推进。成功覆盖内存、可恢复接纳还是后端提交需按实际组件与配置判断，两者都不自动形成缓存/数据库共同事务。异步写回需管理状态合并、版本与删除顺序、重复重试、容量和恢复，不能仅凭写延迟声明持久性或RPO。

**例子：** 缓存接受v2后数据库仍为v1；未耐久待写记录丢失会让重载回到v1。按键只保留最新设置可以减少写入，却不能丢掉独立付款事件。

**深入阅读：** [写穿与异步写回：写入成功究竟确认到了哪里](../knowledge/cache-search/write-through-write-behind-and-durability.md)

<a id="cache-search.invalidation"></a>

## Cache Invalidation / TTL

**ID：** `cache-search.invalidation` · **建议优先级：** P0

**别名 / 检索词：** Cache Invalidation、TTL、缓存失效、过期时间

**简释：** 主动失效与按时过期。

主动失效移除或更新已知旧内容，TTL 限定缓存项的存活期限。TTL 限制陈旧窗口但不提供强一致，失效消息也可能丢失或乱序。

**例子：** 更新数据库并删除缓存后，先前发出的旧读取仍可能迟到回填。

**深入阅读：** [Cache-Aside 与失效：缓存为什么会返回旧数据](../knowledge/cache-search/cache-aside-and-invalidation.md) · [CDN 与 WAF：边缘命中和请求放行分别证明什么](../knowledge/networking/cdn-edge-caches-and-waf-boundaries.md) · [缓存加载合并与惊群控制：少回源为何仍需容量和回填边界](../knowledge/cache-search/cache-load-coalescing-and-stampedes.md) · [写穿与异步写回：写入成功究竟确认到了哪里](../knowledge/cache-search/write-through-write-behind-and-durability.md) · [权限模型与策略传播：规则改了，哪些请求仍可能被允许](../knowledge/security/authorization-models-policy-distribution-and-revocation.md) · [Redis 数据结构：怎样按操作、容量与原子边界选型](../knowledge/cache-search/redis-data-types-operations-and-atomicity.md)

<a id="cache-search.cache-failures"></a>

## Penetration / Breakdown / Avalanche

**ID：** `cache-search.cache-failures` · **建议优先级：** P0

**别名 / 检索词：** Penetration、Breakdown、Avalanche、缓存穿透、缓存击穿、缓存雪崩

**简释：** 不存在键回源、热点失效和大量键或节点失效造成的负载问题。

穿透、击穿和雪崩是常见工程称呼，口径可能不同，应先描述真实键分布、未命中与回源路径。负缓存要限定错误类别、身份及有效期；同键合并不能阻止随机不同键或缓存故障将依赖压满。

**例子：** 热门键过期可合并加载；随机不存在ID仍需输入限制、受控负缓存或完整同步前提下的过滤，以及回源接纳。

**深入阅读：** [缓存加载合并与惊群控制：少回源为何仍需容量和回填边界](../knowledge/cache-search/cache-load-coalescing-and-stampedes.md)

<a id="cache-search.stampede"></a>

## Cache Stampede

**ID：** `cache-search.stampede` · **建议优先级：** P0

**别名 / 检索词：** Cache Stampede、缓存踩踏、同键加载

**简释：** 并发未命中或刷新引发同一结果的重复加载与回源放大。

热点过期、冷启动或刷新可能让同一可复用结果被重复加载。同键合并减少所覆盖范围内的重复工作，但跨实例、不同键、错误重试和缓存故障仍需独立的容量与时间限制；TTL抖动、早刷新和旧值复用各有前提。

**例子：** 三个实例各合并本地同键请求，一波请求仍可能触发三份回源；单键合并不能限制大量不同键的总加载。

**深入阅读：** [Cache-Aside 与失效：缓存为什么会返回旧数据](../knowledge/cache-search/cache-aside-and-invalidation.md) · [缓存加载合并与惊群控制：少回源为何仍需容量和回填边界](../knowledge/cache-search/cache-load-coalescing-and-stampedes.md)

<a id="cache-search.redis-types"></a>

## Redis Data Structures

**ID：** `cache-search.redis-types` · **建议优先级：** P0

**别名 / 检索词：** Redis Data Structures、Redis 数据结构

**简释：** 按整值、字段、成员、排名或消费位置组织服务器操作的 Redis 逻辑类型。

String、Hash、List、Set、Sorted Set和Stream表达不同访问语义；类型不等于内部编码、持久化或端到端业务协议。需同时限定响应/成员容量、命令与事务错误、过期粒度及集群槽位。单命令原子、脚本或消费确认都不能替代外部副作用幂等和恢复证据。

**例子：** 排行榜同分按字节顺序处理而非先达先得；Hash字段更新通常不续键TTL，字段过期还要核对7.4.0起的命令能力。

**深入阅读：** [Redis 数据结构：怎样按操作、容量与原子边界选型](../knowledge/cache-search/redis-data-types-operations-and-atomicity.md)

<a id="cache-search.lock-lease"></a>

## Distributed Lock / Lease

**ID：** `cache-search.lock-lease` · **建议优先级：** P0

**别名 / 检索词：** Distributed Lock、Lease、分布式锁

**简释：** 跨节点互斥及有期限的持有权。

分布式锁/租约限定某段时间的资格，不能使暂停进程或在途写入消失。随机持有标识支持条件释放，严格递增代次支持资源端新旧判断；缓存回填还需业务版本或失效资格检查。

**例子：** 客户端长暂停后恢复，不能只凭自己曾拿到锁就继续写入共享资源。

**深入阅读：** [租约与 Fencing：锁过期后怎样拒绝旧执行者](../knowledge/distributed/leases-heartbeats-and-fencing.md)

<a id="cache-search.inverted"></a>

## Inverted Index

**ID：** `cache-search.inverted` · **建议优先级：** P0

**别名 / 检索词：** Inverted Index、倒排索引、Postings List、倒排表、位置索引、Tokenization

**简释：** 从词项定位文档及可选位置，分析规则、布尔条件与短语匹配分别决定结果。

倒排索引把词项映射到包含它的文档，位置记录可支持短语等条件。分词、正规化和索引更新范围决定可匹配的内容，命中不等于业务相关。

**例子：** 中文分词规则变化后，旧索引需按兼容策略重建或迁移。

**深入阅读：** [倒排索引与全文检索：词都命中了，为什么仍不是想要的结果](../knowledge/cache-search/inverted-indexes-analysis-and-relevance.md) · [索引重建、增量追赶与切换：怎样覆盖期间的新增和删除](../knowledge/cache-search/index-rebuild-watermarks-and-cutover.md)

<a id="cache-search.bm25"></a>

## BM25 / Full-text Search

**ID：** `cache-search.bm25` · **建议优先级：** P0

**别名 / 检索词：** BM25、Full-text Search、全文检索、词频、文档频率、TF、DF

**简释：** 全文匹配与相关性排序分别负责候选和次序；正文概述 BM25 的词频、集合及长度因素，不提供完整评分实现。

全文检索先确定匹配候选，再用 BM25 等方法评分。BM25 综合词频、文档频率与长度因素，分数不是可信度概率，跨查询或索引的原始分数也不能随意比较。

**例子：** 某词在一篇文档出现很多次，得分提升通常会饱和而非无限线性增长。

**深入阅读：** [倒排索引与全文检索：词都命中了，为什么仍不是想要的结果](../knowledge/cache-search/inverted-indexes-analysis-and-relevance.md)

<a id="cache-search.vectors"></a>

## Embedding / Similarity Search

**ID：** `cache-search.vectors` · **建议优先级：** P0

**别名 / 检索词：** Embedding、Similarity Search、向量索引、余弦相似度、Cosine Similarity、Inner Product、L2 Distance、嵌入向量、相似度检索

**简释：** 用兼容空间中的距离或相似度比较向量，区分编码质量、归一化与精确搜索基线。

Embedding 把内容映射到向量空间，检索按指定度量比较向量。模型、预处理、维度和归一化必须兼容，向量接近不保证事实支持或权限合格。

**例子：** 余弦相似度与内积在归一化条件下才有可对应的排序关系。

**深入阅读：** [RAG：检索到了资料，为什么仍会答错](../knowledge/ai/rag-retrieval-and-grounding.md) · [向量索引与近似检索：找到了相似项，为什么仍会漏掉近邻](../knowledge/cache-search/vector-indexes-metrics-and-approximate-search.md)

<a id="cache-search.ann"></a>

## ANN / HNSW

**ID：** `cache-search.ann` · **建议优先级：** P0

**别名 / 检索词：** ANN、HNSW、近似近邻、近似检索、Approximate Nearest Neighbor、IVF、Product Quantization、PQ、近邻召回率、efSearch、nprobe

**简释：** 通过图探索、分区或量化交换查询/空间成本与近邻覆盖；过滤和精确基线有各自前提。

ANN 用近似搜索换取速度或空间收益；HNSW 用图探索，IVF 用分区，量化压缩表示。需要用同一语料与度量下的精确基线测量召回和资源成本。

**例子：** 提高 efSearch 可能改善近邻覆盖，同时增加查询工作量与延迟。

**深入阅读：** [向量索引与近似检索：找到了相似项，为什么仍会漏掉近邻](../knowledge/cache-search/vector-indexes-metrics-and-approximate-search.md)

<a id="cache-search.hybrid"></a>

## Hybrid Search / Reranking

**ID：** `cache-search.hybrid` · **建议优先级：** P0

**别名 / 检索词：** Hybrid Search、Reranking、混合召回、混合检索、重排、RRF、Reciprocal Rank Fusion、Cross-Encoder、Bi-Encoder、候选窗口

**简释：** 对齐多路候选身份后融合排名或校准分数，再对有限输入重排；截断、相关性与来源支持分别检查。

混合检索合并关键词与向量等候选，RRF 可按排名融合，重排模型再对有限候选评分。要统一文档身份和权限，候选被截断后重排无法找回它们。

**例子：** 先联合词项与向量候选并去重，再重排并核对最终片段是否支持答案。

**深入阅读：** [RAG：检索到了资料，为什么仍会答错](../knowledge/ai/rag-retrieval-and-grounding.md) · [混合召回与重排：分数更高，为什么仍救不回遗漏的资料](../knowledge/cache-search/hybrid-retrieval-fusion-and-reranking.md)

<a id="cache-search.objects"></a>

## Object Storage / Presigned URL

**ID：** `cache-search.objects` · **建议优先级：** P0

**别名 / 检索词：** Object Storage、Presigned URL、对象存储、预签名 URL

**简释：** 按键和可选版本保存对象，通过有范围与期限的签名请求能力访问。

对象键、版本ID、ETag、checksum与业务归属各有用途。以S3通用桶为参照，单键一致性不构成跨键/数据库共同发布，分段上传须核对最终完成结果。预签名URL可重复使用且受请求范围、凭据和当前存储策略约束；到期或业务撤销不自动终止在途下载，也不追回已有字节。

**例子：** URL写明12:10到期，但临时凭据12:06到期，则示例中的新请求期限受12:06约束；已接受的下载与业务数据库撤销需另行判断。

**深入阅读：** [对象存储与预签名访问：文件上传后怎样成为可用的业务对象](../knowledge/cache-search/object-storage-versions-uploads-and-presigned-access.md)

<a id="cache-search.index-cutover"></a>

## Index Rebuild / Index Cutover

**ID：** `cache-search.index-cutover` · **建议优先级：** P1

**别名 / 检索词：** Index Rebuild、Index Cutover、索引重建、索引切换

**简释：** 以快照与增量覆盖明确源状态边界，再发布新的索引代次，并安排在途请求、回退和旧代次回收。

重建需让全量视图与持续变更无缺口衔接；应用水位表示此前应处理变化均已完成，多分区进度不能取最大值代替。版本规则与删除保留避免旧回填覆盖新状态，别名或代次指针只负责相应范围的发布。

**例子：** G2 从与变更流配对的快照加载，重放之后的新增、更新和删除；达到发布边界且可搜索后切换读别名，并在回退窗口继续维护 G1。

**深入阅读：** [索引重建、增量追赶与切换：怎样覆盖期间的新增和删除](../knowledge/cache-search/index-rebuild-watermarks-and-cutover.md)

<a id="cache-search.coalescing"></a>

## Request Coalescing / Singleflight

**ID：** `cache-search.coalescing` · **建议优先级：** P1

**别名 / 检索词：** Request Coalescing、Request Collapsing、Singleflight、同键加载合并、缓存加载合并

**简释：** 让可复用结果的同键重叠请求共享一项在途工作。

请求合并是抑制重复在途加载的策略；Go singleflight 是以 Group 和键划定范围的具体机制，不保存历史缓存，也不自动协调跨进程或管理应用取消、容量与回填资格。合并键须表达参数和权限下的结果等价，普通缓存踩踏、批量请求和分布式锁不是它的同义词。

**例子：** 同一实例的多个获准读者共享公开商品数据加载，各自按期限等待；结果不同的租户价格查询使用不同键。

**深入阅读：** [缓存加载合并与惊群控制：少回源为何仍需容量和回填边界](../knowledge/cache-search/cache-load-coalescing-and-stampedes.md)

## 资料与延伸

下列资料提供相关机制的进一步说明，并不表示覆盖本页所有术语。各条已关联的专题文章另列具体来源、适用版本与验证边界。

- [Redis：数据结构](https://redis.io/docs/latest/develop/data-types/)
- [Introduction to Information Retrieval：倒排索引与检索](https://nlp.stanford.edu/IR-book/)
- [PostgreSQL 18：逻辑解码、快照与变更流](https://www.postgresql.org/docs/18/logicaldecoding-explanation.html)
- [Elasticsearch：Reindex 复制范围](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-reindex)
- [Elasticsearch：别名与多动作结果](https://www.elastic.co/docs/manage-data/data-store/aliases)
- [Go singleflight package documentation](https://pkg.go.dev/golang.org/x/sync/singleflight)
- [RFC 9111: HTTP Caching](https://www.rfc-editor.org/rfc/rfc9111.html)
- [AWS Caching challenges and strategies](https://aws.amazon.com/builders-library/caching-challenges-and-strategies/)
- [Cloudflare Sometimes I cache: implementing lock-free probabilistic caching](https://blog.cloudflare.com/sometimes-i-cache/)
- [Hazelcast 5.6: Building a Cache with MapStore](https://docs.hazelcast.com/hazelcast/5.6/mapstore/working-with-external-data)
- [Hazelcast 5.6: Configuring a MapStore](https://docs.hazelcast.com/hazelcast/5.6/mapstore/configuration-guide)
- [Hazelcast 5.6: Implementing a Custom MapStore](https://docs.hazelcast.com/hazelcast/5.6/mapstore/implement-a-mapstore)
- [Ehcache 3.11: Cache Usage Patterns](https://www.ehcache.org/documentation/3.11/caching-patterns.html)
- [Ehcache 3.11: Cache Loaders and Writers](https://www.ehcache.org/documentation/3.11/writers.html)
- [Redis ZRANGE](https://redis.io/docs/latest/commands/zrange/)
- [Redis HGETALL](https://redis.io/docs/latest/commands/hgetall/)
- [Redis Transactions](https://redis.io/docs/latest/develop/using-commands/transactions/)
- [Redis Lua scripting](https://redis.io/docs/latest/develop/programmability/eval-intro/)
- [Redis EXPIRE](https://redis.io/docs/latest/commands/expire/)
- [Redis HEXPIRE](https://redis.io/docs/latest/commands/hexpire/)
- [Redis Cluster specification](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/)
- [Redis SCAN](https://redis.io/docs/latest/commands/scan/)
- [Redis Persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/)
- [Redis XACK](https://redis.io/docs/latest/commands/xack/)
- [S3 object keys](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-keys.html)
- [S3 copying and moving objects](https://docs.aws.amazon.com/AmazonS3/latest/userguide/copy-object.html)
- [S3 consistency model](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html)
- [S3 conditional writes](https://docs.aws.amazon.com/AmazonS3/latest/userguide/conditional-writes.html)
- [S3 upload integrity](https://docs.aws.amazon.com/AmazonS3/latest/userguide/checking-object-integrity-upload.html)
- [S3 multipart upload overview](https://docs.aws.amazon.com/AmazonS3/latest/userguide/mpuoverview.html)
- [S3 CompleteMultipartUpload API](https://docs.aws.amazon.com/AmazonS3/latest/API/API_CompleteMultipartUpload.html)
- [S3 presigned URLs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html)
- [S3 Versioning](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Versioning.html)
- [etcd 3.6 并发 API](https://etcd.io/docs/v3.6/dev-guide/api_concurrency_reference_v3/)
- [Kleppmann 对分布式锁的原始分析](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html)
- [Chubby 原论文](https://storage.googleapis.com/gweb-research2023-media/pubtools/4444.pdf)
- [Redis锁模式说明](https://redis.io/docs/latest/develop/clients/patterns/distributed-locks/)

[返回分类词汇表](index.md) · [完整术语索引](../glossary.md)
