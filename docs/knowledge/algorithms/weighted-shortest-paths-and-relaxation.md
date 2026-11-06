---
id: "kb-algorithms-weighted-paths"
title: "加权最短路与松弛：先到达一个节点，为什么还不能确定最优"
kind: "concept"
domain: "algorithms"
status: "evolving"
summary: "用松弛、不变量和负权反例区分 BFS、DAG 路径、Dijkstra 与 Bellman-Ford，并说明负环、路径恢复和实现成本。"
created: "2026-10-20"
updated: "2026-10-20"
last_verified: "2026-10-20"
verification: "source-checked"
prerequisites: ["kb-algorithms-graphs", "kb-algorithms-trees-heaps", "kb-algorithms-complexity"]
related: ["kb-algorithms-greedy", "kb-algorithms-dynamic-programming", "kb-algorithms-union-find-mst", "kb-cache-search-vector-indexes", "kb-engineering-property-state-models"]
tags: ["shortest-path", "relaxation", "dijkstra", "bellman-ford", "negative-cycle"]
---

# 加权最短路与松弛：先到达一个节点，为什么还不能确定最优

学习入口：找到一条可达路径，或第一次发现目标，是否已经找到最低成本路线？前置：[图遍历](graphs-traversal-and-dependency-order.md)、[堆与优先队列](trees-heaps-and-priority-queues.md)。本文限定有限、计算期间固定的有向图，边权有限且可相加；算术与比较按有界成本模型分析，图和步骤为纸面设计，没有运行路径算法。

## 最少边数与最小权重是不同目标

