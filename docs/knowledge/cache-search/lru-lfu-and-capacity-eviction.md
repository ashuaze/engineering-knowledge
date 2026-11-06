---
id: "kb-cache-search-eviction"
title: "LRU、LFU 与缓存淘汰：最近用过，为什么仍可能被移走"
kind: "concept"
domain: "cache-search"
status: "evolving"
summary: "比较精确 LRU/LFU 的访问状态、维护成本和适应性，区分容量、接纳、过期、失效与 Redis 近似策略。"
created: "2026-10-20"
updated: "2026-10-23"
last_verified: "2026-10-20"
verification: "source-checked"
prerequisites: ["kb-algorithms-linear-structures", "kb-algorithms-hash-tables", "kb-cache-search-cache-aside"]
related: ["kb-cache-search-bloom", "kb-algorithms-trie", "kb-algorithms-trees-heaps", "kb-performance-backpressure", "kb-frontend-routing-cache", "kb-cache-redis-data-types"]
tags: ["lru", "lfu", "cache-eviction", "capacity"]
---

# LRU、LFU 与缓存淘汰：最近用过，为什么仍可能被移走

学习入口：缓存已经设容量上限，为什么[热点](../../glossary/performance.md#performance.contention)仍会被淘汰，命中率高又为何不能证明数据够新？前置：[链表与端点](../algorithms/sequences-stacks-queues-and-deques.md)、[哈希表](../algorithms/hash-tables-collisions-and-key-contracts.md)和 [Cache-Aside](cache-aside-and-invalidation.md)。本文先定义精确策略的教学模型，再对照 Python 3.13 与 Redis 官方机制；没有运行缓存或负载实验。

## 淘汰、接纳与有效性分开决定

| 决定 | 回答什么 | 不能代替什么 |
| --- | --- | --- |
| 接纳 | 新对象是否值得进入缓存 | 已有对象的更新与权限判断 |
| [容量淘汰](../../glossary/algorithms.md#algorithms.eviction) | 放不下时优先移除谁 | [TTL](../../glossary/cache-search.md#cache-search.invalidation)、主动失效与权威数据同步 |
| 过期 | 对象是否超过约定时间边界 | 数据源修改后立即可见 |
| 主动失效 | 哪些对象或版本不再可用 | 空间足够时的保留优先级 |

LRU/LFU 根据过去访问预测未来价值，不检查业务内容是否最新。一个频繁命中的旧值可能一直受到保留；一致性继续由[缓存失效协议](cache-aside-and-invalidation.md)解释。

## 最近访问和累计频率会选不同对象

本例容量为 2 个等重条目，不考虑 TTL、失效或[并发](../../glossary/systems.md#systems.concurrency)。首次 put 算一次使用，命中 get 算一次；每次使用也更新新近顺序。新键一定接纳，满时先从已有键中选受害者再插入。LFU 使用自条目插入后的累计次数、无衰减；同次数时按 LRU 打破并列。本例没有已有键的 put 覆盖或淘汰后重新接纳，扩展时需另定是否计次、更新新近顺序及重置频次。

纸面操作依次为 put A、get A、get A、put B、get B，最后 put C：

| 插入 C 前的观察 | A | B |
| --- | --- | --- |
| 累计使用次数 | 3 | 2 |
| 最近使用先后 | 较早 | 较晚 |

精确 LRU 移除 A，保留 B、C；精确 LFU 移除 B，保留 A、C。两者都遵守自身规则，不能以“刚访问了 B”证明 LFU 不该淘汰它。算例是自设策略，不对应 Redis 的逐步实际结果。

LRU 易受到一次性大扫描影响：新扫描项可能不断挤走原热点；不衰减的累计 LFU 又可能长期保留过去很热、如今已冷的对象。是否加入接纳门槛、近期窗口或衰减，需要按负载选择，不能断言 LFU 或 LRU 总有更高命中率。

## 精确状态需要维护，也可能使读变成写

典型精确 LRU 可用[哈希表](../../glossary/algorithms.md#algorithms.hash-table)定位节点，再用双向[链表](../../glossary/algorithms.md#algorithms.sequences)维护从旧到新的次序。命中后摘下并移到新端；插入满容量时移除旧端，并同步删除映射。已有合法节点时链表重连为 O(1)，加上哈希操作假设可得到预期常数成本；分配、扩容、锁和资源释放仍需另计。

Python 3.13 的 [OrderedDict](https://docs.python.org/3.13/library/collections.html#collections.OrderedDict)提供 move_to_end 和定端 popitem，可支持相应设计；普通字典保留插入次序，不表示读取会自动更新 LRU 次序。本文不提供可部署缓存类。

精确 LFU 不一定每次全表排序。可用按频次组织的链式桶、桶内条目与按键索引：命中时从频次 f 搬到相邻的 f+1 桶，维护最小非空桶；桶内还需落实本例的并列规则。相关结构见 [Shah、Mitra、Matani 的 LFU 论文](https://arxiv.org/abs/2110.11602)。常数成本依赖相应索引、指针及有界计数操作模型，不表示所有 LFU 实现或全局衰减都是 O(1)。

缓存读取若维护次序或频次，就会改变内部元数据。并发时必须让索引、链表、计数和容量保持一致；“只是读缓存”不能成为忽略共享修改的理由。

## 产品的近似策略要单独理解

Redis 的 [Key eviction](https://redis.io/docs/latest/develop/reference/eviction/)说明，其 LRU 通过抽样等机制近似选择旧项，LFU 使用概率计数与衰减，并对候选进行抽样；不是本篇精确序列的原样实现。抽样和衰减参数影响开销与适应性，但不保证某次一定移除全局最旧或累计次数最少的键。

候选范围也由策略决定，例如 allkeys 与 volatile 的候选不同；后者只考虑带过期设置的键，不等于仅淘汰“已经过期”的键。容量上限及产品内存口径也不应直接当作整个[进程](../../glossary/systems.md#systems.execution-units) RSS 的严格上界。本文不修改 Redis 配置，也不提供通用参数推荐。

一个键内部仍可能包含许多字段或成员，实际操作与返回成本见[Redis 数据结构](redis-data-types-operations-and-atomicity.md)。数据类型、过期粒度和淘汰策略需要一起判断，不能用单个键的存在推定容量或恢复保证。

## 条目数、字节和回源负载需要一起算

本例的两个条目等重，真实对象却可能大小悬殊。按条目数限制不自动约束字节量；按权重限制则要定义元数据是否计入、更新后重新计量，以及一次大对象是否需要淘汰多个条目。对象本身超过总预算时还需明确拒绝缓存等策略，不能不停淘汰却仍放不下。

淘汰后通常会增加回源工作；大量失效或热点替换可能令依赖承压。应同时观察请求命中率、字节命中率、加载成本、淘汰/过期数量与等待，结合[背压与有界队列](../performance/backpressure-and-bounded-queues.md)控制回源，而不是只追求一个命中率数值。

缓存内部线程安全也不保证同键只加载一次。Python [lru_cache](https://docs.python.org/3.13/library/functools.html#functools.lru_cache)明确允许首次结果尚未缓存时发生重复调用；若需要合并加载，还要管理在途结果、失败、[超时](../../glossary/api.md#api.retries)和失效后的旧回填。淘汰也不能撤销已发起工作或替代当前[授权](../../glossary/security.md#security.identity)检查。

自检：容量按条目还是字节？命中是否更新策略状态？LFU 统计从何时开始，是否衰减？并列如何决定？移除的是冷对象、过期对象还是失效版本？回源和旧请求由谁管理？

2026-10-20 核查 Python 3.13、LFU 原作者论文和 Redis 官方淘汰文档，状态为 source-checked。访问序列、桶和容量为教学设计；未运行 LRU/LFU、衰减抽样、并发加载、字节额度、热点扫描或缓存性能实验。
