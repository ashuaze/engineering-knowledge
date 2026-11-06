<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# 分布式系统

建议优先级：P1。目标：明确故障模型、一致性范围与协调成本。

下方术语用于知识索引。建议从[实际工程问题](../../problems.md)或本页核心问题进入，结合已有正文理解机制、适用边界与相关概念。

## 一个核心问题

[租约](../../glossary/distributed.md#distributed.fencing)过期的旧持有者恢复后，如何避免继续写入？

## 已有正文

- [CAP 与 PACELC：分区和延迟下，一次操作还能承诺什么](cap-pacelc-and-operation-guarantees.md)：从两副本断联的读写历史解释 [CAP](../../glossary/distributed.md#distributed.cap) 的形式边界，区分超时与未知提交，并用 PACELC 分析正常通信时的[延迟](../../glossary/performance.md#performance.latency-throughput)和一致性取舍。
- [共识与 Quorum：多数响应为什么还不等于一致决定](consensus-leaders-and-quorums.md)：区分复制、[选主](../../glossary/distributed.md#distributed.leadership)、[共识](../../glossary/distributed.md#distributed.consensus)与法定集合，说明相交条件、日志规则、读取保证和分区下的推进边界。
- [一致性与复制：写入成功后为什么仍可能读到旧值](consistency-and-replication.md)：区分复制进度、单对象读取保证、[事务隔离](../../glossary/database.md#database.isolation)和业务约束，明确结果可见的边界。
- [一致性哈希与数据放置：节点变化后哪些键需要搬走](consistent-hashing-placement-and-rebalancing.md)：用可复算的哈希环解释局部映射变化、虚拟节点和权重，区分键分布、副本[故障域](../../glossary/reliability.md#reliability.fault-domains)与真实迁移协议。
- [CRDT：怎样合并并发更新，收敛又没有保证什么](crdts-convergence-and-concurrent-merge-semantics.md)：以逐副本计数器和带标签的观察删除集合解释合并条件、并发语义与元数据责任，区分收敛、业务约束和持久化。
- [分布式 ID：唯一、可排序与业务只执行一次分别依赖什么](distributed-identifiers-time-and-uniqueness.md)：比较集中序列、经典 Snowflake、[UUIDv4](../../glossary/distributed.md#distributed.uuid)/v7 与 [ULID](../../glossary/distributed.md#distributed.ids)，说明唯一性条件、时间排序、状态恢复和业务权限的边界。
- [混合逻辑时钟：时间戳怎样尊重因果，又保留物理时间参照](hybrid-logical-clocks-and-timestamp-boundaries.md)：用可复算的 [HLC](../../glossary/distributed.md#distributed.hlc) 更新说明物理分量、逻辑计数与因果单向保证，区分时间戳、经过时间、提交及安全读取边界。
- [租约与 Fencing：锁过期后怎样拒绝旧执行者](leases-heartbeats-and-fencing.md)：区分故障怀疑、限时持有与写入代次校验，解释旧[进程](../../glossary/systems.md#systems.execution-units)恢复、迟到请求和权威存储的责任。
- [逻辑时钟与因果关系：编号更大为什么不代表已经看过另一事件](logical-clocks-causality-and-concurrency.md)：从 happened-before 解释 Lamport 与[向量时钟](../../glossary/distributed.md#distributed.vector-clocks)，区分因果、并发、全序、物理时间、版本和提交进度。
- [共识成员变更与分区恢复：谁有资格决定下一条日志](membership-changes-and-partition-recovery.md)：用跨配置多数反例解释[成员变更](../../glossary/distributed.md#distributed.membership)、learner 与扩容门槛，区分分区追赶、失多数恢复和外部旧执行者隔离。
- [跨服务事务：2PC、Saga 与补偿恢复](two-phase-commit-sagas-and-recovery.md)：从部分成功解释[两阶段提交](../../glossary/distributed.md#distributed.2pc)的持久决议与阻塞，以及 [Saga](../../glossary/distributed.md#distributed.saga) 的本地提交、业务补偿、并发隔离和恢复责任。

## 术语范围

| 术语 | 简释 |
| --- | --- |
| [CAP / PACELC](../../glossary/distributed.md#distributed.cap) | CAP 限定分区模型下[线性一致性](../../glossary/distributed.md#distributed.linear-serial)与请求最终完成无法同时保证；PACELC 还分析正常通信时延迟与一致性的设计取舍。 |
| [Strong / Eventual Consistency](../../glossary/distributed.md#distributed.consistency) | 不同可见性保证，强一致须进一步说明具体模型。 |
| [Linearizability / Serializability](../../glossary/distributed.md#distributed.linear-serial) | 实时单操作顺序与事务可串行执行的等价性。 |
| [Consensus / Raft](../../glossary/distributed.md#distributed.consensus) | 在故障模型下就日志或状态达成一致。 |
| [Leader Election / Quorum](../../glossary/distributed.md#distributed.leadership) | 选主与按法定集合达成读写条件。 |
| [Heartbeat / Lease / Fencing Token](../../glossary/distributed.md#distributed.fencing) | 存活检测、限时持有与拒绝过期执行者。 |
| [Replication Lag](../../glossary/distributed.md#distributed.lag) | 副本应用变更落后于上游。 |
| [Split Brain](../../glossary/distributed.md#distributed.split-brain) | 多个节点同时认为自己拥有权威。 |
| [Network Partition](../../glossary/distributed.md#distributed.partition) | 节点间通信被切断或严重不可达。 |
| [Distributed Transaction / 2PC](../../glossary/distributed.md#distributed.2pc) | 跨参与者协调提交及其阻塞等成本。 |
| [Saga / Compensation](../../glossary/distributed.md#distributed.saga) | 多步业务通过补偿应对部分成功。 |
| [Consistent Hashing](../../glossary/distributed.md#distributed.hashing) | 减少节点变化时键重新分布的范围。 |
| [Logical Clock / Clock Skew](../../glossary/distributed.md#distributed.clocks) | 因果顺序表示与物理时钟偏差。 |
| [Snowflake ID / ULID](../../glossary/distributed.md#distributed.ids) | 对照基于节点与序列的Snowflake类ID和基于时间与随机部分的ULID，按各自条件判断唯一性与排序。 |
| [Vector Clock](../../glossary/distributed.md#distributed.vector-clocks) | 以参与者计数向量表达因果包含，逐维比较区分后继与并发；精确性依赖身份、更新和上下文传播规则。 |
| [UUIDv4 / UUIDv7](../../glossary/distributed.md#distributed.uuid) | RFC9562中的128位标识格式；v4采用122位随机数据，v7组合时间前缀与随机或可选单调构造，保证仍依赖版本和实现。 |
| [Membership Reconfiguration](../../glossary/distributed.md#distributed.membership) | 按协议改变复制组的投票资格与法定集合，保护新旧配置之间的决定关系。 |
| [Hybrid Logical Clock](../../glossary/distributed.md#distributed.hlc) | 结合已知物理分量与逻辑计数，让已编码的因果边对应严格递增时间戳。 |
| [Conflict-free Replicated Data Type](../../glossary/distributed.md#distributed.crdt) | 把允许更新、并发语义与合并规则共同设计，在传播前提成立时使同一对象的副本收敛。 |

## 练习与验收

选择上面的一个核心问题，先画执行过程或数据边界，再构造一个正常路径和一个失败路径。用原理解释、架构或代码、诊断证据和取舍依据说明保证范围；记录已完成验证与待验证项。

[回到知识地图](../../map.md) · [问题导航](../../problems.md) · [学习路径](../../paths/index.md)
