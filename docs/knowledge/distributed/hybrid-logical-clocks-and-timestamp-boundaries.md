---
id: "kb-distributed-hlc"
title: "混合逻辑时钟：时间戳怎样尊重因果，又保留物理时间参照"
kind: "concept"
domain: "distributed"
status: "evolving"
summary: "用可复算的 HLC 更新说明物理分量、逻辑计数与因果单向保证，区分时间戳、经过时间、提交及安全读取边界。"
created: "2026-10-23"
updated: "2026-10-23"
last_verified: "2026-10-23"
verification: "source-checked"
prerequisites: ["kb-distributed-logical-clocks", "kb-distributed-consistency"]
related: ["kb-distributed-consensus-quorum", "kb-distributed-leases-fencing", "kb-distributed-identifiers", "kb-cache-search-index-cutover", "kb-database-isolation-mvcc"]
tags: ["hlc", "logical-clock", "causality", "clock-skew", "timestamps"]
---

# 混合逻辑时钟：时间戳怎样尊重因果，又保留物理时间参照

学习入口：A 发送消息后，B 的墙钟读数比 A 小，怎样给接收事件分配更大的时间戳？只用逻辑计数又会丢掉日期时间参照。[混合逻辑时钟](../../glossary/distributed.md#distributed.hlc)（Hybrid Logical Clock，HLC）把已知物理时间与逻辑递增分开，让消息链上的时间戳递增；它仍不能单凭两个数判断并发、确认提交或测量持续时间。

前置：[逻辑时钟与因果](logical-clocks-causality-and-concurrency.md)、[一致性与复制](consistency-and-replication.md)。本文采用顺序处理时钟事件的节点、显式携带时间戳的消息和非恶意参与者模型。数字、伪代码及故障反例均为纸面推演，未执行时钟实现、数据库或集群实验。

## 把两个增长原因分开

设一个节点的 HLC 为 `(l,c)`。`l` 保存该节点从本地物理钟及已收到消息获知的最大物理分量，`c` 在物理分量不能前进时区分新的逻辑事件。比较使用字典序：先比 l，相同再比 c，不把 c 当作另一段毫秒。

这不是把任意墙钟读数和任意计数拼起来。下面使用 [Kulkarni 等 2014 年技术报告 §3.3、图 5](https://cse.buffalo.edu/tech-reports/2014-04.pdf)中的双分量更新机制，改写变量以便复算。每次更新须作为本节点完整、串行化的时钟操作；同[进程](../../glossary/systems.md#systems.execution-units)多个线程竞争更新时，也要保持这个约束。

物理读数 `p` 在本次事件采样一次。初始化 `(l,c)=(0,0)`；本篇例子的物理读数均为正。发送消息使用这次发送事件生成的时间戳，接收消息携带 `(lm,cm)`：

```text
本地或发送事件：
    old_l = l
    l = max(old_l, p)
    c = c + 1  若 l == old_l；否则为 0
    返回 (l,c)

接收事件：
    old_l = l
    l = max(old_l, lm, p)
    若 l == old_l == lm：c = max(c,cm) + 1
    否则若 l == old_l：c = c + 1
    否则若 l == lm：c = cm + 1
    否则：c = 0
    返回 (l,c)
```

接收时不能只取较大物理分量后统一清零。例如本地 `(100,4)` 收到 `(100,7)`，即使墙钟为 99，也必须得到 `(100,8)`。取 `(100,0)` 会让接收事件排到发送事件之前。反过来，若物理钟已到 101，则 `(101,0)` 已严格大于两者，可以清零计数。

## 一条消息链怎样跨过墙钟回拨

以下单位为教学毫秒刻度，A、B、C 均从 `(0,0)` 开始。只有 a1→b2 和 b3→a2 两条跨节点消息边；表格行序不会增加其他跨节点因果边。

| 事件 | 动作与当前物理读数 p | 更新后的 HLC |
| --- | --- | --- |
| a1 | A 在 p=100 发送 m | `(100,0)` |
| b1 | B 在 p=95 本地计算 | `(95,0)` |
| b2 | B 在 p=96 收到 m `(100,0)` | `(100,1)` |
| b3 | B 在 p=96 向 A 发送 n | `(100,2)` |
| a2 | A 在 p=99 收到 n `(100,2)` | `(100,3)` |
| a3 | A 的物理钟回到 p=98，再发生本地事件 | `(100,4)` |
| a4 | A 的物理钟前进到 p=101，本地事件 | `(101,0)` |
| c1 | C 在 p=100 独立计算，没有收到任何上述消息 | `(100,0)` |

沿 a1→b2→b3→a2，时间戳严格增加。a3 的物理钟更小，HLC 仍大于 a2；a4 的物理分量前进，计数重新从零开始。这个机制维护的是事件顺序，不是修好了 A 的物理钟，也不表示 a2 到 a3 经过了 1 毫秒。

## 因果在先推出较小，较小不能反推因果

在上述模型中，本地连续事件及消息发送到接收都严格递增，传递闭包也保留这一关系，故 `e → f` 可推出 `H(e) < H(f)`。但 c1 与 b2 没有信息路径，即使 `(100,0) < (100,1)`，也不能说 C 的更新已被 B 看见。

两个不同节点还可产生相同时间戳，a1 与 c1 就都是 `(100,0)`。按 `(l,c,node_id)` 再排序可以消除这两个事件的平局，但它只是确定性排序规则；身份和计数复用仍需处理，不能直接把 HLC 当作天然全局唯一事件 ID。区别见[分布式 ID](distributed-identifiers-time-and-uniqueness.md)。

需要判断两个版本是否并发时，应保留协议所需的因果上下文，例如[向量时钟](logical-clocks-causality-and-concurrency.md)。只保存一个 HLC 最大值，会丢掉这种区分能力。按最大时间戳覆盖值也只是选定的冲突政策，不能保证保留所有用户意图。

## 接近物理时间的界来自假设

报告对 l 与物理读数之差的界，依赖相应的物理时钟同步约束。HLC 更新本身不会证明 NTP 正常，也不会为任意回拨、未来消息或损坏状态建立一个固定误差界。本文表格允许局部回拨以说明递增规则，未据此验证该报告全部有界性前提。

假设误配置节点发送“未来一天”的 l，其他节点若直接合并，就可能把这个未来分量继续传播。工程实现需要定义可接受的时钟范围、异常来源处置与恢复方式；拒绝消息、停止相关工作或重新加入各有可用性成本，不能先接受并对外发布，再随意把 l 调小来修正。

[CockroachDB 事务层文档](https://www.cockroachlabs.com/docs/stable/architecture/transaction-layer.html#max-clock-offset-enforcement)把 HLC 传播和最大[时钟偏差](../../glossary/distributed.md#distributed.clocks)约束分开描述，说明真实产品还维护这些运行前提。这里按核查日 stable 文本理解机制，不把其阈值、[隔离级别](../../glossary/database.md#database.isolation)行为或故障处置推广成 HLC 的统一规定，也未验证某个部署。

有限计数字段同样有边界：若物理分量长时间不前进，c 可能连续递增。具体实现必须规定字段宽度、溢出处理和恢复策略；静默回绕不保留严格递增。重启若忘掉已对外使用的时钟状态，也不能无条件声称新输出仍位于旧输出之后。持久化、等待或协议化恢复要与存储和身份生命周期一起设计。

## 时间戳不替代期限、提交和读取屏障

| 工程判断 | 除 HLC 外还要什么 |
| --- | --- |
| 一个请求是否超过本机预算 | 适当的本机经过时间来源，以及暂停/重启语义 |
| 写入是否已经成功提交 | 实际复制、事务和确认协议 |
| 某时点的读取是否完整 | 已提交版本、应用进度及不会再出现更早相关写入的协议证据 |
| 旧执行者是否还能写资源 | 资源端验证的资格代次或其他隔离条件 |

Linux 的 [`clock_gettime` 手册](https://man7.org/linux/man-pages/man3/clock_gettime.3.html)区分可跳变的 `CLOCK_REALTIME` 与本机单调时钟。HLC 的差值也不能直接用作可靠经过时间：c 是计数，l 可能来自其他节点且领先本机；跨节点的“现在减时间戳”仍需时间误差模型。

给写入分配了 T，不表示它已经提交或已被所有读取副本应用。观察到某个更大的 T2，也不能排除较早工作仍未完成。CockroachDB 文档的 [Closed timestamps](https://www.cockroachlabs.com/docs/stable/architecture/transaction-layer.html#closed-timestamps)另行说明某范围内不会再产生更早写入的读取依据；它不是“拿到一个较大 HLC”的同义词。一般投影的连续进度另见[索引重建水位](../cache-search/index-rebuild-watermarks-and-cutover.md)，排他执行另见[Fencing](leases-heartbeats-and-fencing.md)。

## 五道自检与核查范围

1. l 与 c 各记录什么？为何接收 `(100,7)` 时不能一律清零，物理读数 101 又为何允许清零？
2. 复算 b2、a2、a3、a4；哪几条边保证时间戳严格递增，哪次回拨没有改变逻辑顺序？
3. c1 与 b2 的大小、a1 与 c1 的相等分别能说明什么？加入 node_id 后为何仍不能反推因果？
4. 任意未来消息、计数溢出和重启遗忘分别破坏哪种前提？HLC 是否自己提供可信物理误差界？
5. 为什么不能用 `(100,4)-(100,3)` 测量时长，也不能从已见较大时间戳推出提交、完整读取或旧执行者已隔离？

核查日期：2026-10-23。实际读取 Kulkarni 等 2014-04 技术报告的 §3.3 更新、图 5、单向因果定理及有界性前提；CockroachDB stable 的 HLC、偏差约束、提交与 closed timestamps 相关段；Linux 时钟接口的物理/单调区别。报告使用可读取的技术报告版本，失败的作者旧 publications 链接不计已读；产品与手册按核查日文本限定。未执行 HLC、校时/回拨、重启持久化、溢出、集群故障、快照读取或性能实验，没有验证具体数据库的一致性。
