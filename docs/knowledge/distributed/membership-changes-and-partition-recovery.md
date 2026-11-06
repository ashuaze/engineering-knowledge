---
id: "kb-distributed-membership-recovery"
title: "共识成员变更与分区恢复：谁有资格决定下一条日志"
kind: "concept"
domain: "distributed"
status: "evolving"
summary: "用跨配置多数反例解释成员变更、learner 与扩容门槛，区分分区追赶、失多数恢复和外部旧执行者隔离。"
created: "2026-10-22"
updated: "2026-10-23"
last_verified: "2026-10-22"
verification: "source-checked"
prerequisites: ["kb-distributed-consensus-quorum", "kb-distributed-consistency"]
related: ["kb-distributed-cap-pacelc", "kb-distributed-leases-fencing", "kb-distributed-consistent-hashing", "kb-database-backups-pitr", "kb-api-idempotency", "kb-distributed-crdt"]
tags: ["membership", "quorum", "learner", "partition-recovery", "raft"]
---

# 共识成员变更与分区恢复：谁有资格决定下一条日志

学习入口：三个投票成员只剩两个互通时，为什么直接加入一台尚未就绪的投票成员，可能让剩余两台也无法继续写？网络恢复后，旧主保存的写入能直接拼到新主后面吗？前置：[共识与 Quorum](consensus-leaders-and-quorums.md)、[一致性与复制](consistency-and-replication.md)。成员配置规定谁有资格参与决定，故障检测只说明目前观察到了谁；改变前者本身也需要协议保护。

