---
id: "kb-algorithms-union-find-mst"
title: "并查集与最小生成树：连通成本最低，为什么路线未必最短"
kind: "concept"
domain: "algorithms"
status: "evolving"
summary: "区分集合代表与真实路径，解释合并、路径压缩和摊还成本，再以 Kruskal 与割性质说明最小生成树的目标和边界。"
created: "2026-10-20"
updated: "2026-10-20"
last_verified: "2026-10-20"
verification: "source-checked"
prerequisites: ["kb-algorithms-graphs", "kb-algorithms-trees-heaps", "kb-algorithms-sorting-boundaries"]
related: ["kb-algorithms-greedy", "kb-algorithms-weighted-paths", "kb-algorithms-complexity", "kb-engineering-property-state-models"]
tags: ["union-find", "disjoint-set", "mst", "kruskal", "amortized"]
---

# 并查集与最小生成树：连通成本最低，为什么路线未必最短

学习入口：需要低成本连通全部站点，能否反复选最便宜的边？得到的树能否再当作任意两点间的最短路线？前置：[图与连通](graphs-traversal-and-dependency-order.md)、[树](trees-heaps-and-priority-queues.md)、[排序](sorting-binary-search-and-boundaries.md)。本文限定有限、计算期间固定的无向加权图；集合、边集与步骤为纸面推演，没有运行连通算法或建网实验。

## 并查集保存分组，不保存原图路线

