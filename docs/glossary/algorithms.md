<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# 数据结构与算法词汇表

本页解释 20 组术语，按[完整术语索引](../glossary.md#algorithms)中的顺序排列。示例为说明性场景；具体技术版本与验证范围见各条深入阅读。

[分类词汇表](index.md) · [数据结构与算法文章](../knowledge/algorithms/index.md)

## 本页术语

- [Time / Space Complexity](#algorithms.complexity)
- [Array / Linked List](#algorithms.sequences)
- [Hash Table / Hash Function](#algorithms.hash-table)
- [Stack / Queue / Deque](#algorithms.queues)
- [Tree / Heap / Trie](#algorithms.trees)
- [B-Tree / B+Tree](#algorithms.b-tree)
- [Sorting / Binary Search](#algorithms.sorting-search)
- [Graph / BFS / DFS](#algorithms.graph-traversal)
- [Bloom Filter](#algorithms.bloom)
- [LRU / LFU](#algorithms.eviction)
- [Amortized Analysis](#algorithms.amortized)
- [Probabilistic Data Structure](#algorithms.probabilistic)
- [Weighted Shortest Path / Relaxation](#algorithms.shortest-path)
- [Greedy Algorithm / Exchange Argument](#algorithms.greedy)
- [Dynamic Programming / Memoization](#algorithms.dynamic-programming)
- [Union-Find / Disjoint Set Union](#algorithms.union-find)
- [Minimum Spanning Tree / Kruskal](#algorithms.mst)
- [Divide and Conquer](#algorithms.divide-conquer)
- [Backtracking](#algorithms.backtracking)
- [Exact String Matching / KMP](#algorithms.string-matching)

<a id="algorithms.complexity"></a>

## Time / Space Complexity

**ID：** `algorithms.complexity` · **建议优先级：** P0

**别名 / 检索词：** Time、Space Complexity、时间复杂度、空间复杂度

**简释：** 时间、空间随输入规模增长的趋势。

复杂度描述资源消耗随输入规模的增长，需注明最坏、平均或摊还等口径。渐近阶忽略常数和硬件因素，适合比较扩展趋势。

**例子：** 线性扫描为 O(n)，但小数组上可能比维护复杂索引更便宜。

**深入阅读：** [复杂度与数据结构：如何从访问方式选择存储组织](../knowledge/algorithms/complexity-and-data-structures.md) · [分治与回溯：怎样拆开问题，又怎样安全地排除分支](../knowledge/algorithms/divide-and-conquer-backtracking-and-pruning.md) · [字符串匹配：失配怎样安全回退，位置又按什么计算](../knowledge/algorithms/string-matching-prefix-functions-and-text-boundaries.md)

<a id="algorithms.sequences"></a>

## Array / Linked List

**ID：** `algorithms.sequences` · **建议优先级：** P0

**别名 / 检索词：** Array、Linked List、数组、动态数组、链表、Dynamic Array

**简释：** 连续槽位或链式节点的访问和修改，完整成本包含定位与维护。

数组支持按位置直接访问，插入中间通常要移动元素；链表通过节点链接，已知位置后的修改便宜但定位和分配有成本。复杂度需包含寻找位置的过程。

**例子：** 在链表尾插前若每次都从头寻找尾节点，总体成本仍可能很高。

**深入阅读：** [线性结构与端点操作：数组、链表、栈和队列怎样选择](../knowledge/algorithms/sequences-stacks-queues-and-deques.md) · [复杂度与数据结构：如何从访问方式选择存储组织](../knowledge/algorithms/complexity-and-data-structures.md)

<a id="algorithms.hash-table"></a>

## Hash Table / Hash Function

**ID：** `algorithms.hash-table` · **建议优先级：** P0

**别名 / 检索词：** Hash Table、Hash Function、哈希表、哈希函数、碰撞、负载因子、Load Factor

**简释：** 按哈希缩小候选并依键相等定位，涉及碰撞、负载及扩容前提。

哈希函数把键映射到候选位置，哈希表再用键相等规则处理冲突。装载因子、扩容与哈希分布影响性能；哈希相等不代表键相等。

**例子：** 两个键落入同一桶时，还必须比较键内容来找到目标记录。

**深入阅读：** [哈希表与键契约：查找为什么不是无条件常数时间](../knowledge/algorithms/hash-tables-collisions-and-key-contracts.md) · [复杂度与数据结构：如何从访问方式选择存储组织](../knowledge/algorithms/complexity-and-data-structures.md)

<a id="algorithms.queues"></a>

## Stack / Queue / Deque

**ID：** `algorithms.queues` · **建议优先级：** P0

**别名 / 检索词：** Stack、Queue、Deque、栈、队列、双端队列、FIFO、LIFO、deque

**简释：** 后进先出、先进先出与双端接口，需另外约定容量和共享操作语义。

栈提供后进先出，队列提供先进先出，双端队列允许两端操作。这些是接口语义，底层可用数组或链表实现；容量与并发安全需另行约定。

**例子：** 撤销历史可用栈，按到达顺序处理任务可用队列。

**深入阅读：** [线性结构与端点操作：数组、链表、栈和队列怎样选择](../knowledge/algorithms/sequences-stacks-queues-and-deques.md)

<a id="algorithms.trees"></a>

## Tree / Heap / Trie

**ID：** `algorithms.trees` · **建议优先级：** P0

**别名 / 检索词：** Tree、Heap、Trie、二叉搜索树、BST、优先队列、Priority Queue、Top-K、二叉堆、前缀树、前缀检索、Radix Tree、Longest Prefix Match、树、堆、字典树

**简释：** 树形、搜索顺序、堆优先关系与 Trie 前缀分支各有不变量及更新责任。

树是层次结构；搜索树维护键序；堆维护父子优先关系；Trie 按键的符号前缀分支。堆适合取极值，不能据此推断任意元素都有全局排序。

**例子：** 优先队列可用堆选择下一任务，前缀补全可用 Trie 缩小候选。

**深入阅读：** [树、堆与优先队列：能取最小值，为什么不等于已经有序](../knowledge/algorithms/trees-heaps-and-priority-queues.md) · [Trie 与前缀检索：路径存在，为什么不等于键存在](../knowledge/algorithms/tries-prefix-search-and-key-encoding.md)

<a id="algorithms.b-tree"></a>

## B-Tree / B+Tree

**ID：** `algorithms.b-tree` · **建议优先级：** P0

**别名 / 检索词：** B-Tree、B+Tree、B 树、B+ 树、页索引、扇出、Fanout

**简释：** 面向页访问的多路平衡树，区分分隔键、叶载荷、范围扫描和维护成本。

B 树和 B+ 树以多路平衡结构降低页访问层数；B+ 树通常把记录或记录引用放在叶层并支持顺序访问。具体页布局和并发维护由存储引擎决定。

**例子：** 范围查询先定位起点叶页，再按叶层顺序读取后续记录。

**深入阅读：** [B 树、B+ 树与页索引：树高很低，查询为什么仍然慢](../knowledge/algorithms/b-trees-bplus-trees-and-page-indexes.md)

<a id="algorithms.sorting-search"></a>

## Sorting / Binary Search

**ID：** `algorithms.sorting-search` · **建议优先级：** P0

**别名 / 检索词：** Sorting、Binary Search、排序、二分查找、Lower Bound、Upper Bound、稳定排序

**简释：** 排序契约与有序区间边界，区分存在性、重复范围及有序维护。

排序需约定比较关系、稳定性和原地性；二分查找依赖已排序区间或单调判定。查某值、找首个不小于值及找重复范围的边界不同。

**例子：** 找插入位置可求 lower bound，而不是命中任意一个相等元素就停止。

**深入阅读：** [排序与二分查找：找到一个位置，为什么仍可能答错](../knowledge/algorithms/sorting-binary-search-and-boundaries.md) · [分治与回溯：怎样拆开问题，又怎样安全地排除分支](../knowledge/algorithms/divide-and-conquer-backtracking-and-pruning.md)

<a id="algorithms.graph-traversal"></a>

## Graph / BFS / DFS

**ID：** `algorithms.graph-traversal` · **建议优先级：** P0

**别名 / 检索词：** Graph、BFS、DFS、图、广度优先、深度优先、拓扑排序、Topological Sort、DAG

**简释：** 图表示与遍历，区分可达性、无权距离、环和依赖顺序。

BFS 按层扩展，适用于无权图最少边数；DFS 沿路径深入，常用于环检测和结构分析。拓扑排序要求有向无环，不能直接套用于含环依赖。

**例子：** 依赖图出现环时，应报告循环依赖，而非输出一个声称有效的构建顺序。

**深入阅读：** [图遍历与依赖顺序：找到可达节点，为什么还不能安排执行](../knowledge/algorithms/graphs-traversal-and-dependency-order.md) · [分治与回溯：怎样拆开问题，又怎样安全地排除分支](../knowledge/algorithms/divide-and-conquer-backtracking-and-pruning.md)

<a id="algorithms.bloom"></a>

## Bloom Filter

**ID：** `algorithms.bloom` · **建议优先级：** P0

**别名 / 检索词：** Bloom Filter、布隆过滤器、误报、假阳性、False Positive

**简释：** 用共享位判断集合成员；阳性可能误报，阴性依赖完整插入、位状态与同步覆盖。

Bloom Filter 用多个哈希设置共享位，允许误报。只有在插入完整、位状态未损坏且同步范围正确时，阴性才能排除集合成员；普通结构不能随意清位删除。

**例子：** 过滤器说可能存在时仍查主存储；说不存在前须确认新写入已同步。

**深入阅读：** [Bloom Filter 与成员判断：可能存在，为什么不能直接当作命中](../knowledge/cache-search/bloom-filters-membership-and-synchronization.md)

<a id="algorithms.eviction"></a>

## LRU / LFU

**ID：** `algorithms.eviction` · **建议优先级：** P0

**别名 / 检索词：** LRU、LFU、缓存淘汰、容量淘汰、LRU Cache、LFU Cache、最近最少使用

**简释：** 依据新近或频次分配有限缓存容量，区分精确/近似、接纳、过期和失效。

LRU 优先淘汰较久未访问项，LFU 优先淘汰低频项。实际系统可能采用近似计数或采样；容量淘汰、数据过期、接纳和主动失效是不同决策。

**例子：** 一次性全表扫描可能冲掉 LRU 中常用数据，需要结合负载评估策略。

**深入阅读：** [LRU、LFU 与缓存淘汰：最近用过，为什么仍可能被移走](../knowledge/cache-search/lru-lfu-and-capacity-eviction.md)

<a id="algorithms.amortized"></a>

## Amortized Analysis

**ID：** `algorithms.amortized` · **建议优先级：** P0

**别名 / 检索词：** Amortized Analysis、摊还分析、扩容

**简释：** 把一系列操作的总成本分摊，不保证每次操作的最坏延迟。

摊还分析把一段操作序列的总成本分配到每次操作，不要求输入服从随机分布。摊还常数时间不代表单次操作没有扩容或搬迁尖峰。

**例子：** 动态数组多次尾部追加的平均分摊成本低，但一次扩容仍需搬移很多元素。

**深入阅读：** [线性结构与端点操作：数组、链表、栈和队列怎样选择](../knowledge/algorithms/sequences-stacks-queues-and-deques.md) · [复杂度与数据结构：如何从访问方式选择存储组织](../knowledge/algorithms/complexity-and-data-structures.md) · [字符串匹配：失配怎样安全回退，位置又按什么计算](../knowledge/algorithms/string-matching-prefix-functions-and-text-boundaries.md)

<a id="algorithms.probabilistic"></a>

## Probabilistic Data Structure

**ID：** `algorithms.probabilistic` · **建议优先级：** P0

**别名 / 检索词：** Probabilistic Data Structure、概率数据结构、近似成员判断、Approximate Membership

**简释：** 以 Bloom 为例用概率误报换取空间或工作量，其他概率结构仍待深入。

概率数据结构以误差概率换取空间或计算节省，必须说明误差方向和参数前提。成员判断、基数估计和频率估计的保证不能互相套用。

**例子：** Bloom Filter 的阳性可能误报，不能直接据此拒绝用户创建唯一名称。

**深入阅读：** [Bloom Filter 与成员判断：可能存在，为什么不能直接当作命中](../knowledge/cache-search/bloom-filters-membership-and-synchronization.md)

<a id="algorithms.shortest-path"></a>

## Weighted Shortest Path / Relaxation

**ID：** `algorithms.shortest-path` · **建议优先级：** P1

**别名 / 检索词：** 加权最短路、松弛、Dijkstra、Bellman-Ford、负权环、Negative Cycle、decrease-key、加权最短路径

**简释：** 在明确边权与图前提下计算最小可加路线成本，区分发现、确认、有限距离、不可达与负环影响。

加权最短路寻找边权可加的最低成本路径，松弛用已知路径改善距离估计。Dijkstra 的确认规则依赖非负边权；负环影响下不一定存在有限最短值。

**例子：** 路网允许负权时，不能未经前提检查就沿用 Dijkstra 的提前确认。

**深入阅读：** [加权最短路与松弛：先到达一个节点，为什么还不能确定最优](../knowledge/algorithms/weighted-shortest-paths-and-relaxation.md)

<a id="algorithms.greedy"></a>

## Greedy Algorithm / Exchange Argument

**ID：** `algorithms.greedy` · **建议优先级：** P1

**别名 / 检索词：** 贪心算法、贪心选择、交换论证、区间调度、Interval Scheduling、Greedy Choice

**简释：** 按局部规则承诺选择，并用安全交换等论证连接到全局目标；可行、不能扩充与最优分别判断。

贪心按局部规则做出选择，正确性需要交换论证等连接到全局最优的证明。局部可行或无法继续扩充，不等于已经最优。

**例子：** 按最早结束选择无权区间可用交换论证支持，改成带权目标后需重新分析。

**深入阅读：** [贪心选择与交换论证：每一步最好，为什么未必整体最优](../knowledge/algorithms/greedy-choices-and-exchange-arguments.md) · [分治与回溯：怎样拆开问题，又怎样安全地排除分支](../knowledge/algorithms/divide-and-conquer-backtracking-and-pruning.md)

<a id="algorithms.dynamic-programming"></a>

## Dynamic Programming / Memoization

**ID：** `algorithms.dynamic-programming` · **建议优先级：** P1

**别名 / 检索词：** 动态规划、记忆化、状态转移、0/1 背包、Knapsack、滚动数组、伪多项式、Pseudopolynomial

**简释：** 定义充分状态及无环依赖，复用子问题结果；初始化、更新方向、方案恢复与数值规模分别限定。

动态规划把问题分解为可复用子问题，状态必须包含后续决策所需信息。转移、初值与依赖顺序共同决定结果，压缩存储也不能改变使用的阶段。

**例子：** 0/1 背包压缩到一维时，更新方向要避免同一物品被重复使用。

**深入阅读：** [动态规划与状态设计：记住子问题，为什么还会算错](../knowledge/algorithms/dynamic-programming-states-and-dependency-order.md) · [分治与回溯：怎样拆开问题，又怎样安全地排除分支](../knowledge/algorithms/divide-and-conquer-backtracking-and-pruning.md)

<a id="algorithms.union-find"></a>

## Union-Find / Disjoint Set Union

**ID：** `algorithms.union-find` · **建议优先级：** P1

**别名 / 检索词：** 并查集、不相交集合、DSU、路径压缩、Path Compression、Union by Rank

**简释：** 通过代表维护只合并的互斥分组，按秩/大小与压缩改善序列成本；内部父指针不是原图路线。

并查集维护不相交分组，通过查代表和合并更新连通关系。路径压缩与按秩或大小合并改善序列成本；普通结构不直接支持删边或恢复原图路径。

**例子：** 两顶点代表相同可判断已连通，父指针不一定是原图中的边。

**深入阅读：** [并查集与最小生成树：连通成本最低，为什么路线未必最短](../knowledge/algorithms/union-find-components-and-minimum-spanning-trees.md)

<a id="algorithms.mst"></a>

## Minimum Spanning Tree / Kruskal

**ID：** `algorithms.mst` · **建议优先级：** P1

**别名 / 检索词：** 最小生成树、最小生成森林、MST、Kruskal、割性质、Cut Property

**简释：** 在无向图中以最小边权总和连接各分量，结合无环与安全跨割边；目标不同于单源最短路径。

最小生成树在无向连通图上以最低总边权连接全部顶点，不连通时对应最小生成森林。Kruskal 按边权考虑安全边，并用并查集避免成环。

**例子：** 总权重最小的连通树不必提供某个源点到所有顶点的最短路径。

**深入阅读：** [并查集与最小生成树：连通成本最低，为什么路线未必最短](../knowledge/algorithms/union-find-components-and-minimum-spanning-trees.md)

<a id="algorithms.divide-conquer"></a>

## Divide and Conquer

**ID：** `algorithms.divide-conquer` · **建议优先级：** P1

**别名 / 检索词：** Divide and Conquer、Divide-and-Conquer、分治、分治法

**简释：** 把问题分成更小同类问题，再依正确的组合规则构造原答案。

分治要说明基本情况、规模严格缩小、子问题接口与合并正确性；跨块约束不能因切分输入就消失。成本应把各分支与本地工作相加，递归深度不等于总工作量，划分失衡时也不能沿用平衡递推。

**例子：** n=8、内部按子问题长度计费、单元素叶计1时，四层各8共32单位；这不是实际比较次数或运行时间。

**深入阅读：** [分治与回溯：怎样拆开问题，又怎样安全地排除分支](../knowledge/algorithms/divide-and-conquer-backtracking-and-pruning.md)

<a id="algorithms.backtracking"></a>

## Backtracking

**ID：** `algorithms.backtracking` · **建议优先级：** P1

**别名 / 检索词：** Backtracking、回溯搜索、回溯法

**简释：** 逐步选择并探索部分方案，在返回时恢复选择，用有证明的条件排除无用分支。

回溯可求存在性、一个解、全部解或最优解；候选覆盖、状态恢复与输出语义需分别验证。可行性剪枝和最优界有不同证明，剪枝前提、并列最优与负数/零不能忽略；它不是DFS、动态规划或从结果恢复方案的同义词。

**例子：** 允许负数时，取5后仍可再取−2得到目标3；因当前和超过目标就停止会漏解。枚举[3,0]目标3时，也不能在取3后省略后续零的选择。

**深入阅读：** [分治与回溯：怎样拆开问题，又怎样安全地排除分支](../knowledge/algorithms/divide-and-conquer-backtracking-and-pruning.md)

<a id="algorithms.string-matching"></a>

## Exact String Matching / KMP

**ID：** `algorithms.string-matching` · **建议优先级：** P1

**别名 / 检索词：** Exact String Matching、精确字符串匹配、KMP、Knuth-Morris-Pratt

**简释：** 按明确符号与位置契约找精确子串，用前缀函数安全复用失配前信息。

KMP是精确子串匹配的一种算法；本篇的前缀函数形式在有界符号访问/比较与位置输出模型下按O(n+m+k)分析，并保留重叠及跨块状态。完整DFA表示另有字母表成本，哈希、Trie和正则不是它的同义词。编码、规范化与大小写折叠仍决定相等和偏移映射。

**例子：** ababaca的pi为0,0,1,2,3,0,1；在abababacaba里失配后保留aba，报告起点2。A😀B中的B在UTF-8字节、码点、UTF-16码元中分别位于5、2、3。

**深入阅读：** [字符串匹配：失配怎样安全回退，位置又按什么计算](../knowledge/algorithms/string-matching-prefix-functions-and-text-boundaries.md)

## 资料与延伸

下列资料提供相关机制的进一步说明，并不表示覆盖本页所有术语。各条已关联的专题文章另列具体来源、适用版本与验证边界。

- [Open Data Structures：数据结构与分析](https://opendatastructures.org/)
- [MIT 6.006 Spring 2020 Lecture 3: Sorting](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/6d1ae5278d02bbecb5c4428928b24194_MIT6_006S20_lec3.pdf)
- [Jeff Erickson Algorithms: Recursion](https://jeffe.cs.illinois.edu/teaching/algorithms/book/01-recursion.pdf)
- [Jeff Erickson Algorithms: Backtracking](https://jeffe.cs.illinois.edu/teaching/algorithms/book/02-backtracking.pdf)
- [Stanford CS106B Spring 2020: Backtracking 1](https://web.stanford.edu/class/archive/cs/cs106b/cs106b.1206/lectures/backtracking1/)
- [Stanford EE364b: Branch and Bound Methods](https://web.stanford.edu/class/ee364b/lectures/bb_slides.pdf)
- [Misra: Knuth-Morris-Pratt Algorithm (2017-06-05)](https://www.cs.utexas.edu/~misra/Notes.dir/KMP.pdf)
- [algs4 authors: KMP.java (master snapshot)](https://raw.githubusercontent.com/kevin-wayne/algs4/master/src/main/java/edu/princeton/cs/algs4/KMP.java)
- [algs4 authors: RabinKarp.java (master snapshot)](https://raw.githubusercontent.com/kevin-wayne/algs4/master/src/main/java/edu/princeton/cs/algs4/RabinKarp.java)
- [Unicode 17.0.0 Core Specification, Chapter 3](https://www.unicode.org/versions/Unicode17.0.0/core-spec/chapter-3/)
- [Unicode 17.0.0 UAX #15 rev57](https://www.unicode.org/reports/tr15/tr15-57.html)
- [Unicode 17.0.0 UAX #29 rev47](https://www.unicode.org/reports/tr29/tr29-47.html)
- [Unicode 17.0.0 CaseFolding data](https://www.unicode.org/Public/17.0.0/ucd/CaseFolding.txt)

[返回分类词汇表](index.md) · [完整术语索引](../glossary.md)