本文以 [Raft](../../glossary/distributed.md#distributed.consensus) 的非拜占庭故障模型为背景，区分 2014-05-20 的 Extended Version 论文、`etcd-io/raft v3.6.0` 库说明与 etcd v3.6 运维接口。集合、门槛和时间线均为纸面推演；没有部署集群、执行扩缩容、分区或恢复操作，也不提供可直接执行的生产恢复步骤。

## 成员资格、健康状态与数据位置分别是什么

| 对象 | 回答的问题 | 不能据此推出什么 |
| --- | --- | --- |
| 当前投票配置 | 哪些身份可投票、怎样计算法定集合 | 所有成员此刻都可达 |
| [心跳](../../glossary/distributed.md#distributed.fencing)与通信观测 | 最近哪些节点能响应 | 失联者已永久停止，或已被移出配置 |
| Learner / 非投票成员 | 哪些节点接收日志但尚不计入投票多数 | 已有资格帮助提交或接替领导者 |
| 键放置与再均衡 | 哪些位置应保存或处理哪些数据 | 已完成共识[成员变更](../../glossary/distributed.md#distributed.membership)或真实数据追赶 |

因此，配置有五个投票成员、当前只有两个可达时，多数仍是三，不能临时按“两台存活机器的多数”计算。删除失联节点也不是本地改一份名单：[etcd v3.6 重配置说明](https://etcd.io/docs/v3.6/op-guide/runtime-configuration/#cluster-reconfiguration-operations)要求变更前已有多数成员可用，并串行处理变更。

[一致性哈希](../../glossary/distributed.md#distributed.hashing)决定键映射怎样随放置视图变化；共识成员变更决定一份复制日志由谁共同维护。某系统可以用共识保存路由元数据，仍需另外完成数据复制与接管，见[一致性哈希与数据放置](consistent-hashing-placement-and-rebalancing.md)。

## 旧、新配置各自有多数，为什么仍可能冲突

纸面反例：旧配置是 `C_old = {A,B,C}`，新配置是 `C_new = {A,B,C,D,E}`。若节点各自直接切换名单，`{A,B}` 达到旧配置的二成员多数，`{C,D,E}` 达到新配置的三成员多数，两组却没有交集。这里描述的是错误切换规则允许的计数，不是说正确 Raft 会认可两个相互冲突的提交。

[Raft Extended Version §6、图 10–11](https://raft.github.io/raft.pdf)通过中间联合配置 `C_old,new` 连接两个阶段：联合阶段的选举和提交分别需要旧配置多数与新配置多数；不是在并集里只数一个多数。联合配置提交后，才进入最终新配置的阶段，最终配置按新配置规则提交。

| 同一轮得到的不同成员集合 | 旧侧至少 2 | 新侧至少 3 | 联合阶段的人数条件 |
| --- | --- | --- | --- |
| `{A,B}` | 满足 | 不满足 | 不满足 |
| `{C,D,E}` | 不满足 | 满足 | 不满足 |
| `{A,B,C}` | 满足 | 满足 | 满足 |

同一个成员可同时属于两种配置，两项条件不要求人数相加。满足表中人数条件还要遵守任期、日志新旧、持久化和提交规则，不能把任意响应当成确认。

论文将配置作为日志条目传播，各节点按自己日志中的最新配置行动，具体生效点也属于协议。各节点无需在同一物理时刻收到配置，但不能让旧、新配置无约束地独立决定。联合阶段若无法同时凑齐所需集合，可以暂停推进；这种等待不意味着安全规则失效。

## 单节点增量变更不是任意批量改名单

另一条受约束的路径是每次只改变一个投票成员。以 `{A,B,C}` 增加 D 为例，旧多数是 2，新多数是 3；两集合都来自四个身份，而 `2+3>4`，所以任意这样的旧、新多数相交。若一次从三变五，前面的不相交反例就重新出现。集合交叠只解释一个必要关系，不替代整个变更协议。

[`etcd-io/raft v3.6.0` README 的 Implementation notes](https://github.com/etcd-io/raft/blob/v3.6.0/README.md#implementation-notes)对其增量变更路径说明：配置条目按旧配置提交，在应用条目时生效；领导者日志中尚有未提交成员变更时，禁止再提议一个。这与上述论文“写入日志即按最新配置行动”的表述不同，不能把二者拼成一套实现步骤，也不能仅凭 README 这一段推断该库所有配置接口的能力。

评审具体系统时，要同时核对“一次改变多少成员”“哪个配置提交这条变更”“何时生效”“上一次变更何时算完成”。只限制运维界面一次点一个节点，仍不足以证明后台不会重叠变更。成员身份也不能仅按可复用 [IP](../../glossary/networking.md#networking.transport) 识别；该库要求节点 ID 在同一集群历史中不被重复使用。

## Learner 先追赶，投票门槛后改变

新增机器可能没有历史数据。若立刻给它投票权，门槛已经变化，它却还不能提供有效进度。[etcd v3.6 learner 设计](https://etcd.io/docs/v3.6/learning/design-learner/)解释了追赶流量和扩容带来的可用性压力；[该版本运维说明](https://etcd.io/docs/v3.6/op-guide/runtime-configuration/#add-a-new-member-as-learner)将添加非投票成员、启动追赶、检查后提升分开。

以下只计算稳定配置中的简单多数，假设 A、B 可用，C 暂时失联，D 尚未准备好：

| 状态 | 投票成员数 | 多数门槛 | A、B 是否够数 |
| --- | --- | --- | --- |
| 原配置 ABC | 3 | 2 | 够；仍需完整协议条件 |
| D 作为 learner 加入 | 3 | 2 | 人数条件不变 |
| D 直接成为投票成员 | 4 | 3 | 仅 A、B 不够 |
| D 已追赶并安全提升，A、B、D 可用 | 4 | 3 | 三者够；仍需实际通信与协议条件 |

从三变四后，容忍的投票成员故障数仍是一个；多一台机器并未在这个阶段增加简单多数的故障容忍数。若启用了 etcd 默认的严格重配置检查，某些导致已启动成员不足新多数的请求会先被拒绝，表中第三行不能当作必然可提交的操作。

Learner 不投票，不能补齐已经缺失的多数；添加、提升本身也要由仍能推进的集群处理。[进程](../../glossary/systems.md#systems.execution-units)已启动、网络端口可达，不等于日志已追赶。etcd 会检查提升条件，未满足可拒绝；非投票仍有复制与资源成本，不应让追赶耗尽现有集群的带宽和执行资源。设计文中的未来构想，也不能当作 v3.6 已提供的自动行为。

## 分区恢复要协调历史，超时结果另行核对

教学设定：固定五投票成员 A–E，已提交前缀到索引 `k−1`。A 是旧领导者，随后分成 AB 与 CDE；未发生成员变更，持久化和日志规则均正确。

| 时刻 | 纸面事件 | 能判断什么 |
| --- | --- | --- |
| t0 | A 把 x 写到自己及 B 的索引 k，尚无第三个确认 | x 不能仅凭这两个副本宣布提交 |
| t1 | 调用方等待 x 超时；CDE 在更高任期选出合法新主 | 超时只结束等待；本例已知 x 未提交，不代表任意超时都如此 |
| t2 | 新主按完整协议在索引 k 提交 y | 新提交历史不能被旧主未提交尾部随意替换 |
| t3 | 通信恢复，AB 接受当前权威并修复不匹配尾部 | x 可被覆盖；不是把 x、y 按到达顺序拼接 |

[etcd v3.6 故障说明](https://etcd.io/docs/v3.6/op-guide/failures/#network-partition)区分多数侧与少数侧，并说明恢复后重新同步。旧主仍运行或短暂自认为主，不等于它能提交新日志；能否提供某种本地旧值读取，也不能替代当前线性一致读的条件。

另一种执行中，写入可能已经提交，只是响应丢失。[etcd v3.6 API 保证的 Operation completed](https://etcd.io/docs/v3.6/learning/api_guarantees/#operation-completed)明确了超时或通信中断带来的结果不确定。业务应携带稳定动作标识，按协议查询或去重，而不是恢复后换一个 ID 无条件再做，见[幂等性](../api/idempotency.md)。日志修复不会追回旧执行者已发出的外部扣款；实际资源仍需执行资格检查与[代次隔离](leases-heartbeats-and-fencing.md)。

## 快照追赶与失多数后重建，恢复边界不同

Raft 日志压缩快照表示已应用的已提交状态；论文 §7 还保留覆盖到的索引、任期及该位置的成员配置，用来解释后续日志。只复制一份业务键值，不能由此重建任意 Raft 节点所需的完整协议状态。正常节点重启还要恢复所需持久状态；日志已被压缩的落后节点可能需要协议快照继续追赶。

etcd 运维导出的键空间快照另有用途。按 [v3.6 灾难恢复文档](https://etcd.io/docs/v3.6/op-guide/recovery/#restoring-from-snapshot)，从它重建会创建新数据目录并重写成员 ID、集群 ID，形成新的逻辑集群；不是把一个 learner 直接补进失去多数的旧集群。

| 情况 | 恢复依据 | 仍需证明什么 |
| --- | --- | --- |
| 暂时失联，足够原成员能回来 | 原身份及有效持久状态恢复协议进度 | 配置、日志和实际应用进度正确 |
| 少数成员永久损坏，当前仍有多数 | 经现有协议串行替换和追赶 | 每一步门槛、完成条件和资源余量 |
| 多数永久丢失，无法按原配置继续 | 选定恢复材料，另建受控的新逻辑集群 | 可恢复的数据边界、旧集群隔离、客户端与外部业务重接 |

最后一行不延续“当前旧多数已经证明”的论证。快照只覆盖制作时的历史，之后已确认的写入可能不在其中；直接复制 etcd 的数据库文件还可能漏掉仅在 [WAL](../../glossary/database.md#database.recovery-log) 中的数据。需记录恢复目标、材料身份和可能损失，不能声称“恢复成功所以所有成功写都还在”。备份制作与业务验收的区别见[备份与时间点恢复](../database/backups-and-point-in-time-recovery.md)。

在重建接受新写入前，应让旧成员和旧客户端路径无法继续作为另一套业务权威，并处理外部旧执行者。新的随机集群 ID 本身不等于可比较、递增的 fencing 代次；恢复后的计数也可能低于外部资源已见值，需要共同设计恢复纪元与接受规则。etcd 的成员隔离机制不自动隔离所有外部副作用。

etcd v3.6 恢复文档还说明：回退后的 revision（键空间的逻辑修订号）可能与 watch（从指定修订位置订阅变更）的消费者、控制器本地缓存冲突。revision bump 提高恢复后的修订号；配合把此前位置标为已压缩，使旧订阅失效，消费者再按其协议重取视图。消费者仍需正确处理订阅终止或已压缩结果；这些机制处理通知与缓存衔接，不补回丢失数据。该文档强烈不鼓励把 `force-new-cluster` 当日常修复手段，尤其不能忽略旧成员仍存活的情况。本文仅解释边界，具体恢复需按真实版本、材料、隔离条件与业务目标另行演练。

允许并发更新的对象怎样合并与保留删除上下文，另见[CRDT](crdts-convergence-and-concurrent-merge-semantics.md)。[CRDT](../../glossary/distributed.md#distributed.crdt) 写者/清理身份与本篇投票成员不是同一契约；收敛规则不能替代复制组的配置交叠、权威隔离或备份恢复协议。

## 五道自检与核查范围

1. 旧配置 ABC 的 AB 多数与新配置 ABCDE 的 CDE 多数为什么不相交？联合配置怎样判断 ABC 的确认，为什么不能只数并集多数？
2. 单节点增量变更依赖哪些配置交叠、串行化与生效规则？为什么“每次只点一个节点”仍不等于协议正确？
3. ABC 中只有 AB 可用时，D 作为 learner 或直接成为投票成员，门槛分别是多少？learner 为什么不能修好只剩 A 的原集群？
4. 分区后旧主的未提交尾部、已经提交但响应丢失的写、外部已经发生的扣款，各应怎样处理？为什么不能统一叫作回滚[重试](../../glossary/api.md#api.retries)？
5. 从旧快照重建新逻辑集群后，哪些历史、成员身份、revision/watch 缓存和外部执行资格必须重新核对？新的集群 ID 为什么不能直接替代 fencing 代次？

核查日期：2026-10-22。下面的一手来源已实际联网读取；集合反例、门槛表、t0–t3 与恢复责任表是教学综合，不是协议实现或生产操作手册。未启动 etcd/Raft、变更成员、执行 learner 提升、注入分区、重启或安装快照，也未恢复集群、运行强制重建、测量可用性或验证外部副作用隔离。

| 一手资料与固定范围 | 本文实际使用部分 |
| --- | --- |
| [Ongaro、Ousterhout，Raft Extended Version，2014-05-20](https://raft.github.io/raft.pdf) | §6 的直接切换反例、联合配置与非投票追赶；§7 的协议快照元数据；不是完整实现规范 |
| [`etcd-io/raft v3.6.0` README](https://github.com/etcd-io/raft/blob/v3.6.0/README.md) | Implementation notes 的增量变更、生效时机、串行约束与节点 ID；不泛化该说明为所有接口和实现 |
| [etcd v3.6 Runtime reconfiguration](https://etcd.io/docs/v3.6/op-guide/runtime-configuration/) | 当前多数、逐次变更、learner 添加/提升及严格检查；未照搬历史 v3.4 learner 数量为所有版本上限 |
| [etcd v3.6 learner design](https://etcd.io/docs/v3.6/learning/design-learner/) | 扩容门槛、追赶压力、已实现的非投票/提升机制；未来[设计提案](../../glossary/engineering.md#engineering.design-docs)不当作已实现能力 |
| [etcd v3.6 Failure modes](https://etcd.io/docs/v3.6/op-guide/failures/) | 多数失效、分区、未提交日志及恢复同步；不扩展到恶意节点模型 |
| [etcd v3.6 API guarantees](https://etcd.io/docs/v3.6/learning/api_guarantees/) | 读取范围与操作完成、超时结果不确定；不把 watch 或旧值读取等同于线性一致读 |
| [etcd v3.6 Disaster recovery](https://etcd.io/docs/v3.6/op-guide/recovery/) | 快照数据边界、新逻辑集群/身份、旧成员隔离、revision/watch 衔接与强制重建限制；未执行恢复 |