[并查集](../../glossary/algorithms.md#algorithms.union-find)（Disjoint Set Union，Union-Find）维护互不相交集合。make-set 建立单元素集合，find 返回所在集合的代表，union 合并两个集合；同集合中任意两元素的 find 结果相同。这里的“代表”是结构标识，不是业务领导者、最小编号或永久 ID，合并后可以改变。基础模型见 [MIT 并查集讲义](https://ocw.mit.edu/courses/6-046j-design-and-analysis-of-algorithms-spring-2012/resources/mit6_046js12_lec16/)。

常见表示是父指针森林：根指向自身，find 沿父指针找到根，union 先找两个根，已经相同则不再合并。直接把任意非根的父指针改到另一个节点，可能拆坏已有分组或产生环；合并操作要维护结构[不变量](../../glossary/systems.md#systems.atomicity)。

纸面初始 {A}、{B}、{C}、{D}、{E}，五个分量。合并 A/B，再合并 C/D，分量变为 {A,B}、{C,D}、{E}；再合并 B/C 得 {A,B,C,D}、{E}，共两个。重复合并 A/D 不再减少分量。每次只合并不同根时，分量计数才减一。

父指针是分组的内部表示，不是输入图的边。比如上述第三次输入边为 B—C，合并却可能把根 C 指向根 A，即使原图没有 A—C 这条边。之后路径压缩还会改父指针；不能沿这棵内部树输出真实线路、距离或生成树边，所选图边需要另行保存。

## 合并策略与路径压缩共同控制成本

随意合并可形成长链，单次 find 最坏走过量级 n 个节点。按大小把小树根接到大树根，或按秩合并，可控制树高；秩是结构维护量，有路径压缩后不必等于当前真实高度。路径压缩则在 find 时把经过节点改指向根，使后续查询更短，逻辑分组不变。

因此 find 虽然逻辑上是查询，实现中也可能写父指针；不能未经设计就让多个[线程](../../glossary/systems.md#systems.execution-units)无同步共用。并查集也不自动支持删除一条图边后的分裂；回滚、持久化与动态连通需要额外机制，不能靠把某个父指针清空来还原任意历史合并。

按秩/大小与路径压缩组合后，建立 n 个元素再执行 m 次合并/查询，常用上界为 O(n+mα(n))，α 是增长很慢的反阿克曼函数；这是操作序列的摊还界，不是每一次都严格常数时间。[数组](../../glossary/algorithms.md#algorithms.sequences)索引、比较与指针操作按有界成本，空间 O(n)。组合优化与分析口径参照 [MIT Union-Find 与摊还材料](https://ocw.mit.edu/courses/6-046j-design-and-analysis-of-algorithms-spring-2015/d25d9d3ba96321326601c8f6dd073e60_MIT6_046JS15_Recitation3.pdf)。

## 最小生成树优化的是全部选边总和

对连通图，生成树要覆盖所有 V 个顶点、连通且无环，恰含 V−1 条边。[最小生成树](../../glossary/algorithms.md#algorithms.mst)（MST）在所有生成树中最小化边权总和，没有指定一个源点，也不最小化每对节点间的距离。无向图、生成树及安全选边性质见 [MIT 最小生成树讲义](https://ocw.mit.edu/courses/6-046j-design-and-analysis-of-algorithms-spring-2012/resources/mit6_046js12_lec03/)。

如果输入不连通，就不存在覆盖全部节点的一棵生成树；可分别求各连通分量的最小生成树，得到最小生成森林，孤立节点也保留。负权边可以参与 MST：树不会无限重复绕环，不能把[最短路负环](weighted-shortest-paths-and-relaxation.md)的无下界结论搬过来。相同边权可能导致多个最优树；边权全异是唯一性的充分条件，不是存在最优树的条件。

## Kruskal 用并查集拒绝形成环的边

Kruskal 先把边按权重升序排列；依次检查 u—v，若 find(u) 与 find(v) 不同就接纳该边并合并，否则跳过。连通图接纳 V−1 条后即可结束；不连通时需保留森林结果。算法与成本参照 [MIT Kruskal 材料](https://ocw.mit.edu/courses/6-046j-design-and-analysis-of-algorithms-spring-2012/resources/mit6_046js12_lec04/)。

纸面图仅有四个顶点，边按以下次序给出，所有权重不同：

| 扫描边与权重 | 动作 | 原因 |
| --- | --- | --- |
| A—B:1 | 接纳 | 不同分量 |
| B—C:2 | 接纳 | 不同分量 |
| A—C:3 | 跳过 | A、C 已连通，会形成环 |
| C—D:4 | 接纳 | D 仍独立 |
| B—D:6 | 无需继续 | 已有 3 条边并连通全部 4 点 |

所得树为 A—B、B—C、C—D，总权重 7。若只是“挑最轻的 V−1 条边”，会取前三条，把 D 留在外面。并查集检查负责无环与分量合并，权[重排](../../glossary/cache-search.md#cache-search.hybrid)序及安全选边论证负责最优性；只满足其中一项不够。

## 割性质连接合法选择与整体最优

把顶点分成两个非空部分称为一个割。设当前已选森林 F 能扩展为某棵 MST，选择一个没有 F 中边跨越的割。该割的最轻跨边 e 是安全候选：若某棵包含 F 的 MST 没有 e，加上 e 会出现环；这个环有另一条跨割边 f，且 f 不属于 F，权重不小于 e。用 e 换掉 f，仍为生成树、保留 F，权重不增加，因此存在一棵 MST 包含 F 和 e。

Kruskal 当前连接两个分量的最轻可接纳边，符合相应分量割的条件。证明保证可以把当前森林继续扩展成最优树；有并列时，不声称某一条最轻边必属于所有 MST。对比 [贪心交换论证](greedy-choices-and-exchange-arguments.md)，安全条件必须和当前约束一起说明。

## 树的形状和完整工作量仍有边界

最小总连通成本不保证最短路线。另一个独立纸面三角形：A—B:2、B—C:2、A—C:3。MST 取前两条，总和 4；但其 A 到 C 路线长度为 4，比原图直接边的 3 更长。单源最短路径树、最小生成树和并查集内部森林是三个不同对象。

比较[排序](../../glossary/algorithms.md#algorithms.sorting-search)按有界成本，Kruskal 包含 O(V) 初始化、O(E log(E+2)) 排序和 O(Eα(V)) 摊还集合操作，不能忽略无边的孤立节点；输入、排序缓冲、并查集和输出分别计空间。若边早已排序，也只是省掉该项，不会使读边、初始化与集合维护免费。

自环无法连接两个分量，应跳过；平行边需按各自身份和权重处理，不能随意按端点覆盖。确定排序中的并列规则可帮助复现，但不使最优树变得数学上唯一。真实网络还可能要求[冗余](../../glossary/reliability.md#reliability.fault-domains)、方向、容量或故障域分散；一棵树的总费用最优不代表满足这些额外条件。

自检：find 得到的是分量代表还是图中路线？重复 union 是否改错计数？输入是否连通、是否要求返回森林？安全边来自哪个割？输出要全局连通总成本还是指定源点距离？

2026-10-20 核查 MIT 6.046J 并查集、摊还、最小生成树与 Kruskal 材料，状态为 source-checked。分组、四点扫描、三角形和成本展开为自设纸面推演；未执行并查集、生成树、动态删除、[并发](../../glossary/systems.md#systems.concurrency)或性能实验。
