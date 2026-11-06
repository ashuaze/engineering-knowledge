---
id: "kb-cache-search-vector-indexes"
title: "向量索引与近似检索：找到了相似项，为什么仍会漏掉近邻"
kind: "concept"
domain: "cache-search"
status: "evolving"
summary: "区分向量空间、距离与精确基线，解释 HNSW、IVF、量化、过滤及近邻召回率的保证范围。"
created: "2026-10-20"
updated: "2026-10-22"
last_verified: "2026-10-20"
verification: "source-checked"
prerequisites: ["kb-algorithms-trees-heaps", "kb-algorithms-graphs"]
related: ["kb-cache-search-inverted-index", "kb-cache-search-hybrid-reranking", "kb-ai-rag", "kb-ai-evals", "kb-ai-memory-versioning", "kb-ai-memory-access-deletion", "kb-cache-search-index-cutover"]
tags: ["vector-index", "ann", "hnsw", "ivf", "quantization"]
---

# 向量索引与近似检索：找到了相似项，为什么仍会漏掉近邻

学习入口：数据库里有正确资料，向量检索为什么没有返回？是编码、距离、索引还是过滤出了问题？前置：[Top-K 与候选维护](../algorithms/trees-heaps-and-priority-queues.md)、[图与遍历](../algorithms/graphs-traversal-and-dependency-order.md)。本文解释实数向量的检索模型，参照 Faiss、[HNSW](../../glossary/cache-search.md#cache-search.ann) 论文及 pgvector 0.8.7 文档；数值和集合均为纸面推演，没有生成 [Embedding](../../glossary/cache-search.md#cache-search.vectors) 或运行索引。

## 向量表示与搜索结构负责不同事情

Embedding 把文本等对象映射为向量；索引组织已有向量，减少查询时的工作。索引可以更快地找到指定空间里的近邻，却不能修复编码模型已经丢掉的版本号、否定条件或领域含义。[RAG](../ai/rag-retrieval-and-grounding.md)中的“相关资料”与数值近邻因此需要分别检验。

查询和文档向量需要来自兼容的空间及处理契约，包括模型版本、查询/文档编码方式、维度与归一化。同维度只说明长度相同，不能证明坐标含义兼容；不同的查询与文档编码器也只有经过相应配对设计才可直接比较。不能通过随意补零、截断或混入新模型向量来完成索引迁移。

## 先定义“近”，再谈有没有漏

设查询 q 与候选 x 都为同维度、各分量有限的向量。本例只有非零向量，使用普通内积和欧氏范数：

| 比较方式 | 定义 | 优先方向 |
| --- | --- | --- |
| 内积 | q·x，即对应分量乘积之和 | 越大越优先 |
| 平方 L2 | 各分量差的平方之和 | 越小越优先 |
| 余弦相似度 | (q·x) / (‖q‖‖x‖) | 越大越优先 |

纸面查询 q=(1,0)，候选 A=(10,0)、B=(1,1)、C=(-1,0)：

| 候选 | 内积 | 平方 L2 | 余弦相似度 |
| --- | --- | --- | --- |
| A | 10 | 81 | 1 |
| B | 1 | 1 | 1/√2，约 0.707 |
| C | -1 | 4 | -1 |

未归一化时，内积和余弦在本例都把 A 放在最前，L2 却先选 B，不能把距离名称当作可随意互换的参数。平方根是非负距离的单调变换，因此 L2 与平方 L2 的排序相同，数值却不同。Faiss 返回平方 L2，具体契约见其[距离说明](https://github.com/facebookresearch/faiss/wiki/MetricType-and-distances)。

若查询与候选都按 L2 范数归一化为单位向量，则平方 L2=2−2×内积，内积也等于余弦；这才给出相应排序等价条件。零向量不能按此归一化，也没有上述余弦定义，需要拒绝或另定处理规则。相似度 0.9 仍不是“内容有九成概率正确”。

## 精确基线固定集合，近似搜索限制工作

对固定数据视图和符合当前过滤条件的集合，逐项计算约定距离，再按距离与明确的并列规则选前 k 个，可建立精确 [Top-K](../../glossary/algorithms.md#algorithms.trees) 基线。这里的“精确”针对给定向量、数值实现与排序规则，不代表业务相关性绝对正确。直接遍历 N 个 d 维向量的距离工作通常按 O(Nd) 分析，还要计入选择、存储访问和返回成本。

ANN 是 Approximate Nearest Neighbor，近似近邻搜索；它可能只访问部分候选，或用有损表示估算距离，以交换时间、空间与近邻覆盖。精确查询也可受益于[批处理](../../glossary/performance.md#performance.batching)或硬件优化，小集合并不必然值得引入近似索引。Faiss 的[索引类型说明](https://github.com/facebookresearch/faiss/wiki/Faiss-indexes)区分 Flat 精确搜索与相应近似结构；建好了索引不等于每次搜索都遍历了全集。

## HNSW、IVF 与量化改变的是不同环节

HNSW 将向量组织为多层邻近图，通常先在较稀疏的高层导航，再在低层扩大候选探索；不用比较每个向量，路径和预算也可能使真正近邻未被访问。分层结构见 [Malkov 与 Yashunin 的论文](https://arxiv.org/abs/1603.09320)。它与 [BFS](../../glossary/algorithms.md#algorithms.graph-traversal) 的“稳定图上最少边数路径”不是同一个检索目标，不能把某种数据上的速度曲线当作任意输入的固定[延迟](../../glossary/performance.md#performance.latency-throughput)保证。

在 Faiss HNSW 的术语中，M 涉及图的邻接规模，efConstruction 控制构建时的探索，efSearch 控制查询时的探索；它们分别影响内存、构建与查询成本，efSearch 不是最终返回数 k。更多探索通常用更多工作换取覆盖机会，但不能据一个参数值承诺所有数据都达到某召回率，参照 [Faiss 参数取舍](https://github.com/facebookresearch/faiss/wiki/How-to-make-Faiss-run-faster)。

IVF（Inverted File）先把向量分配到若干粗分区，查询时选择部分分区检查。Faiss 用 nlist 表示分区数量、nprobe 表示查询探查数量；真正近邻所在分区没有被选中，就可能漏掉。这里的“倒排”按向量分区组织，不等于[全文检索](inverted-indexes-analysis-and-relevance.md)的词项到文档映射；分区也不保证等长，不能把 nprobe/nlist 直接当作实际访问比例。

量化则用较短编码近似表示向量。PQ（Product Quantization，乘积量化）分别编码子向量，可以节省部分存储，但估算距离也会有误差，机制见 [Faiss 有损压缩说明](https://github.com/facebookresearch/faiss/wiki/Lower-memory-footprint)。即使扫描全部压缩编码，也不必等于按原始向量得到精确结果；用原向量重新比较已选候选，只能修正这些候选内的次序，不能找回此前被排除的向量。分区、码本训练与模型训练也应分别记录，不能把 HNSW 图构建和所有索引都称为同一种训练。

## 先取前 k 个，再过滤，可能不足 k 个

纸面反例：全体记录按约定距离的前五名是 X、Y、A、B、C，其中 X、Y 不在本次允许范围内。先取全体前三名再过滤，只剩 A；在允许集合内做精确前三名，本应得到 A、B、C。

过滤前后的位置会改变候选覆盖。预先限制集合、搜索过程中结合过滤、取候选后过滤是不同实现；不能把一个产品的流程推广成所有向量引擎。pgvector 0.8.7 的[过滤与迭代扫描说明](https://github.com/pgvector/pgvector/blob/v0.8.7/README.md#filtering)指出，近似索引扫描后过滤可能使返回不足，迭代扫描仍受其预算上限约束。它不意味着只要增大搜索预算就一定得到足够或全局精确的结果。

“范围内只有一个对象”“检索只找到一个”“[超时](../../glossary/api.md#api.retries)后只保留一个”应留下不同状态。[授权](../../glossary/security.md#security.identity)、版本和删除属于当前读取约束，不能为凑够 k 而放宽；未经许可的内容也不应先送给[重排](../../glossary/cache-search.md#cache-search.hybrid)模型，再指望模型过滤。

索引在持续更新下怎样重建和替换，见[索引重建与切换](index-rebuild-watermarks-and-cutover.md)；近邻召回评估所用的数据与索引版本也要明确对应。

## 近邻召回率与业务相关性要分别量化

本文约定：同一查询、数据视图、过滤条件、距离和并列规则，允许集合至少有 k 个对象，k>0；E_k 是精确前 k 个的唯一标识集合，R_k 是近似返回的至多 k 个唯一标识。集合 Recall@k 定义为：

```text
近邻 Recall@k = |E_k ∩ R_k| / k
```

纸面例 E_2={A,B}，R_2={A,C}，近邻 Recall@2=1/2。缺少的结果不能靠重复标识补足；允许集合不足 k、为空或存在大量并列时，应先另定分母与处理规则，再跨查询汇总。这是本文口径，不表示所有基准中名为 recall 的指标都相同。

精确近邻也可能与业务问题不相关；若用户所问的版本条件没有正确进入读取约束，数值上最近的资料也可能是相对于该问题的错误版本。精确算法不会自行补齐这个条件，因此还要用业务标注检查[相关性与回答质量](../ai/evals-and-failure-analysis.md)。分别保存近邻覆盖、相关性、[尾延迟](../../glossary/performance.md#performance.percentiles)、内存、构建/更新成本，并说明数据分布和过滤选择性；只报告平均速度或几个看起来不错的结果，不足以判断取舍。

更新时还需关联文档/片段标识、源版本、模型与处理版本、索引代次和删除状态。重建切换要覆盖期间的增量，读取与缓存遵守当前权限；相关责任见[记忆版本与失效](../ai/memory-versions-conflicts-and-expiry.md)和[权限与删除](../ai/memory-access-revocation-and-deletion.md)。某个库能添加向量，不表示它也支持相同方式的删除、[并发](../../glossary/systems.md#systems.concurrency)更新或恢复。

自检：近邻以哪个空间和距离定义？是没有访问到，还是估算距离排错？过滤在哪一步发生？精确基线和近似查询是否比较同一集合？索引召回率高，为什么仍需相关性标注？

2026-10-20 核查 Faiss 官方 Wiki、HNSW 原论文及 pgvector 0.8.7 README，状态为 source-checked。坐标、排序、过滤及 Recall 均为纸面推演；未安装或运行向量库、生成 Embedding、构建/训练索引、执行过滤/量化/更新或测量召回与性能。