路径成本是沿途边权之和。若 S→T 成本为 9，S→A 和 A→T 分别为 2、3，[BFS](../../glossary/algorithms.md#algorithms.graph-traversal) 找到的一条边路线并非成本最小的路线。BFS 的最少边数保证适合无权或相同正权模型；把普通[队列](../../glossary/algorithms.md#algorithms.queues)替换成堆后，也不能沿用“首次发现就结束”的规则。

距离可有三类结果：不可达记为 +∞；存在有限最优值；若从源点能进入[负权环](../../glossary/algorithms.md#algorithms.shortest-path)，再从环到达目标，允许重复经过节点时成本可无限降低，记为 −∞。图里另一个不相关的负环，不会使所有目标都失去有限答案。这里讨论允许重复经过的路线，不是限定节点不重复的最短简单路径问题。定义参照 [MIT 加权路径讲义](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/resources/mit6_006s20_lec11/)。

## 松弛保留已经找到的更好路线

用 d[v] 表示当前距离估计：初始 d[S]=0，其他为 +∞。若 d[u] 有限，边 u→v 权重为 w，且 d[u]+w 小于 d[v]，就更新 d[v] 并记录前驱。这一步叫松弛。有限估计来自已经找到的某条路线，因此在有限最优值存在时是其上界；它还不等于已经最优。

算法的关键区别在于按什么顺序松弛、什么时候能停止更新。对 DAG，按拓扑顺序处理节点出边，前驱先处理，负权也不会产生环；包括[排序](../../glossary/algorithms.md#algorithms.sorting-search)和初始化可为 O(V+E)。对一般非负权图，Dijkstra 使用距离顺序；存在负权时则需要其他依据。

## Dijkstra 确认的是最小估计的取出时刻

Dijkstra 每次从尚未确认的节点中取出估计最小者，再松弛出边。非负权使后续绕行不能从一个更大的前缀成本降回来：考虑一条可能更优路线，进入未确认集合的第一条边，其已确认前驱已经完成松弛；这个候选不会大于该路线的后续成本。结合当前取出者最小，可以证明取出时估计已最优。完整论证与队列模型见 [MIT Dijkstra 讲义](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/resources/mit6_006s20_lec13/)。

纸面边集仅有 S→A:7、S→B:2、B→A:1、A→T:2、B→T:8：

| 当前取出并确认 | 松弛后的关键变化 |
| --- | --- |
| S，距离 0 | A=7，B=2 |
| B，距离 2 | A 改为 3，T=10 |
| A，距离 3 | T 改为 5 |
| T，距离 5 | 最优路线为 S→B→A→T |

A 首次发现时是 7，后来才成为 3；T 首次发现时是 10，确认时是 5。只求 T 时，可在有效的最小条目取出并确认 T 后停止，不能在首次把它放入队列时停止。

若队列支持 decrease-key，可更新同一节点的优先级。若每次改善都另插一个条目，旧的 A=7、T=10 仍可能留在堆里；取出时必须跳过过期条目，不能重复把旧距离当作新结论。[二叉堆](../../glossary/algorithms.md#algorithms.trees)的并列项还需可比较的稳定辅助序号等安排，不能要求任意业务对象天然可排序。

本文的 Dijkstra 保证要求源点可达子图的所有边非负，检查全图边均非负是更直接的充分条件；零权允许存在。负权反例：S→A:2、S→B:5、B→A:−4。算法会先确认 A=2，但实际路线 S→B→A 成本为 1；没有负环也足以破坏该确认规则。允许重新打开节点的其他实现不能继续直接引用同一正确性与复杂度保证。

## Bellman-Ford 通过反复松弛处理负权

对源点可达且不受负环影响的目标，存在一条有限最短路线，可去掉无益的重复环，保留至多 V−1 条边。Bellman-Ford 的常见原地版本反复扫描所有边，只从有限估计更新：至多 V−1 遍后，再检查是否仍有边能严格改善；若有，则说明存在源点可达负环。某一完整遍没有变化时可提前停止。原理与分层解释见 [MIT Bellman-Ford 讲义](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/resources/mit6_006s20_lec12/)。

原地扫描可能在同一遍连续传播多条边，不能说“第 k 遍后恰好等于至多 k 条边的最优值”；每层只读上一层的版本才有这个精确状态含义。扫描次序会影响中间值与提前停止时机，不改变满足前提后的最终保证。

例如 S→A:1、A→B:−2、B→A:0、B→T:3。A→B→A 每绕一次减少 2，T 也受影响；额外孤立点 Z 仍不可达。要给每个节点分类，发现可改善边还不够，需要把影响沿可达关系传播；未立即改善的后继也可能是 −∞，不能直接给它有限答案。若 X→Y:−1、Y→X:0 与 S 完全隔离，单源检查不会把这个环算成 S 的可达负环；检查全图需要另行覆盖所有分量。

## 成本要和数据结构一起说明

这里 V、E 包含孤立节点与全部边，图存储另计；以下是所列实现的上界，不是运行秒数：

| 方法及实现 | 时间口径 | 辅助空间与限制 |
| --- | --- | --- |
| DAG 拓扑松弛 | O(V+E) | O(V)，必须无环 |
| 二叉堆及可定位的 decrease-key | O((V+E) log(V+2)) | O(V)，邻接扫描与数值操作按有界成本 |
| 改善就入堆的非负权版本 | O(V+E log(E+2)) | O(V+E)，最多量级 E 个改善条目，须跳过旧项 |
| 原地 Bellman-Ford 扫描 | O(V+VE) | O(V)，距离/前驱；分类负环影响另加 O(V+E) 遍历 |

恢复一条路线还需要沿前驱回溯并付出输出长度成本；并列最优不保证路线唯一，也不枚举全部最优路线。零权环下尤其不能任意把所有等长边都设为前驱。使用浮点数、无穷哨兵或固定宽度整数时，还应单独处理 NaN、精度与溢出，不能直接照搬理想算术证明。

动态拥塞、容量约束、多目标费用或随时间改变的代价可能不符合固定可加边权。图搜索也不自动等于[向量近邻检索](../cache-search/vector-indexes-metrics-and-approximate-search.md)；最短路与[最小生成树](union-find-components-and-minimum-spanning-trees.md)的优化目标不同。

自检：边是否非负，图是否无环？终止点是发现、有效取出还是全轮收敛？负环能否从源点到达、再影响目标？堆里是否有旧条目？输出需要距离、一条路线还是全部路线？

2026-10-20 核查 MIT 6.006 加权路径、Dijkstra 与 Bellman-Ford 讲义，状态为 source-checked。边集、距离与复杂度展开为教学推演；未执行路径算法、负环分类、堆操作或性能实验。
