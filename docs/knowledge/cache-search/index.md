<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# 缓存、检索与对象存储

建议优先级：P0。目标：设计快速读取、失效、相关性与大对象访问。

下方术语用于知识索引。建议从[实际工程问题](../../problems.md)或本页核心问题进入，结合已有正文理解机制、适用边界与相关概念。

## 一个核心问题

缓存失效时，如何避免回源请求压垮数据库？

## 已有正文

- [Cache-Aside 与失效：缓存为什么会返回旧数据](cache-aside-and-invalidation.md)：区分缓存读取、权威写入、失效与过期，分析旧值回填和回源的边界。

## 术语范围

| 术语 | 简释 |
| --- | --- |
| Cache Aside / Read Through | 应用管理缓存或由缓存层加载数据。 |
| Write Through / Write Behind | 写入同步持久化或延后异步写回。 |
| Cache Invalidation / TTL | 主动失效与按时过期。 |
| Penetration / Breakdown / Avalanche | 不存在键回源、热点失效和批量失效问题。 |
| Cache Stampede | 并发未命中引发重复加载与回源放大。 |
| Redis Data Structures | 按访问语义选择字符串、哈希、集合、有序集合和流。 |
| Distributed Lock / Lease | 跨节点互斥及有期限的持有权。 |
| Inverted Index | 从词项定位包含它的文档。 |
| BM25 / Full-text Search | 基于词项统计的相关性排序与全文检索。 |
| Embedding / Similarity Search | 向量表示与距离或相似性查找。 |
| ANN / HNSW | 近似近邻搜索及分层图索引。 |
| Hybrid Search / Reranking | 组合多种召回并重新评分排序。 |
| Object Storage / Presigned URL | 按对象保存数据与限时签名访问。 |

## 练习与验收

选择上面的一个核心问题，先画执行过程或数据边界，再构造一个正常路径和一个失败路径。用原理解释、架构或代码、诊断证据和取舍依据说明保证范围；记录已完成验证与待验证项。

[回到知识地图](../../map.md) · [问题导航](../../problems.md) · [学习路径](../../paths/index.md)
