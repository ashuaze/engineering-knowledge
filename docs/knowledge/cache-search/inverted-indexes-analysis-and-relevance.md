---
id: "kb-cache-search-inverted-index"
title: "倒排索引与全文检索：词都命中了，为什么仍不是想要的结果"
kind: "concept"
domain: "cache-search"
status: "evolving"
summary: "从词项到倒排表解释布尔和短语查询，区分分词契约、词频统计、BM25 排序及文档版本与访问边界。"
created: "2026-10-20"
updated: "2026-10-20"
last_verified: "2026-10-20"
verification: "source-checked"
prerequisites: ["kb-algorithms-sorting-boundaries", "kb-algorithms-hash-tables"]
related: ["kb-algorithms-trie", "kb-database-lsm", "kb-database-indexes-plans", "kb-ai-rag", "kb-security-object-authorization", "kb-ai-memory-versioning", "kb-cache-search-vector-indexes", "kb-cache-search-hybrid-reranking"]
tags: ["inverted-index", "full-text-search", "tokenization", "bm25"]
---

# 倒排索引与全文检索：词都命中了，为什么仍不是想要的结果

学习入口：文档同时包含两个搜索词，是否就匹配这个短语？排在第一位，又是否证明内容正确、最新且可以返回？前置：[有序列表与比较成本](../algorithms/sorting-binary-search-and-boundaries.md)、[哈希与精确键](../algorithms/hash-tables-collisions-and-key-contracts.md)。本文用固定英文词项解释倒排结构，并以 PostgreSQL 18 [全文检索](../../glossary/cache-search.md#cache-search.bm25)作机制对照；未运行检索服务或评分实验。

## 从文档找词，反转为从词找文档

文档到词项的表示回答“这篇文档有哪些词”；[倒排索引](../../glossary/cache-search.md#cache-search.inverted)回答“这个词项出现在哪些文档”。典型结构包含词项字典和各词项对应的倒排表 Postings List。表项可含文档标识，还可保存词频、位置等信息；不是把整篇正文按字符倒着存。结构参照[信息检索教材：建立倒排索引](https://nlp.stanford.edu/IR-book/html/htmledition/a-first-take-at-building-an-inverted-index-1.html)。

下面是自设、固定且无[并发](../../glossary/systems.md#systems.concurrency)修改的三篇文档。只按空格切开已有小写 ASCII 单词，不去停用词、不做词干化或同义词扩展；位置从 1 开始，指词项位置而非字节偏移。每篇有唯一编号：

| 文档 | 完整词项序列 |
| --- | --- |
| D1 | [cache invalidation](../../glossary/cache-search.md#cache-search.invalidation) cache |
| D2 | cache eviction |
| D3 | invalidation cache update |

相应的位置倒排表为：

```text
cache        → D1:[1,3]，D2:[1]，D3:[2]
eviction     → D2:[2]
invalidation → D1:[2]，D3:[1]
update       → D3:[3]
```

倒排表中的文档编号按同一全局次序排列。一篇文档重复出现某词，可以归在同一文档表项下，记录多个位置或词频；不能因此把它当作多篇文档。

## 求交得到共同文档，位置才回答短语

cache AND invalidation 对两个文档列表求交，结果为 D1、D3；cache OR invalidation 求并，结果为 D1、D2、D3。这里显式规定运算符，没有声明实际搜索框默认采用 AND 或 OR。

已排序且每篇文档只出现一次的两个列表，长度为 m、n，双指针比较可在 O(m+n) 的上界内求交：相等就输出并同时前进，不等就推进较小编号。这个模型假定单次编号比较成本有界，不含词项字典查找、列表解压、位置检查、原文取回和排序成本，机制见[布尔查询处理](https://nlp.stanford.edu/IR-book/html/htmledition/processing-boolean-queries-1.html)。常见词的列表仍可能很长，存在索引不等于查询总是常数成本。

本例严格相邻短语 "cache invalidation" 还要求 invalidation 的位置恰好比某个 cache 大 1：D1 的 1→2 满足；D3 只有 invalidation 在 1、cache 在 2，顺序相反，不满足。只有文档编号而没有位置或原文等额外核对，无法完成这一步。位置机制见[位置索引](https://nlp.stanford.edu/IR-book/html/htmledition/positional-indexes-1.html)；带停用词、同义词或距离容差的短语语义应另行定义。

## 分析规则决定了什么能匹配

Token 是某次切分出的实例，Term 是纳入字典的词项类型，通常经过规范化。切分、大小写处理、词干化、停用词及同义词决定索引能保留哪些区别；相关问题见[分词说明](https://nlp.stanford.edu/IR-book/html/htmledition/tokenization-1.html)。中文没有英文式空格边界，不能直接套用本文的空格切分模型。

查询和索引需要兼容的分析契约。本例查 cach 不会命中 cache；若要前缀、子串、拼写纠错或同义匹配，需要相应扩展或额外索引。[Trie](../algorithms/tries-prefix-search-and-key-encoding.md)可辅助词项前缀定位，但前缀词项命中之后仍要读取相应倒排表，不等于已经找到最相关文档。

PostgreSQL 18 用 to_tsvector 按配置把文本转换为词项及位置，用查询解析函数生成 tsquery，见[文档与查询控制](https://www.postgresql.org/docs/18/textsearch-controls.html)。它的英文配置与本例的原样词项规则不同，本文表格不是该配置的执行输出。更换词典或分词规则，应评估重建与新旧查询兼容，不能只改查询侧就默认旧索引同时改变。

## 布尔匹配与相关性排序是两层问题

另一条相似检索路径见[向量索引与近似检索](vector-indexes-metrics-and-approximate-search.md)，多路结果继续读[混合召回与重排](hybrid-retrieval-fusion-and-reranking.md)。词项匹配、数值近邻、融合名次和最终支持关系各有前提；本次关联没有新增全文或向量实测。

布尔匹配回答哪些文档满足条件，排序决定先展示谁。Term Frequency（TF）是词在某文档中的出现次数；Document Frequency（DF）是含该词的文档数。本例 cache 在 D1 的 TF 为 2，整个集合的 DF 为 3；invalidation 的 DF 为 2。重复词影响 TF，却不会把同一文档的 DF 计两次。

BM25 是常见词项相关性评分模型，利用词的集合分布、文档内词频和长度等信息；词频贡献通常饱和，长文归一化由模型参数控制，参照[教材 BM25](https://nlp.stanford.edu/IR-book/html/htmledition/okapi-bm25-a-non-binary-model-1.html)。这不是“重复越多就无限领先”，也不是事实正确、[授权](../../glossary/security.md#security.identity)或答案有据的概率。比较时先固定查询词及组合方式，具体公式、统计范围、字段权重与参数也会影响分数；本例没有给定完整[评分规则](../../glossary/ai.md#ai.eval-rubric)，因此不推出 D1、D3 的最终排名。

PostgreSQL 18 自带 ts_rank 和 ts_rank_cd，后者考虑覆盖密度与位置；不能只因使用倒排索引就称其为 BM25。匹配、评分与结果排序需要分别指定，具体见其[排序说明](https://www.postgresql.org/docs/18/textsearch-controls.html#TEXTSEARCH-RANKING)。不同查询、集合或检索器的分数也不能未经校准就当作同一尺度比较。

## 索引组织与文档生命周期分别保证

倒排结构描述词项到文档的映射，不规定底层必须用某一种存储引擎；[LSM](../database/lsm-sstables-and-compaction.md)描述有序数据的写入与合并，二者不在同一个选择层次。词项字典、倒排表、压缩块、增量段与原文可以有不同表示。

PostgreSQL 的 [GIN 全文索引](https://www.postgresql.org/docs/18/textsearch-indexes.html)是具体倒排实现；其索引并不存储所有查询所需信息，例如涉及词项权重标签的条件需要回查表行。不要把纸面位置倒排表等同于 GIN 的完整物理格式，也不能由“有索引”推出评分、短语检查和返回原文都无需额外工作。

若 D1 被修改为只含 eviction，仍沿用旧倒排表就会为 cache 返回陈旧候选。需要删除或屏蔽旧版本，建立新版本的词项，并定义发布与读取视图；复制一份新原文不等于索引同步。PostgreSQL 的[表与索引说明](https://www.postgresql.org/docs/18/textsearch-tables.html)给出表达式索引和生成列的维护方式；独立搜索服务的数据同步、刷新和重建切换仍需自己的协议。

结果中的文档标识、片段和缓存还要符合当前版本及[访问权限](../security/object-level-authorization.md)。检索评分不能授予权限；在原文进入模型或返回之前就应落实读取边界，不能先泄露再期待[重排](../../glossary/cache-search.md#cache-search.hybrid)过滤。进入 [RAG](../ai/rag-retrieval-and-grounding.md) 后，还需检查内容对当前问题的支持关系，关键词命中只提供检索信号。

自检：索引保留的是词项、词频还是位置？查询默认怎样组合？短语是否保留顺序和间隔？新词典是否对应新索引？低排名、未召回、旧版本与无权返回怎样分别定位？

2026-10-20 核查信息检索教材的倒排构建、布尔处理、分词、位置和 BM25 章节，以及 PostgreSQL 18 全文检索文档，状态为 source-checked。D1–D3、倒排表和结果均为纸面推演；未执行中文分词、全文索引、评分、[查询计划](../../glossary/database.md#database.plans)、重建同步、向量或混合检索实验。
