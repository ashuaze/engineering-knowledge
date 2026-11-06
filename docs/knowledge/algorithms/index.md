<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# 数据结构与算法

建议优先级：P0。目标：通过访问模式和复杂度选择数据结构。

下方术语用于知识索引。建议从[实际工程问题](../../problems.md)或本页核心问题进入，结合已有正文理解机制、适用边界与相关概念。

## 一个核心问题

为什么[数据库索引](../../glossary/database.md#database.indexes)常用 [B+ 树](../../glossary/algorithms.md#algorithms.b-tree)，向量检索常讨论图索引？

## 已有正文

- [B 树、B+ 树与页索引：树高很低，查询为什么仍然慢](b-trees-bplus-trees-and-page-indexes.md)：从页访问和扇出解释 B/B+ 树，区分分隔键、叶条目、范围扫描、分裂及真实数据库的回表与可见性成本。
- [复杂度与数据结构：如何从访问方式选择存储组织](complexity-and-data-structures.md)：说明渐进复杂度、最坏/期望/摊还成本，并把查找、更新和额外内存放到同一选择中。
- [分治与回溯：怎样拆开问题，又怎样安全地排除分支](divide-and-conquer-backtracking-and-pruning.md)：从子问题契约、递归树和搜索状态解释[分治](../../glossary/algorithms.md#algorithms.divide-conquer)与回溯，区分递归深度、总工作、可行性剪枝、最优界及输出成本。
- [动态规划与状态设计：记住子问题，为什么还会算错](dynamic-programming-states-and-dependency-order.md)：从状态含义、递推与依赖顺序解释[记忆化](../../glossary/algorithms.md#algorithms.dynamic-programming)和表格法，用 0/1 背包说明初始化、循环方向、方案恢复及伪多项式成本。
- [图遍历与依赖顺序：找到可达节点，为什么还不能安排执行](graphs-traversal-and-dependency-order.md)：区分图表示、[BFS](../../glossary/algorithms.md#algorithms.graph-traversal) 与 DFS、无权最短路和环检测，并说明拓扑顺序、重复访问和依赖完成的边界。
- [贪心选择与交换论证：每一步最好，为什么未必整体最优](greedy-choices-and-exchange-arguments.md)：以区间选择和反例解释贪心规则、可行性与最优性的区别，用[交换论证](../../glossary/algorithms.md#algorithms.greedy)说明安全选择及目标变化的边界。
- [哈希表与键契约：查找为什么不是无条件常数时间](hash-tables-collisions-and-key-contracts.md)：解释哈希、相等判断、[碰撞](../../glossary/algorithms.md#algorithms.hash-table)、负载因子和[扩容](../../glossary/algorithms.md#algorithms.amortized)，区分键身份、重复策略与预期复杂度。
- [线性结构与端点操作：数组、链表、栈和队列怎样选择](sequences-stacks-queues-and-deques.md)：从访问位置、修改位置和顺序规则比较[动态数组](../../glossary/algorithms.md#algorithms.sequences)、链表、栈、[队列](../../glossary/algorithms.md#algorithms.queues)与双端队列，解释定位成本和容量语义。
- [排序与二分查找：找到一个位置，为什么仍可能答错](sorting-binary-search-and-boundaries.md)：区分[排序](../../glossary/algorithms.md#algorithms.sorting-search)契约、稳定性与确定顺序，用半开区间和循环不变量解释二分边界、重复值及维护成本。
- [字符串匹配：失配怎样安全回退，位置又按什么计算](string-matching-prefix-functions-and-text-boundaries.md)：用前缀函数解释 [KMP](../../glossary/algorithms.md#algorithms.string-matching) 的失配回退、重叠与跨块匹配，区分符号比较、编码偏移、规范化及哈希候选。
- [树、堆与优先队列：能取最小值，为什么不等于已经有序](trees-heaps-and-priority-queues.md)：区分树形关系、[二叉搜索树](../../glossary/algorithms.md#algorithms.trees)和平衡条件、二叉堆与优先队列，解释有序查询、堆顶、Top-K 和更新责任。
- [Trie 与前缀检索：路径存在，为什么不等于键存在](tries-prefix-search-and-key-encoding.md)：区分完整键、前缀枚举与最长前缀匹配，解释终止标记、字符编码、[路径压缩](../../glossary/algorithms.md#algorithms.union-find)、输出成本与删除责任。
- [并查集与最小生成树：连通成本最低，为什么路线未必最短](union-find-components-and-minimum-spanning-trees.md)：区分集合代表与真实路径，解释合并、路径压缩和摊还成本，再以 [Kruskal](../../glossary/algorithms.md#algorithms.mst) 与割性质说明最小生成树的目标和边界。
- [加权最短路与松弛：先到达一个节点，为什么还不能确定最优](weighted-shortest-paths-and-relaxation.md)：用[松弛](../../glossary/algorithms.md#algorithms.shortest-path)、不变量和负权反例区分 BFS、DAG 路径、Dijkstra 与 Bellman-Ford，并说明负环、路径恢复和实现成本。

## 术语范围

| 术语 | 简释 |
| --- | --- |
| [Time / Space Complexity](../../glossary/algorithms.md#algorithms.complexity) | 时间、空间随输入规模增长的趋势。 |
| [Array / Linked List](../../glossary/algorithms.md#algorithms.sequences) | 连续槽位或链式节点的访问和修改，完整成本包含定位与维护。 |
| [Hash Table / Hash Function](../../glossary/algorithms.md#algorithms.hash-table) | 按哈希缩小候选并依键相等定位，涉及碰撞、负载及扩容前提。 |
| [Stack / Queue / Deque](../../glossary/algorithms.md#algorithms.queues) | 后进先出、先进先出与双端接口，需另外约定容量和共享操作语义。 |
| [Tree / Heap / Trie](../../glossary/algorithms.md#algorithms.trees) | 树形、搜索顺序、堆优先关系与 Trie 前缀分支各有不变量及更新责任。 |
| [B-Tree / B+Tree](../../glossary/algorithms.md#algorithms.b-tree) | 面向页访问的多路平衡树，区分分隔键、叶载荷、范围扫描和维护成本。 |
| [Sorting / Binary Search](../../glossary/algorithms.md#algorithms.sorting-search) | 排序契约与有序区间边界，区分存在性、重复范围及有序维护。 |
| [Graph / BFS / DFS](../../glossary/algorithms.md#algorithms.graph-traversal) | 图表示与遍历，区分可达性、无权距离、环和依赖顺序。 |
| [Bloom Filter](../../glossary/algorithms.md#algorithms.bloom) | 用共享位判断集合成员；阳性可能误报，阴性依赖完整插入、位状态与同步覆盖。 |
| [LRU / LFU](../../glossary/algorithms.md#algorithms.eviction) | 依据新近或频次分配有限缓存容量，区分精确/近似、接纳、过期和失效。 |
| [Amortized Analysis](../../glossary/algorithms.md#algorithms.amortized) | 把一系列操作的总成本分摊，不保证每次操作的最坏[延迟](../../glossary/performance.md#performance.latency-throughput)。 |
| [Probabilistic Data Structure](../../glossary/algorithms.md#algorithms.probabilistic) | 以 Bloom 为例用概率误报换取空间或工作量，其他概率结构仍待深入。 |
| [Weighted Shortest Path / Relaxation](../../glossary/algorithms.md#algorithms.shortest-path) | 在明确边权与图前提下计算最小可加路线成本，区分发现、确认、有限距离、不可达与负环影响。 |
| [Greedy Algorithm / Exchange Argument](../../glossary/algorithms.md#algorithms.greedy) | 按局部规则承诺选择，并用安全交换等论证连接到全局目标；可行、不能扩充与最优分别判断。 |
| [Dynamic Programming / Memoization](../../glossary/algorithms.md#algorithms.dynamic-programming) | 定义充分状态及无环依赖，复用子问题结果；初始化、更新方向、方案恢复与数值规模分别限定。 |
| [Union-Find / Disjoint Set Union](../../glossary/algorithms.md#algorithms.union-find) | 通过代表维护只合并的互斥分组，按秩/大小与压缩改善序列成本；内部父指针不是原图路线。 |
| [Minimum Spanning Tree / Kruskal](../../glossary/algorithms.md#algorithms.mst) | 在无向图中以最小边权总和连接各分量，结合无环与安全跨割边；目标不同于单源最短路径。 |
| [Divide and Conquer](../../glossary/algorithms.md#algorithms.divide-conquer) | 把问题分成更小同类问题，再依正确的组合规则构造原答案。 |
| [Backtracking](../../glossary/algorithms.md#algorithms.backtracking) | 逐步选择并探索部分方案，在返回时恢复选择，用有证明的条件排除无用分支。 |
| [Exact String Matching / KMP](../../glossary/algorithms.md#algorithms.string-matching) | 按明确符号与位置契约找精确子串，用前缀函数安全复用失配前信息。 |

## 练习与验收

选择上面的一个核心问题，先画执行过程或数据边界，再构造一个正常路径和一个失败路径。用原理解释、架构或代码、诊断证据和取舍依据说明保证范围；记录已完成验证与待验证项。

[回到知识地图](../../map.md) · [问题导航](../../problems.md) · [学习路径](../../paths/index.md)
