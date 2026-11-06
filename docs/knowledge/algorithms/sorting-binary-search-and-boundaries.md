---
id: "kb-algorithms-sorting-boundaries"
title: "排序与二分查找：找到一个位置，为什么仍可能答错"
kind: "concept"
domain: "algorithms"
status: "evolving"
summary: "区分排序契约、稳定性与确定顺序，用半开区间和循环不变量解释二分边界、重复值及维护成本。"
created: "2026-10-20"
updated: "2026-10-23"
last_verified: "2026-10-20"
verification: "source-checked"
prerequisites: ["kb-algorithms-complexity", "kb-algorithms-linear-structures"]
related: ["kb-algorithms-hash-tables", "kb-algorithms-trees-heaps", "kb-api-contracts-pagination", "kb-database-indexes-plans", "kb-engineering-property-state-models", "kb-algorithms-greedy", "kb-algorithms-union-find-mst", "kb-algorithms-divide-backtrack"]
tags: ["sorting", "binary-search", "invariant", "boundary"]
---

# 排序与二分查找：找到一个位置，为什么仍可能答错

学习入口：明明用了二分，为什么遇到重复值、空序列或边界就出错？前置：[复杂度](complexity-and-data-structures.md)与[数组访问](sequences-stacks-queues-and-deques.md)。本文以有序随机访问序列为模型，Python 片段参照 3.13 文档，均未执行；比较和索引的实际成本另计。

## 排序先要定义保持什么

[排序](../../glossary/algorithms.md#algorithms.sorting-search)输出应保留输入的元素及重复次数，并满足约定顺序。去重、过滤、分组是额外操作，不是排序自然附带的行为。比较规则还需一致；若比较结果随时间变化或含无法按约定处理的值，就不能套用普通有序序列的保证。

稳定排序保留“按排序键相同”的记录在输入中的相对次序。它不自动给不同来源的输入建立唯一顺序：两次输入中同键记录原本的顺序不同，稳定结果仍可不同。跨页或跨批次要可确定的次序，还需定义足够的次级键与[并发](../../glossary/systems.md#systems.concurrency)数据范围，见[接口排序与分页](../api/contracts-and-pagination.md)。

Python 的 sort/sorted 支持 key 并保证稳定；sort 修改原列表，sorted 产生新列表，见 [Sorting HOWTO](https://docs.python.org/3.13/howto/sorting.html)。“修改原列表”不等于算法辅助空间必为 O(1)，返回新列表也不等于深度复制每个对象。

## 排序成本与后续收益一起计算

排序可服务于[区间贪心](greedy-choices-and-exchange-arguments.md)及[Kruskal 最小生成树](union-find-components-and-minimum-spanning-trees.md)，但排好序并不自动证明后续选择最优；还需目标、可行性与安全选择论证。两篇为来源核查和纸面推演，没有新增本文排序或基准结果。

选择算法要看数据规模、已有顺序、额外空间、比较成本和稳定性。作为分析对照，典型插入排序最坏 O(n²)；典型[数组](../../glossary/algorithms.md#algorithms.sequences)归并排序通过排序两半再线性合并，得到 O(n log n) 时间并使用额外合并空间。具体实现与证明参照 [MIT 6.006 Sorting](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/resources/mit6_006s20_lec3/)，不是本项目的性能测量。

先花 O(n log n) 排序，再做 q 次 O(log n) 查找，与 q 次线性扫描的 O(qn) 相比，还要判断结果能否复用、更新多不多、排序是否改变外部语义。只有一次查询时，排序不一定划算。

## 二分依赖有序性与持续缩小的区间

下面教学函数针对不降序整数列表，列表在调用期间不改变；返回第一个大于或等于 x 的位置，允许返回 len(a)。函数不自行检查排序前提，也不做输入类型验证：

```python
def lower_bound(a, x):
    lo, hi = 0, len(a)
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if a[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    return lo
```

循环保持：索引小于 lo 的元素都小于 x；索引大于或等于 hi 的元素都大于或等于 x；尚未分类的元素索引位于半开区间 [lo, hi)，边界答案则允许落在 hi。每轮严格缩小区间，lo=hi 时得到分界。这里是整数的通常一致比较，不扩展到 NaN 或任意自定义比较器。

纸面推演 a=[2,4,4,9]、x=4：初始 (0,4)，mid=2 后成为 (0,2)，mid=1 后为 (0,1)，mid=0 后为 (1,1)，返回 1。空列表返回 0；x=10 返回 4。边界位置是合法答案，不一定是可读取下标。

如果把 lo=mid+1 改为 lo=mid，当区间只剩一个待判定元素时就可能不再缩小；若固定返回某个相等位置，也未必得到重复值的最左边界。这些是纸面反例，没有执行输出。

## 插入位置、存在性与重复范围不同

Python [bisect](https://docs.python.org/3.13/library/bisect.html)用于找插入点，不直接返回“找到/没找到”。对上述整数模型，i=lower_bound(a,x) 后，还需检查 i<len(a) 且 a[i]==x，才能断言存在；不能直接读取 a[len(a)]。

若还求出第一个严格大于 x 的上边界 j，则所有等于 x 的元素位于 [i,j)，数量为 j−i。对 a=[2,4,4,9] 和 x=4，下界 1、上界 3，数量 2；若 x 不存在，这段范围为空。

使用 bisect 的 key 参数时，key 应用于序列元素而不应用于查找值 x；查询必须位于对应的键空间。这与 sort 的“给每项提取 key”相近但不能机械互换，依据见其 API 文档。

分解、合并正确性与平衡/失衡递推，继续见[分治与回溯](divide-and-conquer-backtracking-and-pruning.md)。二分只走一个半区间，归并需要两边结果，不能仅凭都有对数深度推导同样总成本。

## 维护有序也有成本

二分只减少定位比较次数。在普通连续列表中插入仍可能移动 O(n) 项；若每次定位都重新排序、切片复制或在线性结构上定位中点，总操作也不再只有 O(log n)。比较长键时，比较成本本身还需计入。

并发修改可能使循环前提失效，Python bisect 也不为共享序列的并发使用提供[线程](../../glossary/systems.md#systems.execution-units)安全保证；需要稳定快照或适合的同步，而不是认为每步都是读取就安全。有序更新频繁时，可继续比较[平衡树](trees-heaps-and-priority-queues.md)；[数据库索引](../../glossary/database.md#database.indexes)的页访问又需另行分析，见[索引与计划](../database/indexes-and-query-plans.md)。

自检：要存在性、某个相等项、最左位置还是区间？排序键和查找键是否一致？循环怎样确保收缩？输出是否保留重复项？可用[属性与边界检查](../engineering/property-testing-and-state-models.md)验证有序、元素多重集合不变及分界条件，但本批尚未执行。

2026-10-20 核查 MIT 6.006、Python 3.13 排序与 bisect 文档，状态为 source-checked。lower_bound、区间及成本为教学推演；未执行排序/二分用例、属性生成、并发修改或基准实验。
