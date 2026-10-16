<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# 数据结构与算法

建议优先级：P0。目标：通过访问模式和复杂度选择数据结构。

下方术语用于知识索引。建议从[实际工程问题](../../problems.md)或本页核心问题进入，结合已有正文理解机制、适用边界与相关概念。

## 一个核心问题

为什么数据库索引常用 B+ 树，向量检索常讨论图索引？

## 已有正文

- [复杂度与数据结构：如何从访问方式选择存储组织](complexity-and-data-structures.md)：说明渐进复杂度、最坏/期望/摊还成本，并把查找、更新和额外内存放到同一选择中。

## 术语范围

| 术语 | 简释 |
| --- | --- |
| Time / Space Complexity | 时间、空间随输入规模增长的趋势。 |
| Array / Linked List | 连续或链式存储及访问和修改成本。 |
| Hash Table / Hash Function | 键映射、碰撞处理和负载因子。 |
| Stack / Queue / Deque | 后进先出、先进先出与双端操作。 |
| Tree / Heap / Trie | 层级关系、优先级和前缀索引。 |
| B-Tree / B+Tree | 面向页访问的多路平衡树及索引组织。 |
| Sorting / Binary Search | 排序与有序区间上的查找。 |
| Graph / BFS / DFS | 关系建模与图遍历。 |
| Bloom Filter | 允许误报的集合成员近似判断。 |
| LRU / LFU | 按访问新近程度或频率淘汰缓存。 |
| Amortized Analysis | 在一系列操作上分摊成本。 |
| Probabilistic Data Structure | 用可控误差换取空间或时间效率。 |

## 练习与验收

选择上面的一个核心问题，先画执行过程或数据边界，再构造一个正常路径和一个失败路径。用原理解释、架构或代码、诊断证据和取舍依据说明保证范围；记录已完成验证与待验证项。

[回到知识地图](../../map.md) · [问题导航](../../problems.md) · [学习路径](../../paths/index.md)
