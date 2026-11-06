---
id: "kb-cache-search-hybrid-reranking"
title: "混合召回与重排：分数更高，为什么仍救不回遗漏的资料"
kind: "concept"
domain: "cache-search"
status: "evolving"
summary: "解释多路候选、去重、分数与排名融合、Cross-Encoder 重排及分阶段评价，明确截断、权限和失败边界。"
created: "2026-10-20"
updated: "2026-10-20"
last_verified: "2026-10-20"
verification: "source-checked"
prerequisites: ["kb-cache-search-inverted-index", "kb-cache-search-vector-indexes"]
related: ["kb-ai-rag", "kb-ai-evals", "kb-ai-context", "kb-security-object-authorization", "kb-ai-memory-versioning", "kb-performance-backpressure"]
tags: ["hybrid-search", "rank-fusion", "rrf", "reranking", "cross-encoder"]
---

# 混合召回与重排：分数更高，为什么仍救不回遗漏的资料

学习入口：关键词和向量都接入了，为什么关键片段仍没进入最后结果？该增大哪一层候选，还是更换[重排](../../glossary/cache-search.md#cache-search.hybrid)模型？前置：[倒排与词项排序](inverted-indexes-analysis-and-relevance.md)、[向量与近似检索](vector-indexes-metrics-and-approximate-search.md)。本文给出通用流程和自设排名，参照 RRF 论文、Elastic、Sentence Transformers 及信息检索教材；不提供已部署的混合搜索或模型效果结论。

## 多路召回先扩大候选，再决定先看谁

关键词路径可利用名称、错误码、版本号等词项信号；向量路径利用指定空间中的相似关系。混合召回把不同路径的结果结合起来，可能补充覆盖，但各路也可能一起漏掉文档、返回重复片段或偏好旧版。两路不必然比一路质量好，需在实际查询分布上比较。

下面流程是教学设计，分别保留候选与截断边界：

```text
查询与当前允许范围
  ├→ 词项召回 ─┐
  └→ 向量召回 ─┴→ 对齐身份、去重与融合 → 取重排候选
                 → 重排 → 取最终结果/上下文 → 核对支持关系
```

查询理解、召回范围、候选合并、重排和上下文选择不是同一操作。模型无法修复从未进入其输入的片段；如果还有补取、改写查询或再次搜索，那是新增召回路径，应单独计入预算与评价。阶段划分可对照 [Retrieve & Re-Rank](https://www.sbert.net/examples/sentence_transformer/applications/retrieve_rerank/README.html)。

## 身份对齐后再合并，分数不能直接混用

同一个候选应能追踪租户、文档、版本和片段标识。两个检索器返回相同片段，通常在融合结果中只保留一项，同时保存各路排名；不能把两个不同版本仅因标题相同就合并，也不应让同一路的重复标识反复加分。多个片段属于同一文档时，还需定义文档级聚合、去重和证据覆盖，不能默认删掉所有后续片段。

[BM25](../../glossary/cache-search.md#cache-search.bm25) 分数、[余弦相似度](../../glossary/cache-search.md#cache-search.vectors)、负内积或距离不在同一尺度，优先方向也可能相反。加权分数融合需先明确方向、归一化或校准方法、权重与缺席值；单次查询的 min-max 等变换也不自动给出跨查询的可信概率。统一成“越大越好”只是必要步骤，不足以证明分数可相加。

按排名融合可避开直接比较原始分值，但会丢掉分值间隔信息，也仍依赖候选窗口与融合参数。重复接入高度相似的检索路径还可能重复强化同一偏好，多路一致不是独立事实证据。

## 用 RRF 手算一次融合

Reciprocal Rank Fusion（RRF，倒数排名融合）依据候选在各路列表中的名次累加分数。其基础公式见 [Cormack、Clarke、Büttcher 的论文](https://cormack.uwaterloo.ca/cormacksigir09-rrf.pdf)；对有限返回列表的处理可参照 [Elastic RRF](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion)。本文采用等权、每路同一标识只计一次，名次从 1 开始，未出现在该路窗口内的候选贡献为 0：

```text
RRF(d) = 对包含 d 的各路 r 求和 [1 / (c + rank_r(d))]
```

c 是平滑名次影响的正常数，不是返回条数；较大的 c 会减弱不同名次贡献之间的差距。本文约定融合前各路先按候选唯一标识去重，保留首次出现的次序并重新从 1 编号，再使用该名次。下面为便于手算设 c=10，绝非产品默认值或通用推荐。两路各返回三项、无并列，A–D 为同一有效数据视图下的四个唯一片段，均在允许范围内：

| 召回路径 | 从前到后的排名 |
| --- | --- |
| 关键词 | A、B、C |
| 向量 | B、D、A |

| 候选 | 关键词贡献 | 向量贡献 | 合计约值 |
| --- | --- | --- | --- |
| A | 1/11 | 1/13 | 0.1678 |
| B | 1/12 | 1/11 | 0.1742 |
| C | 1/13 | 0 | 0.0769 |
| D | 0 | 1/12 | 0.0833 |

融合顺序为 B、A、D、C；两路各三项不等于六个不同候选，合并后只有四项。RRF 不是精确匹配优先规则，也没有给“答案正确”的概率。本例只改变正数 c 不会改变排序；对其他排名组合，调整 c 可能改变结果。各路窗口、权重或并列策略也会影响融合；有些实现还在融合前截断列表，不能只调整最终返回数来补救，窗口含义见上述 Elastic 文档。

## 重排只能处理实际交给它的候选

若上述流程融合后只取前两项交给重排器，它收到的是 B、A。即使 D 恰好是当前问题需要的关键说明，重排器也只能重新安排 B、A，不能找回 D；丢失发生在融合后的截断。若 C 原本因各路窗口过小根本没进入并集，则是更早的覆盖问题。保留各阶段标识，才能把两者区分开。

Bi-Encoder 通常分别编码查询和文档，文档表示可预先计算；Cross-Encoder 则联合读取查询与候选，按查询—候选对计算相关性，因此常用于较小候选集合的重排。其成本与候选数量、输入长度、模型和[批处理](../../glossary/performance.md#performance.batching)有关，不能宣称“只排序不增加计算”。机制参照 [Cross-Encoder 用法](https://www.sbert.net/docs/cross_encoder/usage/usage.html)。

重排分数可能是 logit，也可能经过激活转换，不能统一理解为 0–1 概率，更不是正确性或当前权限的证明。输入截断可能丢掉候选后半段的条件；版本、领域与语言变化也需要对照评价。本文没有给 B、A 指定模型分数或新的次序，不伪造重排执行结果。

各路深度、[ANN](../../glossary/cache-search.md#cache-search.ann) 探索预算、融合窗口、重排条数、最终返回数和[上下文预算](../ai/tokens-context-and-memory.md)应分别命名。提高其中一个，可能增加等待或重复内容，却不改变另一个已截断的窗口。一路[超时](../../glossary/api.md#api.retries)也不等于该路查得零项；允许降级时应记录缺失路径和规则，不能把不完整融合伪装成完整执行。

## 评价每个阶段，而不只看最后一句答案

近似向量检索的近邻 Recall@k 以精确向量结果为参照；业务相关性需要另有标注集合 G。若 G 非空，候选覆盖可按“候选集中包含的相关唯一项数 / |G|”检查。这个分母来自业务标注，与近邻基线或返回数量不同。

继续纸面例，额外假设评价语料只有 A–D，四项均已完成本查询的二元相关性判定，相关集合 G={A,D}，B、C 已判为不相关。四项并集覆盖了两项，候选相关性召回为 1；融合前两项 {B,A} 只覆盖 A，相关性 Recall@2=1/2，Precision@2=1/2。若重排仍只接收 B、A，就无法恢复 D，但可能把 A 提前，从而改变前一位的体验。此处未定义或执行任何模型来证明一定改善。

有序结果还可用 Precision@n、nDCG@n 等口径检查前部质量与等级相关性，分别说明截断位置、标注等级、并列和无相关项时的规则；nDCG 的实际计算还需固定增益、折扣和理想排序约定。此处只介绍评价目的，完整定义参照[无序集合评价](https://nlp.stanford.edu/IR-book/html/htmledition/evaluation-of-unranked-retrieval-sets-1.html)及[排序评价](https://nlp.stanford.edu/IR-book/html/htmledition/evaluation-of-ranked-retrieval-results-1.html)。未标注项不自动等于不相关；不能只挑成功问题，也不能把相关性分数当作回答被来源支持的度量。

至少对照关键词单路、向量单路、融合、融合加重排，在相同数据视图、允许范围和明确预算下比较。按精确标识、同义问法、版本条件、无答案等查询分类，保存各阶段候选、去重依据、原始分数/排名、模型及参数，以及[延迟](../../glossary/performance.md#performance.latency-throughput)与资源成本；评价原则继续见 [Evals](../ai/evals-and-failure-analysis.md)。

## 当前许可和版本不能交给排序决定

各路使用可信的读取范围，在候选原文进入重排器、生成模型、日志或返回结果前落实相应许可。重排器同样是数据接收方，不能把它视为泄露后的补救边界；访问控制继续见[对象级授权](../security/object-level-authorization.md)。缓存还需绑定主体范围、数据与模型/融合版本，权限或文档更新后处理旧候选和迟到写回。

融合排名高不证明来源当前有效，也不保证文档支持答案中的每个条件。最终上下文选择仍可能挤掉关键片段，后续生成还可能超出证据；这些问题继续由 [RAG 的版本与支持关系](../ai/rag-retrieval-and-grounding.md)分别检查，不能都归到重排模型。

自检：候选在哪个窗口丢失？重复项以什么身份合并？分数的方向和尺度是什么？重排实际看到了哪段文字？质量指标的分母来自精确近邻还是业务标注？一路超时如何呈现？

2026-10-20 核查 RRF 原论文、Elastic RRF、Sentence Transformers 及信息检索教材，状态为 source-checked。A–D、融合值与相关集合为教学设计；未运行检索器、融合服务、Cross-Encoder、生成模型、质量标注流程或延迟/成本实验。
