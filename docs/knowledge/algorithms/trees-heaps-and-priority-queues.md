---
id: "kb-algorithms-trees-heaps"
title: "树、堆与优先队列：能取最小值，为什么不等于已经有序"
kind: "concept"
domain: "algorithms"
status: "evolving"
summary: "区分树形关系、二叉搜索树和平衡条件、二叉堆与优先队列，解释有序查询、堆顶、Top-K 和更新责任。"
created: "2026-10-20"
updated: "2026-10-20"
last_verified: "2026-10-20"
verification: "source-checked"
prerequisites: ["kb-algorithms-complexity", "kb-algorithms-sorting-boundaries"]
related: ["kb-algorithms-linear-structures", "kb-algorithms-hash-tables", "kb-algorithms-graphs", "kb-database-indexes-plans", "kb-performance-backpressure", "kb-algorithms-page-indexes", "kb-algorithms-trie", "kb-algorithms-weighted-paths", "kb-algorithms-union-find-mst"]
tags: ["tree", "binary-search-tree", "heap", "priority-queue", "top-k"]
---

# 树、堆与优先队列：能取最小值，为什么不等于已经有序

学习入口：[容器](../../glossary/devops.md#devops.containers)能快速取最高优先级任务，为什么仍不能直接按顺序遍历或快速查任意 ID？前置：[复杂度](complexity-and-data-structures.md)、[排序与查找](sorting-binary-search-and-boundaries.md)。本文讨论内存中的典型树和[二叉堆](../../glossary/algorithms.md#algorithms.trees)；Python API 限定 3.13，Java 对照限定 21，图与 Top-K 均为纸面推演。

## 二叉只描述形状，搜索还需要规则

有根树可用父子、根、叶和子树描述层级；二叉树限定每个节点最多两个孩子，不自动规定值的大小。二叉搜索树 BST 则增加顺序[不变量](../../glossary/systems.md#systems.atomicity)：本例采用唯一键，左子树所有键小于节点键，右子树所有键大于它。只比较直接孩子还不够，整棵子树都必须满足。

查找沿比较结果选择子树，成本与树高 h 相关，为 O(h)。依次把 1、2、3、4、5 插入未经平衡的普通 BST，可形成向右的链；二叉不等于树高必为 O(log n)。概念参照 [MIT Binary Trees](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/resources/mit6_006s20_lec6/)。

平衡搜索树通过维护条件、旋转等控制树高，同时保留搜索顺序；相关机制见 [MIT AVL](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/resources/mit6_006s20_lec7/)。这不是每次更新都重新[排序](../../glossary/algorithms.md#algorithms.sorting-search)整棵树，也不表示实现无需额外字段和调整成本。Java 21 的 [TreeMap](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/TreeMap.html)以红黑树提供有序映射及相应对数操作契约，不能把这一保证套给任意二叉树。

## 二叉堆只维护局部优先关系

最小二叉堆通常以完全二叉树形状和父值不大于孩子的规则组织；根为最小元素，兄弟和不同子树之间却未必有序。[数组](../../glossary/algorithms.md#algorithms.sequences)表示时，零起点 i 的孩子位置为 2i+1 与 2i+2，超出长度的孩子不存在。

```text
教学最小堆数组：[1, 4, 2, 9, 6, 3]
                 1
              /     \
             4       2
            / \     /
           9   6   3
```

数组是合法最小堆，却不是递增序列，因为 4 在 2 前面。要有序输出，需反复取根并恢复堆，或另行排序；直接遍历内部数组不具备该保证。Python [heapq](https://docs.python.org/3.13/library/heapq.html)采用最小堆，Java [PriorityQueue](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/PriorityQueue.html)也明确其迭代器不保证优先顺序。

## 完整操作决定成本

在有界比较和访问模型下，典型二叉堆查看根 O(1)，插入的上浮和删除根的下沉至多经过 O(log n) 层；数组[扩容](../../glossary/algorithms.md#algorithms.amortized)成本仍另计，不能保证每次实际容器插入都只有这部分工作。自底向上 heapify 建堆为 O(n)，不是把 n 次最坏 O(log n) 插入简单相加得到的唯一建堆方案，参照 [MIT Binary Heaps](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/resources/mit6_006s20_lec8/)。

| 主要需求 | 先考虑什么 | 仍需核算什么 |
| --- | --- | --- |
| 按唯一键查值 | [哈希表](../../glossary/algorithms.md#algorithms.hash-table) | 哈希/相等规则与分散假设 |
| 有序前驱、后继或范围 | 平衡搜索树或有序数组 | 树高、更新与输出数量 |
| 反复取当前最小优先级 | 最小堆 | 修复、并列规则及任务状态 |
| 输出全部排序结果 | 排序或有序遍历 | 仅写出 n 项就需 Ω(n) 工作；反复从堆取根通常共 O(n log n) |

普通堆若未维护额外索引，按 ID 或值查找任意任务通常需扫描，最坏 O(n)；已知位置后，单项优先级改变仍需通过上浮或下沉恢复不变量，至多经过 O(log n) 层。不能只改数组中的优先值，就认为根和后续取出顺序仍正确。

## Top-K 保存的是候选集合

教学目标：输入 [8,3,10,4,7]，保留最大的 3 个数。维持至多 k 个候选的最小堆：未满先加入；满后仅在新值大于根时替换根并修复。根是当前候选中最小的一项，恰好提供新值能否挤入的阈值。

纸面候选依次为 {8}、{3,8}、{3,8,10}、{4,8,10}、{7,8,10}。大括号只表示保留的值及其数量，不表示堆内部排列或已排序输出。这个模型保留重复次数，遇到与根相等的值可忽略该次替换；若还需选择具体记录，必须补并列规则。

对 2≤k≤n，可分析为 O(n log k) 的上界和 O(k) 候选空间；输出为排序结果还要 O(k log k)，k=1 可直接维护一个最大值。本模型只讨论 1≤k≤n，空输入、k=0 或 k>n 的接口行为需另行约定。要最小的 k 项时需改候选策略，不能原样照搬。

## 并列、改优先级与业务执行仍需设计

距离更新的具体场景见[加权最短路](weighted-shortest-paths-and-relaxation.md)：[decrease-key](../../glossary/algorithms.md#algorithms.shortest-path) 或旧条目跳过都需计入正确性和成本。[并查集与最小生成树](union-find-components-and-minimum-spanning-trees.md)则区分内部父指针森林、原图边和输出树，不把树形表示自动解释成最短路线。新文没有新增本文堆或性能实验。

优先队列不自动保证同优先级 [FIFO](../../glossary/algorithms.md#algorithms.queues)。Python heapq 可用“优先级、唯一递增序号、任务”建立并列顺序，并避免比较不可排序的任务对象。改优先级或删除可使用索引堆等机制，或标记旧项无效再插新项；后者需要取出时过滤、检查任务身份并管理旧项积累，依据见 [heapq 实现注意事项](https://docs.python.org/3.13/library/heapq.html#priority-queue-implementation-notes)。

取出队首也不证明任务已执行成功，不保证防饥饿、[截止时间](../../glossary/reliability.md#reliability.retry-budget)或多工作者的业务顺序；容量与接纳继续见[背压](../performance/backpressure-and-bounded-queues.md)。页与前缀结构继续读 [B/B+ 树与页索引](b-trees-bplus-trees-and-page-indexes.md)及 [Trie 与前缀检索](tries-prefix-search-and-key-encoding.md)，其算例仍为纸面推演；堆排序实现与最短路继续待深入。[数据库索引](../database/indexes-and-query-plans.md)的页访问也不等同于本篇[内存模型](../../glossary/systems.md#systems.memory-order)。

自检：需要的是整体有序、按键定位还是一个极值？二叉树靠什么保持高度？堆数组是否真的递增？改优先级后由谁修复？并列和失效项怎样处理？

2026-10-20 核查 MIT 6.006、Python 3.13 heapq 与 Java 21 TreeMap/PriorityQueue，状态为 source-checked。树形、堆数组与 Top-K 为教学设计；未执行平衡树、堆、优先级更新、Top-K 或性能实验。
