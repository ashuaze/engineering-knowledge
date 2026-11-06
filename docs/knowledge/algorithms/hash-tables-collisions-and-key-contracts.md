---
id: "kb-algorithms-hash-tables"
title: "哈希表与键契约：查找为什么不是无条件常数时间"
kind: "concept"
domain: "algorithms"
status: "evolving"
summary: "解释哈希、相等判断、碰撞、负载因子和扩容，区分键身份、重复策略与预期复杂度。"
created: "2026-10-20"
updated: "2026-10-23"
last_verified: "2026-10-20"
verification: "source-checked"
prerequisites: ["kb-algorithms-complexity"]
related: ["kb-algorithms-linear-structures", "kb-algorithms-sorting-boundaries", "kb-algorithms-trees-heaps", "kb-cache-search-cache-aside", "kb-api-idempotency", "kb-algorithms-page-indexes", "kb-cache-search-bloom", "kb-cache-redis-data-types", "kb-algorithms-string-matching"]
tags: ["hash-table", "collision", "load-factor", "key-contract"]
---

# 哈希表与键契约：查找为什么不是无条件常数时间

学习入口：按 ID 查找已经改成映射，为什么仍可能变慢，甚至查不到刚放入的数据？前置：[复杂度的期望与摊还口径](complexity-and-data-structures.md)。本文用普通[哈希表](../../glossary/algorithms.md#algorithms.hash-table)模型解释机制，[容器](../../glossary/devops.md#devops.containers)契约分别参照 Java 21 HashMap 和 Python 3.13；没有执行哈希分布、[扩容](../../glossary/algorithms.md#algorithms.amortized)或攻击负载实验。

## 哈希负责缩小候选，相等规则负责认定键

哈希函数把键转成用于定位的信息，表再将其映射到桶或槽位。有限的位置可能容纳更多不同的键，因此不同键落到同一位置是正常现象，称为碰撞；不能把哈希值相同直接当作键相同。

查找还需按容器约定比较候选键。相等的键必须具有一致的哈希结果；不相等的键却可以碰撞。Python 的 [hashable 定义](https://docs.python.org/3.13/glossary.html#term-hashable)还要求哈希值在对象生命周期内保持不变。键参与相等与哈希的状态若被不当修改，可能破坏查找前提；不是把对象放进表里就自动冻结了它。

业务 ID 的规范化也应先约定。例如本例若规定 ID 是区分大小写的字符串，A7 与 a7 就是不同键；擅自转成小写会改变业务身份。表负责遵守给定键规则，不会替应用判断应该合并哪些账号或订单。

## 碰撞需要保留全部候选

教学模型使用 5 个桶、整数键 h(k)=k mod 5，并以链保存同桶条目；这不是生产哈希函数建议：

| 操作 | 桶 2 的纸面状态 |
| --- | --- |
| 放入 (12, A) | [(12, A)] |
| 放入 (17, B) | [(12, A), (17, B)] |
| 查找 17 | 比较候选键，返回 B |
| 再放入 (12, C)，约定同键替换值 | [(12, C), (17, B)]，总键数仍为 2 |

覆盖同键与错误覆盖同桶是两种行为。要保存一个键对应的多条记录，需要把值定义成集合或序列等，而不是期待普通映射自动保留每次写入。

链地址法把碰撞项放入链等结构；开放寻址则在表内按探测规则寻找位置，插入、查找与删除必须使用一致规则。删除和空槽的处理依实现，不能任意清掉探测路径中的槽位。模型与分析见 [MIT 6.006 Hashing](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/resources/mit6_006s20_lec4/)。

## 预期常数时间需要条件

设键数为 n，桶数为 b，负载因子 α=n/b。对典型链地址模型，在哈希分散及相关随机性假设下，候选链的预期长度与 α 有关；当 α 受控、哈希和相等比较有界时，基本操作才可分析为预期 O(1)。若全部键集中到一条线性链，查找最坏可达 O(n)。

这不是所有语言实现的统一最坏界：有些实现会改变桶的内部结构或使用其他缓解机制。Java 21 的 [HashMap](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/HashMap.html)也把基本操作的常数时间与哈希适当分散联系起来，并说明负载因子、重哈希和容量成本。

| 成本来源 | 容易漏掉什么 |
| --- | --- |
| 计算键的哈希 | 长字符串、复杂对象可能不是有界成本 |
| 比较碰撞项 | 碰撞越集中，相等比较越多 |
| 扩容与重新安排条目 | 单次操作可能处理大量已有项，带来[尾延迟](../../glossary/performance.md#performance.percentiles)和额外空间 |
| 遍历和保持顺序 | 迭代顺序、容量影响和是否按键[排序](../../glossary/algorithms.md#algorithms.sorting-search)取决于容器契约 |

合理几何扩容可分摊维护成本，仍需单独说明随机假设与整串操作成本。预期不是“每次都很快”，摊还也不是“最坏一次仍为常数”；两者不能互相替代。

算法中的哈希表与服务器提供的 Hash 逻辑类型并不处于同一抽象层，继续见[Redis 数据结构](../cache-search/redis-data-types-operations-and-atomicity.md)。选型要核对字段、排名或消费位置的操作需求，而非从名称推导内部编码、复杂度或多命令事务。

滚动窗口的哈希阳性与原符号核对，继续见[字符串匹配](string-matching-prefix-functions-and-text-boundaries.md)。哈希候选不能直接当作精确命中；核对成本、比较单位和返回位置都要纳入算法保证。

## 精确匹配不自动支持有序访问

有序页访问见 [B/B+ 树](b-trees-bplus-trees-and-page-indexes.md)，[近似成员判断](../../glossary/algorithms.md#algorithms.probabilistic)见 [Bloom Filter](../cache-search/bloom-filters-membership-and-synchronization.md)：位图阳性不等于哈希表的精确键命中，过滤器同步与表的相等契约各有前提。本次只补关联，没有新增算法实测。

哈希表适合按键定位，不会天然提供“比此时间更晚的前十项”或按键区间遍历。有插入顺序的容器也不等于按键排序；需要有序操作时，可比较[排序与二分](sorting-binary-search-and-boundaries.md)及[有序树](trees-heaps-and-priority-queues.md)。

把重复扫描换成映射之前，还要计入建表、更新及长期持有的对象；数据频繁变化时，本地表也可能陈旧，关联见[缓存与失效](../cache-search/cache-aside-and-invalidation.md)。每次请求都重新构建整张表，未必比一次扫描便宜。

哈希表也不提供[并发](../../glossary/systems.md#systems.concurrency)的“查重再写入”[原子性](../../glossary/systems.md#systems.atomicity)或持久化保证；多实例业务去重仍需[幂等与提交边界](../api/idempotency.md)。普通哈希值不是全球唯一业务身份，不能仅凭其相等就删除重复记录。

自检：键怎样判等？可变部分会不会改变哈希或相等？重复键是替换、拒绝还是累积？O(1) 的分散、键长度与容量前提是否成立？查询究竟是精确匹配还是有序范围？

2026-10-20 核查 MIT 6.006、Java 21 HashMap 与 Python 3.13 hashable 文档，状态为 source-checked。桶和负载模型为教学设计；未运行哈希表实现、可变键、碰撞、扩容、并发去重或基准实验。
