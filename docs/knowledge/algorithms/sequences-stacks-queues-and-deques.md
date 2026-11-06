---
id: "kb-algorithms-linear-structures"
title: "线性结构与端点操作：数组、链表、栈和队列怎样选择"
kind: "concept"
domain: "algorithms"
status: "evolving"
summary: "从访问位置、修改位置和顺序规则比较动态数组、链表、栈、队列与双端队列，解释定位成本和容量语义。"
created: "2026-10-20"
updated: "2026-10-20"
last_verified: "2026-10-20"
verification: "source-checked"
prerequisites: ["kb-algorithms-complexity"]
related: ["kb-algorithms-hash-tables", "kb-algorithms-sorting-boundaries", "kb-algorithms-graphs", "kb-performance-backpressure", "kb-systems-virtual-memory"]
tags: ["array", "linked-list", "stack", "queue", "deque"]
---

# 线性结构与端点操作：数组、链表、栈和队列怎样选择

学习入口：都是保存一串任务，为什么换个取出位置，成本就完全不同？前置：[复杂度与完整操作](complexity-and-data-structures.md)。本文采用元素访问、移动和指针修改为有界成本的模型；Python API 限定 3.13 文档，算例未执行，也不把某个[容器](../../glossary/devops.md#devops.containers)实现推广到所有语言。

## 先分清接口与表示

栈要求后进先出 [LIFO](../../glossary/algorithms.md#algorithms.queues)，队列要求先进先出 FIFO，双端队列允许从两端添加或移除。它们描述允许的操作及顺序，可以由不同存储结构实现；名字里有 Queue 不表示必定是[链表](../../glossary/algorithms.md#algorithms.sequences)，名字叫 list 也不表示必定是链式节点。

数组将元素或元素引用组织在连续槽位中，便于按下标访问；链表由节点和链接组织顺序，找到节点后可以改动相邻链接。节点的物理地址不必连续，但额外链接和分配也有成本。接口与实现的区别参照 [MIT 6.006 Lecture 2](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/resources/mit6_006s20_lec2/)。

## 把定位与修改一起计入

下表比较典型模型，不包含元素本身昂贵的复制、析构和[并发](../../glossary/systems.md#systems.concurrency)同步：

| 操作 | 动态数组 | 维护头尾引用的单向链表 |
| --- | --- | --- |
| 按下标读取 | O(1) | 最坏 O(n) 沿链定位 |
| 按值查找 | 未[排序](../../glossary/algorithms.md#algorithms.sorting-search)时最坏 O(n) | 最坏 O(n) |
| 尾部追加 | 采用几何[扩容](../../glossary/algorithms.md#algorithms.amortized)时摊还 O(1)，单次可为 O(n) | 已有尾引用时 O(1) |
| 移除头部 | 典型连续表示需移动 O(n) 个槽位 | O(1)，同时维护空表时的尾引用 |
| 移除尾部 | 典型模型摊还 O(1)，缩容策略另计 | 最坏 O(n)，需找到前驱 |
| 在指定位置插入 | 定位后仍可能移动 O(n) 个槽位 | 已持有合法前驱节点时重连 O(1)，先查位置仍可为 O(n) |

双向链表再维护前驱链接，可以支持已知合法节点处的 O(1) 移除，但会增加空间和维护责任。不能删掉“已找到相应节点”这个前提，就宣称任意链表删除都是 O(1)。

动态数组预留容量，减少每次追加都搬移的需要。教学策略是容量满时翻倍，容量 4 时第五次追加可能先复制原 4 项；一串追加可有常数摊还成本，仍不保证第五次也和前几次一样便宜。实际扩容倍率与缩容阈值依实现，不从这个算例推导 Python 的精确策略。

## 端点决定任务顺序

纸面任务序列依次加入 A、B、C。若使用右端加入、右端移除的栈，取出顺序为 C、B、A；右端加入、左端移除的队列为 A、B、C。这个差异会影响撤销、遍历、工作分派等算法的含义，不能只因两种实现都“取出了全部任务”就认为等价。

Python 3.13 的 list 可以用 append/pop 实现栈；以 pop(0) 反复取队首则会移动剩余槽位。最坏从 n 项逐个移除头部，总移动次数为 (n−1)+(n−2)+…+0，量级 O(n²)，不是 n 次操作就必然 O(n)。官方说明见 [Data Structures](https://docs.python.org/3.13/tutorial/datastructures.html#using-lists-as-queues)。

collections.deque 为两端操作提供近似 O(1) 成本，而中间下标访问会退化为 O(n)，见 [deque 文档](https://docs.python.org/3.13/library/collections.html#collections.deque)。为端点优化，不表示它同时替代了数组的随机访问能力。

## 容量与所有权也是契约

教学片段仅用于推演 Python 3.13 的有界 deque，未执行：

```python
from collections import deque

recent = deque(['A', 'B'], maxlen=2)
recent.append('C')
# 推演：从左到右剩余 B、C，A 被丢弃。
```

这里的满队列追加会丢弃另一端元素；不等于[阻塞](../../glossary/systems.md#systems.blocking)生产者，也不等于可靠任务队列的拒绝通知。deque 的有界 insert 又有不同的超限错误规则，不能把“有界就丢弃”推广到所有方法。任务不可丢失时，应单独设计[背压、拒绝与接纳责任](../performance/backpressure-and-bounded-queues.md)。

容器通常保存引用，不自动复制深层对象；元素被其他持有者修改后，容器里观察到的内容也可能改变。单次端点操作的[线程](../../glossary/systems.md#systems.execution-units)安全说明，也不能推出“检查非空再取出”等多步流程整体原子；共享使用仍需相应同步。

## 根据工作负载选择

大量按下标读取、批量扫描且更新集中在尾部，可先考虑动态数组。频繁改动已经持有的节点链接时，可考虑链式表示；大量端点进出可选择合适的 deque 或队列实现。还要核算缓存[局部性](../../glossary/systems.md#systems.cpu-cache)、分配、额外引用、容量和迭代期间修改的规则，不能只比较一个 O 符号。

“连续槽位”也不是“所有业务对象都物理连续”；虚拟地址和物理页关系见[虚拟内存](../systems/virtual-memory-pages-and-faults.md)。本文没有做局部性或分配成本实测。

自检：接口要 FIFO、LIFO 还是任意位置访问？定位算入了吗？单次扩容能否接受？满队列应该等待、拒绝还是丢弃，由谁承担后果？

2026-10-20 核查 MIT 6.006、Python 3.13 容器与 deque 文档，状态为 source-checked。搬移次数、任务顺序、容量策略和片段为纸面推演；未运行容器正确性、并发、扩缩容或性能实验。
