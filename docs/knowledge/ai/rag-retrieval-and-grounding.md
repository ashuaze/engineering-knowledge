---
id: "kb-ai-rag"
title: "RAG：检索到了资料，为什么仍会答错"
kind: "concept"
domain: "ai"
status: "evolving"
summary: "区分索引、召回、重排、上下文组装与生成，解释相关性、来源支持、权限及新鲜度的不同保证。"
created: "2026-10-19"
updated: "2026-10-20"
last_verified: "2026-10-19"
verification: "source-checked"
prerequisites: []
related: ["kb-ai-context", "kb-ai-evals", "kb-cache-search-cache-aside", "kb-security-object-authorization", "kb-reliability-telemetry", "kb-ai-tool-security", "kb-ai-tools-lab", "kb-ai-memory-versioning", "kb-ai-memory-access-deletion", "kb-ai-memory-lab", "kb-cache-search-inverted-index", "kb-cache-search-vector-indexes", "kb-cache-search-hybrid-reranking"]
tags: ["rag", "retrieval", "grounding"]
---

# RAG：检索到了资料，为什么仍会答错

学习入口：回答有文档引用，内容却不适用当前版本，该换模型还是改检索？前置知识：文档索引、查询与模型上下文。本文限定一类常见 [RAG](../../glossary/ai.md#ai.rag)：查询时取回外部资料，将其组织进生成模型的上下文；不覆盖全部联合训练检索架构，也不提供已部署的向量服务。

## 检索给资料，生成组织回答

RAG 是 Retrieval-Augmented Generation，即检索增强生成。外部资料可以在不重新训练生成模型的情况下进入本次输入，帮助回答特定领域问题；资料不是自动写进模型参数，也不是回答必然正确的保证。[官方准确性优化说明](https://developers.openai.com/api/docs/guides/optimizing-llm-accuracy#retrieval-augmented-generation-rag)区分了检索提供的上下文和模型如何使用它这两类问题。

可以先画出两条路径：

```text
入库：权威资料 → 解析与分块 → 附加来源、版本和访问属性 → 建立索引
查询：确认主体与问题 → 在允许范围内召回 → 合并、重排、组装上下文
      → 生成候选回答 → 检查关键声明与来源支持 → 返回或说明缺少依据
```

这是教学架构。具体产品可能合并其中一些步骤，但排查时仍需要知道：资料有没有进入可搜索集合，候选中有没有正确片段，实际送入模型的又是什么。

## 分块保留什么，索引就能查到什么

[Chunking](../../glossary/ai.md#ai.grounding) 把文档切成可索引、可取回的片段。过小可能把“仅适用于 2.4 版”与规则正文分开；过大则可能带入大量噪声，挤占上下文。重叠有机会保留跨边界信息，也会增加存储与重复候选。不存在对所有文档都合适的固定长度。

分块时应保留标题、原文位置、文档及版本标识，并明确表格、代码和附注怎样关联。解析若已经丢掉表头或否定词，之后只调相似度通常无法恢复原始语义。官方 [File search](https://developers.openai.com/api/docs/guides/tools-file-search)展示了一种把文件索引与检索集成的实现；其中的默认行为应按具体服务核查，不能当作通用分块标准。

[Embedding](../../glossary/ai.md#ai.embeddings) 是把数据表示为向量，[向量索引](../../glossary/cache-search.md#cache-search.vectors)提供相应的检索结构。语义接近的表达可能在指定向量空间里更近，但距离不是事实真假的概率。同维度向量也不代表来自兼容空间；更换编码模型或处理规则，需要评估索引迁移与对照，不能把旧、新向量随意混用。[Embedding 指南](https://developers.openai.com/api/docs/guides/embeddings)说明了向量表示与相似性用途。

## 召回与重排的目标不同

近邻定义、[ANN](../../glossary/cache-search.md#cache-search.ann) 与过滤继续见[向量索引与近似检索](../cache-search/vector-indexes-metrics-and-approximate-search.md)，去重、[RRF](../../glossary/cache-search.md#cache-search.hybrid)、候选窗口与 Cross-Encoder 见[混合召回与重排](../cache-search/hybrid-retrieval-fusion-and-reranking.md)。两篇为来源核查与纸面推演，不构成本文真实索引、模型或回答效果的实验结果。

词项匹配的基础继续读[倒排索引与全文检索](../cache-search/inverted-indexes-analysis-and-relevance.md)，区分分析规则、布尔条件、短语位置与相关性分数。其[倒排表](../../glossary/cache-search.md#cache-search.inverted)是纸面推演，不构成本文真实索引、向量或回答质量的实验结果。

召回先从集合中找到候选；重排在这些候选里按当前问题调整顺序。后者不能凭空找回从未进入候选、也未另外补取的关键资料。

| 路径 | 有帮助的场景 | 需要检查的限制 |
| --- | --- | --- |
| 关键词检索 | 精确标识、版本号、错误码和术语重合 | 不同表达可能没有相同关键词 |
| 向量检索 | 同义表达、语义相近的问法 | 主题相近的旧版本或否定描述也可能靠前 |
| 混合检索 | 同时利用文字匹配与语义信号 | 合并规则、去重和排序仍需验证 |
| 重排 | 比较候选对当前问题的适用程度 | 增加计算成本，仍受候选覆盖限制 |

[Retrieval 文档](https://developers.openai.com/api/docs/guides/retrieval)说明了语义检索、属性过滤与排序选项，可用于理解这些实现环节。不同检索器的分数不能未经校准就直接相加，分数阈值也不自动表示“答案有足够依据”。增大 [Top-k](../../glossary/algorithms.md#algorithms.trees) 可能提高候选覆盖，也可能带入更多重复或不适用资料，应该分别观察。

## 有引用、相关与有据不是一回事

Grounding 在本文指关键回答能得到所用资料的支持。引用标识存在，只说明回答给出了引用；还要验证引用可解析、指向正确记录与版本，并检查资料是否支持具体声明、条件是否匹配、来源是否有效。忠实复述旧版或错误文档，也可能对当前问题不正确。

教学问题：“2.4 版接口撤销后，新请求是否立即被拒绝？”假设资料由本地产品定义，以下规则与结果完全虚构。

| 候选资料 | 内容 | 对当前问题的意义 |
| --- | --- | --- |
| D1，1.9 版旧说明 | 等待原凭证到期 | 主题相关，版本不适用 |
| D2，2.4 版当前说明 | 撤销提交后，新请求查会话状态并拒绝 | 支持新请求规则，不证明已开始的任务会中止 |
| D3，2.4 版附注 | 已开始的[长任务](../../glossary/frontend.md#frontend.long-tasks)另按执行策略处理 | 补足问题的适用边界 |

若只召回 D1，是版本与检索问题；D2 已在候选，却因重复内容挤占预算而没送入模型，是组装问题；D2、D3 都已送入，仍回答“所有运行中任务立刻停止”，则超出了来源支持。对缺少权威说明的部分，应说明不确定或继续查询，不能让模型补成已确认事实。

## 权限与更新必须进入数据路径

在原文或片段进入模型、返回结果和日志明细前，应保证当前主体有权访问相应内容。租户、文档范围和有效版本的约束需要由可信策略决定；客户端自己填写的 tenant_id 不能直接成为[授权](../../glossary/security.md#security.identity)依据。检索引擎支持属性过滤，只提供实现手段，不等于应用已经正确授权。

若先把未授权资料交给模型，再要求它“不要引用”，内容已经进入错误的数据路径。共享缓存、引用预览和下载入口也需要保持相同访问边界，详见[对象级授权](../security/object-level-authorization.md)。

资料更新后，源文件、切[分片](../../glossary/database.md#database.partitioning)段、向量索引与回答缓存可能不同步。需要能够追踪文档版本、解析及编码版本、删除状态和索引更新时间，并明确过渡期间哪些结果允许返回。给回答设 TTL 不能独自保证权限撤销或文档删除立即生效，相关时序可对照[缓存与失效](../cache-search/cache-aside-and-invalidation.md)。

检索文本还可能包含试图改变系统行为的指令。资料应按不可信数据处理，不能因来自搜索结果就提升为高优先级指令或工具执行授权。[Agent 安全说明](https://developers.openai.com/api/docs/guides/agent-builder-safety)讨论了这种注入路径。提示、结构化约束与权限隔离各有作用，单一提示不能承诺完全消除风险。

外部内容进入执行链路时，继续读[工具授权与不可信结果](tool-authorization-and-untrusted-results.md)及[本地边界实验](tool-execution-boundaries-lab.md)，区分检索数据、模型候选和可信执行许可。

记忆同样有[版本与失效](memory-versions-conflicts-and-expiry.md)、[权限与删除](memory-access-revocation-and-deletion.md)问题。[记忆治理实验](memory-governance-lab.md)用字符串索引替身验证旧候选排除，不是本文向量召回或回答质量的实测。

## 按阶段留下证据，再评价回答

调查一次错误时，保留必要的查询约束、候选片段及版本、排序、实际上下文、最终声明与引用关系。明细的访问和保留遵守数据策略，不把所有原文放进指标标签或公开日志。

先看正确证据是否在可见资料库，再看它是否被召回、进入上下文、被正确使用。检索覆盖与回答有据应分别评价；还需评价无答案时是否克制、越权内容是否被排除，以及端到端[延迟](../../glossary/performance.md#performance.latency-throughput)与成本。评价口径见 [Evals 与失败分析](evals-and-failure-analysis.md)。

试着解释：相似度很高为何仍可能是错误版本？增大 Top-k 为什么不必然让答案更好？有引用为什么仍可能无依据？模型拒绝引用为何不能修复前面的越权检索？

核查日期：2026-10-19。本文参考官方检索、向量、文件搜索、准确性与安全资料；流程和 D1–D3 为教学设计。没有生成 Embedding、构建索引、调用模型或测量检索与回答指标。

- [Token、上下文与记忆](tokens-context-and-memory.md)：约束实际放入资料的预算和状态来源。
- [日志、指标与链路](../reliability/logs-metrics-and-traces.md)：把阶段证据关联到同一次请求，避免用聚合值代替明细。
