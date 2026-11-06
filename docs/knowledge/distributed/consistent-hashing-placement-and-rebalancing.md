---
id: "kb-distributed-consistent-hashing"
title: "一致性哈希与数据放置：节点变化后哪些键需要搬走"
kind: "concept"
domain: "distributed"
status: "evolving"
summary: "用可复算的哈希环解释局部映射变化、虚拟节点和权重，区分键分布、副本故障域与真实迁移协议。"
created: "2026-10-22"
updated: "2026-10-22"
last_verified: "2026-10-22"
verification: "source-checked"
prerequisites: ["kb-algorithms-hash-tables", "kb-distributed-consistency"]
related: ["kb-distributed-consensus-quorum", "kb-distributed-leases-fencing", "kb-reliability-fault-domains-recovery", "kb-cache-search-index-cutover", "kb-messaging-partitions-offsets", "kb-database-partitioning-sharding", "kb-distributed-membership-recovery"]
tags: ["consistent-hashing", "placement", "virtual-node", "rebalancing"]
---

# 一致性哈希与数据放置：节点变化后哪些键需要搬走

学习入口：缓存从三台扩到四台，为什么大量请求突然回源？若直接使用 `hash(key) mod N`，N 变化会改变许多键的余数。[一致性哈希](../../glossary/distributed.md#distributed.hashing)让成员变化主要影响一部分映射；真正让新位置拥有完整数据，还需要迁移、路由和恢复协议。

前置：[哈希表与键契约](../algorithms/hash-tables-collisions-and-key-contracts.md)、[一致性与复制](consistency-and-replication.md)。本文解释常见哈希环模型，不将所有[分片](../../glossary/database.md#database.partitioning)系统都归为同一种实现；固定槽位、范围分片及其他放置算法需要分别分析。

## 普通取模为何容易大范围换位置

纸面设定：键的哈希值恰为 0–11，旧节点编号为 0、1、2，新增节点编号 3，比较两种映射：

| 哈希值 | `h mod 3` | `h mod 4` | 是否变化 |
| --- | --- | --- | --- |
| 0–2 | 0、1、2 | 0、1、2 | 均不变 |
| 3–5 | 0、1、2 | 3、0、1 | 均变化 |
| 6–8 | 0、1、2 | 2、3、0 | 均变化 |
| 9–11 | 0、1、2 | 1、2、3 | 均变化 |

十二个键中九个改变归属。该比例来自这组教学数据，不是任意键集的固定迁移率。对于在完整共同周期内均匀分布的哈希值，从 N 变成 N+1 时，相同编号仅占 `1/(N+1)`；普通取模也并非每个键必搬。

[Karger 等人的原始一致性哈希论文](https://people.csail.mit.edu/karger/Papers/web.pdf)第 4 节研究成员视图变化时映射的平滑性、单调性与负载等性质。这里的“consistent”指映射变化性质，不能据词名推导数据读取具有[线性一致性](../../glossary/distributed.md#distributed.linear-serial)，也不能理解为所有成员已经达成同一决定。

## 固定坐标，沿顺时针选择归属

常见环模型把哈希空间首尾相接，键与节点 token 都落在其中。键归属于沿约定方向遇到的第一个 token 的物理节点。[Dynamo 原论文](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf)第 4.2 节介绍了这一环形放置及多 token 思路；下面固定端点规则，单独进行教学推演。

设坐标为整数 0–99，单位是“哈希槽”，不是字节或时间。顺时针为数值递增，99 之后回到 0；每个 token 接收前一个 token 之后、自己所在位置及之前的键，即区间 `(前驱, 自己]`。键恰落在 token 上时归属该 token。A、B、C 的 token 分别为 10、40、80。

| 环区间 | 旧归属 | 在 60 加入 D 后 | C 之后退出时 |
| --- | --- | --- | --- |
| `(80,10]`，即 81–99、0–10 | A | A | A |
| `(10,40]`，即 11–40 | B | B | B |
| `(40,60]`，即 41–60 | C | D | D |
| `(60,80]`，即 61–80 | C | C | A |

加入 D 时，只有 `(40,60]` 改变主归属，从 C 转给 D；再移除 C 时，只有 C 当时持有的 `(60,80]` 转给 A。例如键 55 的路线是 C→D→D，键 75 是 C→C→A，键 95 一直归 A。这里每步都保持其他 token 不动，且只算单份主归属。

在这一固定环中，D 实际接收 20 个槽，占整个空间 20%。若键在槽间均匀，预期约 20% 的键改变归属；若所有键都恰好落在 55，改变的就是全部键。常见“新增一台平均移动约 `1/(N+1)`”还依赖新旧节点等权、token 的可交换随机分布和键分布等前提，不能当作每次扩容的上限。

## 虚拟节点改善分配粒度，也增加管理成本

一个物理节点可持有多个分散 token，称为虚拟节点。新增物理节点会接收多个小区间，退出时也可把区间交给多个接收者；可以通过 token 数量或分配策略表达不同容量权重，但目标比例仍需检查实际区间和数据量。

多个随机位置能降低单一位置偶然占很大区间的影响，却不保证每次字节、请求数和 CPU 成本都相等。虚拟节点还增加 token 元数据、邻接关系和迁移任务；不能无限增加后只看平均负载。[Cassandra 架构文档](https://cassandra.apache.org/doc/latest/cassandra/architecture/dynamo.html)讨论了多 token 的收益与代价，具体数量和分配算法应按部署版本核对。

环上键数均衡，也不能拆开一个超热键或超大对象。[热点](../../glossary/performance.md#performance.contention)读取可能需要额外缓存、副本或请求合并；拆分业务键会改变数据模型。容量权重只能改变分配目标，不能使每个键的处理成本自动相同。

## 主归属之外，还要算副本与故障域

若复制因子为 3，不能简单取接下来的三个 token：它们可能属于同一物理节点。副本选择需跳过重复物理节点，还要按机架、可用区等[故障域](../../glossary/reliability.md#reliability.fault-domains)约束放置。[Cassandra 的复制策略说明](https://cassandra.apache.org/doc/latest/cassandra/architecture/dynamo.html)区分物理节点去重及机架、数据中心策略；三个副本共享一个共同失效范围，保护能力会不同。

增加一个节点可能改变主归属之外的副本集合。因此“主键只移动一小段”不能直接推导“只传同样比例的网络字节”，也不能说每次只影响一台相邻物理机器。虚拟节点、复制、故障域策略或额外重新分配 token，都可能扩大参与者范围。

纸面成本：有 10,000 个键，1,000 个键换位置，键数变化率为 10%。如果这 1,000 个键各占 10 MiB，其余各占 1 KiB，单份待搬数据就是 10,000 MiB，约占总数据字节的 99.9%。传输副本、索引、日志与校验还会增加成本；耗时又受可用带宽、磁盘、限速和迁移期间新增写入影响。这个算式不是性能实测。

## 映射切换与数据搬运是两个状态过程

同一个键和[哈希函数](../../glossary/algorithms.md#algorithms.hash-table)，在成员视图不同时仍可能得到不同归属。例如旧客户端把 55 发给 C，新客户端把它发给 D；算法并不自动让两边知道谁已接管。成员配置、变更序列与发布协议决定路由何时生效，需要明确管理；若使用[共识](../../glossary/distributed.md#distributed.consensus)登记配置，也不能把它的保证直接扩大到所有数据写入。

下面是迁移协议需要回答的问题，用于审阅设计，并非任何产品通用的操作步骤：

| 阶段 | 要证明什么 | 典型失败窗口 |
| --- | --- | --- |
| 建立目标范围 | 新旧成员视图、迁移代次、源和目标明确 | 客户端仍缓存旧映射，多个变更重叠 |
| 复制与追赶 | 存量及期间的新增、更新、删除都有接续路径 | 先复制旧值，后漏掉删除或覆盖新值 |
| 接管读写 | 路由条件与目标就绪条件共同满足 | 新节点有 token 但尚未完整，旧节点继续收写 |
| 故障后恢复 | 进度可恢复，重放安全，源仍能提供缺口 | [超时](../../glossary/api.md#api.retries)被误当作未写入，重试造成重复副作用 |
| 回收旧数据 | 已无依赖旧数据的读写，回退与修复窗口结束 | 过早清理，失去唯一完整副本 |

系统可能用转发、迁移期写入扩散、版本比较、日志追赶和修复等不同组合封闭这些窗口，不能只增加一个“双写”步骤就宣布完整。[Cassandra 拓扑变更文档](https://cassandra.apache.org/doc/latest/cassandra/managing/operating/topo_changes.html)明确区分 token 分配、范围数据传输、引导恢复与旧数据清理；新映射存在不是传输完成的证据。

缓存与持久存储也有不同恢复条件：缓存可能允许丢弃并回源，但要预算集中未命中的冲击；持久数据若没有可用完整副本，重新计算映射不会把内容恢复出来。接管后拒绝旧写者的责任可对照[租约与 Fencing](leases-heartbeats-and-fencing.md)，快照与增量衔接可对照[索引重建与切换](../cache-search/index-rebuild-watermarks-and-cutover.md)。

一致性哈希只是一类键放置方案。范围、哈希和目录式分片如何影响裁剪、跨片查询、约束与接管，继续见[分区、分片与数据路由](../database/partitioning-sharding-and-data-routing.md)。

投票成员的配置交叠与失多数后的恢复，继续见[共识成员变更与分区恢复](membership-changes-and-partition-recovery.md)。哈希映射和搬迁负责数据归属，不能替代投票资格及日志接受规则。

## 自检、关联与核查范围

自检：D 已加入、C 尚未退出时，键 60、80、0 分别归谁？为什么多虚拟节点仍解决不了一个占一半流量的键？若所有客户端已拿到新映射，但 D 只复制了一半数据，能否宣布扩容完成？

继续读[故障域、冗余与恢复目标](../reliability/failure-domains-redundancy-and-recovery.md)，评估副本独立性与剩余容量；读[共识与 Quorum](consensus-leaders-and-quorums.md)，区分成员决定、法定集合和数据提交；读[分区、消费组与偏移](../messaging/partitions-consumer-groups-and-offsets.md)，比较分工变化与业务完成的边界。消息分区重新分配不必采用本文的哈希环。

核查日期：2026-10-22。核查了 Karger 等人原论文第 4 节的映射性质、Dynamo 第 4.2 节的环和 token 思路，以及当日 Cassandra 官方文档展示的 5.0 架构与拓扑变更机制；滚动文档中的具体配置需按实际版本复核。本文的取模、0–99 环、迁移字节和阶段表均为教学推演与设计检查，不是 Cassandra 的完整迁移规范。未部署集群、调整 token、传输数据、注入故障或执行性能测试。
