---
id: "kb-algorithms-graphs"
title: "图遍历与依赖顺序：找到可达节点，为什么还不能安排执行"
kind: "concept"
domain: "algorithms"
status: "evolving"
summary: "区分图表示、BFS 与 DFS、无权最短路和环检测，并说明拓扑顺序、重复访问和依赖完成的边界。"
created: "2026-10-20"
updated: "2026-10-20"
last_verified: "2026-10-20"
verification: "source-checked"
prerequisites: ["kb-algorithms-complexity", "kb-algorithms-linear-structures", "kb-algorithms-hash-tables"]
related: ["kb-algorithms-trees-heaps", "kb-runtime-modules-cycles", "kb-architecture-module-boundaries", "kb-ai-workflow-routing", "kb-engineering-property-state-models", "kb-algorithms-weighted-paths", "kb-algorithms-dynamic-programming", "kb-algorithms-union-find-mst"]
tags: ["graph", "bfs", "dfs", "topological-sort", "dependency"]
---

# 图遍历与依赖顺序：找到可达节点，为什么还不能安排执行

学习入口：依赖扫描能找到全部模块，为什么仍可能排出错误的启动顺序？前置：[复杂度](complexity-and-data-structures.md)、[队列](sequences-stacks-queues-and-deques.md)和[键查找](hash-tables-collisions-and-key-contracts.md)。本文以有限、遍历期间不改变的图为模型，Python 3.13 片段为教学设计，未执行遍历或调度实验。

## 边的含义必须先固定

图由顶点和边表示关系。先问边是否有方向、是否带权、能否重复，以及“u→v”究竟表示 u 依赖 v，还是 u 必须先于 v。两种约定都可使用，但建图、算法与输出解释必须一致。

邻接表通常以 O(V+E) 空间保存节点及其出边；邻接矩阵通常占 O(V²)，但按位置判断某条边存在有不同的成本。这里 V、E 分别是节点和边数，孤立节点也要计入，不可只从边推断全部任务。基础模型见 [MIT BFS](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/resources/mit6_006s20_lec9/)。

## BFS 的队列保持层次

[BFS](../../glossary/algorithms.md#algorithms.graph-traversal) 广度优先遍历先发现距起点一条边的节点，再发现更远层。对无权图或相同正权的边，它得到最少边数路径；不是任意[加权最短路](../../glossary/algorithms.md#algorithms.shortest-path)。教学反例：A→D 权重 10，A→B 与 B→D 各为 1；最少一条边的路径成本 10，却不是最小总权重 2。

以下片段假设源点存在于 adj，所有邻居也都是其键；节点可哈希、身份稳定，邻接关系是出边。每条边成本均视为 1，字典和[队列](../../glossary/algorithms.md#algorithms.queues)操作按有界/预期常数模型分析。函数不验证这些输入前提：

```python
from collections import deque

def bfs(adj, source):
    distance = {source: 0}
    parent = {source: None}
    pending = deque([source])
    while pending:
        u = pending.popleft()
        for v in adj[u]:
            if v not in distance:
                distance[v] = distance[u] + 1
                parent[v] = u
                pending.append(v)
    return distance, parent
```

关键是在入队时标记发现，避免多个父节点在出队前反复把同一节点加入。parent 保存一条最短路径树，不枚举全部路径；要实际输出某个目标的路径，还需回溯并付出相应输出成本。

纸面图为 A→B、A→C、B→D、C→D、D→B，A 的邻居按 B、C 顺序枚举。从 A 开始，发现顺序 A、B、C、D，距离为 0、1、1、2，D 的父为 B；环不会使节点无限入队。换邻居顺序可能改变所选父节点，而不改变最少边数。孤立节点 Z 不会从 A 被发现，不能据此说图中不存在 Z。

## DFS 沿一条路径深入，但要区分状态

DFS 深度优先遍历可用递归或显式栈推进，适合分析到达、完成和祖先关系。它找到的第一条路径不保证最短；深链还可能超过[运行时](../../glossary/runtime.md#runtime.virtual-machine)递归限制，不能把递归写法当作任意规模都安全。

对有向图环检测，需要区分尚未发现、正在当前探索路径、已经完成。指向当前探索路径上节点的边（包括自环）能揭示环；仅仅“再次遇到一个见过的节点”还不够，菱形依赖共享同一后继也会重复相遇，却可以无环。无向图还要正确处理回到父节点的边，不能机械复制有向判定。机制见 [MIT DFS](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/resources/mit6_006s20_lec10/)。

## 拓扑顺序回答前置约束

下面另用依赖图，固定 u→v 表示 u 必须先完成、v 才可开始：P→R、Q→R、R→S。有效拓扑顺序可为 P、Q、R、S 或 Q、P、R、S，通常不唯一。

入度消除法先找入度为零的节点，移除一个后减少其后继入度，重复推进；若所有节点都被移除，就得到顺序。若还有节点却已无零入度项，剩余图包含环；剩余节点也可能只是被环[阻塞](../../glossary/systems.md#systems.blocking)的后继，不能把它们全部认定为环成员。

若图有环，就无法让环中每条“必须先完成”的边同时满足。DFS 的逆完成顺序只有在有向无环条件满足时，才能用作相应拓扑顺序；图有环时不能仍当作合法调度结果。Python 3.13 的 [graphlib](https://docs.python.org/3.13/library/graphlib.html)提供拓扑工具，其输入映射为“节点到前驱集合”，使用时必须与自己的边方向约定对齐。

## 顺序计划与业务完成分开

加权目标继续见[最短路与松弛](weighted-shortest-paths-and-relaxation.md)，子问题计算顺序见[动态规划](dynamic-programming-states-and-dependency-order.md)，分量合并及全局连通成本见[并查集与最小生成树](union-find-components-and-minimum-spanning-trees.md)。发现节点、确认距离、状态求值和业务完成各有依据；关联没有新增遍历或执行器实测。

从结构中移除前置节点，只是拓扑算法的模拟步骤。真实[并行](../../glossary/systems.md#systems.concurrency)执行时，要等前置工作按约定成功完成，再释放其后继；失败、[重试](../../glossary/api.md#api.retries)、取消、资源额度及副作用恢复还需执行器管理。找到一条可达路径或调用了一次任务，不等于依赖结果已经可用。例子可继续看[模块初始化环](../runtime/modules-bindings-and-circular-dependencies.md)和[工作流交接](../ai/workflow-routing-and-handoff-contracts.md)。

在邻接表及有界操作模型下，覆盖全图的 BFS/DFS 可分析为 O(V+E)，入度消除也可达这一量级；单源遍历只覆盖可达部分。遍历元数据和队列/栈最坏占 O(V)，图存储另计；若改用矩阵枚举邻居、反复扫描全图或列出全部路径，就不能沿用原有成本。

自检：边表示依赖还是先后？要可达性、最少边数、权重最短路还是调度顺序？发现和完成怎样区分？孤立节点、共享后继、环和重复边如何计入？算法的“移除”在执行器里对应什么可信完成证据？

2026-10-20 核查 MIT 6.006 BFS/DFS 与 Python 3.13 graphlib 文档，状态为 source-checked。BFS、权重反例和依赖图为纸面推演；未执行图算法、环检测、拓扑工具、并行任务或性能实验，未深入 Dijkstra、负权最短路和图索引。
