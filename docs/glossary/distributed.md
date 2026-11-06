<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# 分布式系统词汇表

本页解释 19 组术语，按[完整术语索引](../glossary.md#distributed)中的顺序排列。示例为说明性场景；具体技术版本与验证范围见各条深入阅读。

[分类词汇表](index.md) · [分布式系统文章](../knowledge/distributed/index.md)

## 本页术语

- [CAP / PACELC](#distributed.cap)
- [Strong / Eventual Consistency](#distributed.consistency)
- [Linearizability / Serializability](#distributed.linear-serial)
- [Consensus / Raft](#distributed.consensus)
- [Leader Election / Quorum](#distributed.leadership)
- [Heartbeat / Lease / Fencing Token](#distributed.fencing)
- [Replication Lag](#distributed.lag)
- [Split Brain](#distributed.split-brain)
- [Network Partition](#distributed.partition)
- [Distributed Transaction / 2PC](#distributed.2pc)
- [Saga / Compensation](#distributed.saga)
- [Consistent Hashing](#distributed.hashing)
- [Logical Clock / Clock Skew](#distributed.clocks)
- [Snowflake ID / ULID](#distributed.ids)
- [Vector Clock](#distributed.vector-clocks)
- [UUIDv4 / UUIDv7](#distributed.uuid)
- [Membership Reconfiguration](#distributed.membership)
- [Hybrid Logical Clock](#distributed.hlc)
- [Conflict-free Replicated Data Type](#distributed.crdt)

<a id="distributed.cap"></a>

## CAP / PACELC

**ID：** `distributed.cap` · **建议优先级：** P1

**别名 / 检索词：** CAP、PACELC

**简释：** CAP 限定分区模型下线性一致性与请求最终完成无法同时保证；PACELC 还分析正常通信时延迟与一致性的设计取舍。

这是两个相关但不同的分析对象，不能作为同一定理或任意三选二使用。CAP 的 A 是非故障节点请求最终按操作规范完成，不是固定延迟或可用率；PACELC 的 Else 分支要求明确读写路径、配置和一致性目标，不给整个产品永久分类。

**例子：** 两个副本失联，甲已成功写1后乙才开始读；让两侧都完成请求无法同时保持线性一致。无分区时，等待哪些复制确认、从哪里读取仍会影响延迟和保证。

**深入阅读：** [CAP 与 PACELC：分区和延迟下，一次操作还能承诺什么](../knowledge/distributed/cap-pacelc-and-operation-guarantees.md)

<a id="distributed.consistency"></a>

## Strong / Eventual Consistency

**ID：** `distributed.consistency` · **建议优先级：** P1

**别名 / 检索词：** Strong、Eventual Consistency、最终一致性、强一致性

**简释：** 不同可见性保证，强一致须进一步说明具体模型。

一致性模型约定读写可观察的关系；强一致需要继续指明是否线性一致等具体保证。最终一致描述在相应条件下趋于收敛，并不承诺每次立即读到最新值。

**例子：** 购物车更新后读到旧副本，需检查是否满足产品承诺的读己之写。

**深入阅读：** [一致性与复制：写入成功后为什么仍可能读到旧值](../knowledge/distributed/consistency-and-replication.md) · [CAP 与 PACELC：分区和延迟下，一次操作还能承诺什么](../knowledge/distributed/cap-pacelc-and-operation-guarantees.md) · [CRDT：怎样合并并发更新，收敛又没有保证什么](../knowledge/distributed/crdts-convergence-and-concurrent-merge-semantics.md)

<a id="distributed.linear-serial"></a>

## Linearizability / Serializability

**ID：** `distributed.linear-serial` · **建议优先级：** P1

**别名 / 检索词：** Linearizability、Serializability、线性一致性、可串行化

**简释：** 实时单操作顺序与事务可串行执行的等价性。

线性一致性要求单操作可按尊重实时先后的顺序解释；可串行化要求并发事务结果等价于某个串行次序。两者作用范围和实时条件不同。

**例子：** 事务可串行化并不单独承诺跨服务读写都按现实时间先后可见。

**深入阅读：** [一致性与复制：写入成功后为什么仍可能读到旧值](../knowledge/distributed/consistency-and-replication.md) · [CAP 与 PACELC：分区和延迟下，一次操作还能承诺什么](../knowledge/distributed/cap-pacelc-and-operation-guarantees.md)

<a id="distributed.consensus"></a>

## Consensus / Raft

**ID：** `distributed.consensus` · **建议优先级：** P1

**别名 / 检索词：** Consensus、Raft、共识

**简释：** 在故障模型下就日志或状态达成一致。

共识算法在指定故障模型下让参与者就值或日志达成一致；Raft 通过任期、选主和复制日志维护安全性。获得领导者身份不等于任意写入都已提交。

**例子：** 领导者先复制日志到满足协议条件的多数节点，再确认相应提交。

**深入阅读：** [共识与 Quorum：多数响应为什么还不等于一致决定](../knowledge/distributed/consensus-leaders-and-quorums.md) · [共识成员变更与分区恢复：谁有资格决定下一条日志](../knowledge/distributed/membership-changes-and-partition-recovery.md)

<a id="distributed.leadership"></a>

## Leader Election / Quorum

**ID：** `distributed.leadership` · **建议优先级：** P1

**别名 / 检索词：** Leader Election、Quorum、选主、法定人数

**简释：** 选主与按法定集合达成读写条件。

选主决定协调角色，Quorum 是满足协议条件的节点集合。安全性依赖集合交叠、成员变化与协议规则，不能脱离复制和故障模型只套多数公式。

**例子：** 旧任期的多数信息不能被随意当作当前任期提交的充分证据。

**深入阅读：** [共识与 Quorum：多数响应为什么还不等于一致决定](../knowledge/distributed/consensus-leaders-and-quorums.md) · [CAP 与 PACELC：分区和延迟下，一次操作还能承诺什么](../knowledge/distributed/cap-pacelc-and-operation-guarantees.md) · [共识成员变更与分区恢复：谁有资格决定下一条日志](../knowledge/distributed/membership-changes-and-partition-recovery.md)

<a id="distributed.fencing"></a>

## Heartbeat / Lease / Fencing Token

**ID：** `distributed.fencing` · **建议优先级：** P1

**别名 / 检索词：** Heartbeat、Lease、Fencing Token、心跳、租约、栅栏令牌

**简释：** 存活检测、限时持有与拒绝过期执行者。

心跳是故障怀疑信号，租约给持有权期限，Fencing Token 由资源端比较代次拒绝旧持有者。网络延迟与进程暂停使本地存活判断不能直接代表排他权。

**例子：** 旧持有者暂停后恢复，资源端依据更高代次拒绝其迟到写入。

**深入阅读：** [租约与 Fencing：锁过期后怎样拒绝旧执行者](../knowledge/distributed/leases-heartbeats-and-fencing.md) · [共识成员变更与分区恢复：谁有资格决定下一条日志](../knowledge/distributed/membership-changes-and-partition-recovery.md)

<a id="distributed.lag"></a>

## Replication Lag

**ID：** `distributed.lag` · **建议优先级：** P1

**别名 / 检索词：** Replication Lag、复制延迟

**简释：** 副本应用变更落后于上游。

复制延迟可按日志位置、时间或应用进度描述，不同口径不能直接互换。落后副本影响新鲜度、故障切换损失和读一致性。

**例子：** 副本已接收日志但尚未应用时，读取仍可能缺少最新变更。

**深入阅读：** [一致性与复制：写入成功后为什么仍可能读到旧值](../knowledge/distributed/consistency-and-replication.md) · [索引重建、增量追赶与切换：怎样覆盖期间的新增和删除](../knowledge/cache-search/index-rebuild-watermarks-and-cutover.md) · [共识成员变更与分区恢复：谁有资格决定下一条日志](../knowledge/distributed/membership-changes-and-partition-recovery.md) · [CDC：快照、变更位置与重放怎样接成连续的数据流](../knowledge/database/cdc-snapshots-log-positions-and-replay.md)

<a id="distributed.split-brain"></a>

## Split Brain

**ID：** `distributed.split-brain` · **建议优先级：** P1

**别名 / 检索词：** Split Brain、脑裂

**简释：** 多个节点同时认为自己拥有权威。

脑裂指多个节点同时认为自己拥有权威，可能源于分区、错误切换或旧领导者继续执行。恢复通信并不自动修复冲突，需用协议和资源端约束预防。

**例子：** 两个主节点都接受修改后，必须明确冲突处理与业务修复策略。

**深入阅读：** [共识与 Quorum：多数响应为什么还不等于一致决定](../knowledge/distributed/consensus-leaders-and-quorums.md) · [租约与 Fencing：锁过期后怎样拒绝旧执行者](../knowledge/distributed/leases-heartbeats-and-fencing.md)

<a id="distributed.partition"></a>

## Network Partition

**ID：** `distributed.partition` · **建议优先级：** P1

**别名 / 检索词：** Network Partition、网络分区

**简释：** 节点间通信被切断或严重不可达。

网络分区使部分节点之间不能可靠通信，可能是单向、局部或间歇性的。超时只能表明没及时收到响应，不能据此证明远端已停止工作。

**例子：** 请求超时后远端仍可能提交写入，客户端需核对结果而非盲目重做。

**深入阅读：** [一致性与复制：写入成功后为什么仍可能读到旧值](../knowledge/distributed/consistency-and-replication.md) · [共识与 Quorum：多数响应为什么还不等于一致决定](../knowledge/distributed/consensus-leaders-and-quorums.md) · [CAP 与 PACELC：分区和延迟下，一次操作还能承诺什么](../knowledge/distributed/cap-pacelc-and-operation-guarantees.md)

<a id="distributed.2pc"></a>

## Distributed Transaction / 2PC

**ID：** `distributed.2pc` · **建议优先级：** P1

**别名 / 检索词：** Distributed Transaction、2PC、两阶段提交、分布式事务

**简释：** 跨参与者协调提交及其阻塞等成本。

2PC 先准备再由协调者决定提交或回滚，参与者需持久化决议相关状态。经典协议在某些故障下会阻塞，跨参与者锁与恢复增加可用性成本。

**例子：** 参与者已准备后与协调者失联，不能仅凭本地超时就任意提交。

**深入阅读：** [跨服务事务：2PC、Saga 与补偿恢复](../knowledge/distributed/two-phase-commit-sagas-and-recovery.md)

<a id="distributed.saga"></a>

## Saga / Compensation

**ID：** `distributed.saga` · **建议优先级：** P1

**别名 / 检索词：** Saga、Compensation、补偿事务

**简释：** 多步业务通过补偿应对部分成功。

Saga 把长业务拆成本地事务，用后续动作或补偿处理部分成功。补偿是业务操作，未必精确逆转历史，也可能失败并需要人工处理。

**例子：** 机票预订成功但酒店失败时，取消机票可能受手续费与取消时限约束。

**深入阅读：** [跨服务事务：2PC、Saga 与补偿恢复](../knowledge/distributed/two-phase-commit-sagas-and-recovery.md)

<a id="distributed.hashing"></a>

## Consistent Hashing

**ID：** `distributed.hashing` · **建议优先级：** P1

**别名 / 检索词：** Consistent Hashing、一致性哈希

**简释：** 减少节点变化时键重新分布的范围。

一致性哈希将键和节点映射到共同空间，减少成员变化时需迁移的键范围。虚拟节点有助于分布，热点键、容量差异和复制仍需另行处理。

**例子：** 增加缓存节点时只迁移部分键，但单个超热键不会因此自动均摊。

**深入阅读：** [一致性哈希与数据放置：节点变化后哪些键需要搬走](../knowledge/distributed/consistent-hashing-placement-and-rebalancing.md)

<a id="distributed.clocks"></a>

## Logical Clock / Clock Skew

**ID：** `distributed.clocks` · **建议优先级：** P1

**别名 / 检索词：** Logical Clock、Clock Skew、逻辑时钟、时钟偏差

**简释：** 因果顺序表示与物理时钟偏差。

逻辑时钟描述事件顺序或因果关系，物理时钟会有偏差和回拨。Lamport 时间先后不能反向证明因果；墙钟时间不应未经假设就用于跨节点排他判断。

**例子：** 按时间戳比较两个写入前，先明确是否允许时钟偏差导致次序变化。

**深入阅读：** [逻辑时钟与因果关系：编号更大为什么不代表已经看过另一事件](../knowledge/distributed/logical-clocks-causality-and-concurrency.md) · [混合逻辑时钟：时间戳怎样尊重因果，又保留物理时间参照](../knowledge/distributed/hybrid-logical-clocks-and-timestamp-boundaries.md)

<a id="distributed.ids"></a>

## Snowflake ID / ULID

**ID：** `distributed.ids` · **建议优先级：** P1

**别名 / 检索词：** Snowflake ID、ULID、分布式 ID

**简释：** 对照基于节点与序列的Snowflake类ID和基于时间与随机部分的ULID，按各自条件判断唯一性与排序。

Snowflake与ULID是不同结构的对照组，不是同义格式。经典Twitter布局组合毫秒时间、数据中心/工作者身份和序列；ULID使用48位Unix毫秒时间和80位随机部分，单调工厂另有局部状态。节点复用、回拨、重启、随机质量和编码均影响保证，时间顺序不等于全局因果或提交顺序。

**例子：** 同一Snowflake节点身份在同一时间片重启并清零序列可能重复；一个ULID单调工厂的递增也不会自动协调其他进程。

**深入阅读：** [分布式 ID：唯一、可排序与业务只执行一次分别依赖什么](../knowledge/distributed/distributed-identifiers-time-and-uniqueness.md)

<a id="distributed.vector-clocks"></a>

## Vector Clock

**ID：** `distributed.vector-clocks` · **建议优先级：** P1

**别名 / 检索词：** Vector Clock、Vector Clocks、向量时钟

**简释：** 以参与者计数向量表达因果包含，逐维比较区分后继与并发；精确性依赖身份、更新和上下文传播规则。

在固定参与者并完整传播上下文的逐事件模型中，本地事件递增自身维度，接收消息合并逐维最大值并递增本维；一个向量逐维不大于另一个且至少一维更小时，表示因果在先。互不可比较表示因果并发，不能据此替代业务合并、提交确认或新鲜度保证。动态成员和裁剪还需单独协议。

**例子：** (2,0,1) 与 (1,3,1) 分别在不同维度更大，互不可比较；将它们按字典序排好仍不会产生因果关系。

**深入阅读：** [逻辑时钟与因果关系：编号更大为什么不代表已经看过另一事件](../knowledge/distributed/logical-clocks-causality-and-concurrency.md) · [CRDT：怎样合并并发更新，收敛又没有保证什么](../knowledge/distributed/crdts-convergence-and-concurrent-merge-semantics.md)

<a id="distributed.uuid"></a>

## UUIDv4 / UUIDv7

**ID：** `distributed.uuid` · **建议优先级：** P1

**别名 / 检索词：** UUID、UUIDv4、UUIDv7、Universally Unique Identifier

**简释：** RFC9562中的128位标识格式；v4采用122位随机数据，v7组合时间前缀与随机或可选单调构造，保证仍依赖版本和实现。

UUIDv4与UUIDv7是不同版本。v7高48位为Unix毫秒时间，版本与变体占6位，剩余74位可为随机数据，或按规范组合可选子毫秒片段、适当初始化计数器及剩余随机。纯随机尾部不保证同毫秒生成顺序；随机源、fork/恢复状态及碰撞处置需核查，UUID不替代幂等协议或对象授权。

**例子：** 一个v7库在同毫秒随机填充rand_a/rand_b时，后生成值可能更小；不能仅因名称是v7就假定本进程内严格递增。

**深入阅读：** [分布式 ID：唯一、可排序与业务只执行一次分别依赖什么](../knowledge/distributed/distributed-identifiers-time-and-uniqueness.md)

<a id="distributed.membership"></a>

## Membership Reconfiguration

**ID：** `distributed.membership` · **建议优先级：** P1

**别名 / 检索词：** Membership Reconfiguration、Membership Change、成员变更、成员重配置

**简释：** 按协议改变复制组的投票资格与法定集合，保护新旧配置之间的决定关系。

成员重配置改变谁能参与选举或提交，不等于健康检测或键放置。Raft 论文的联合配置同时要求旧、新两侧多数；具体增量路径还约束单次变化、串行化和生效点。Learner 先接收日志而不投票，提升需检查条件；已有多数永久丢失时，不能靠添加节点继续原协议，另建逻辑集群也需隔离旧权威并明确恢复数据边界。

**例子：** 旧配置 ABC 的 AB 多数与新配置 ABCDE 的 CDE 多数不相交；直接让两套名单各自决定会留下冲突窗口。

**深入阅读：** [共识成员变更与分区恢复：谁有资格决定下一条日志](../knowledge/distributed/membership-changes-and-partition-recovery.md)

<a id="distributed.hlc"></a>

## Hybrid Logical Clock

**ID：** `distributed.hlc` · **建议优先级：** P1

**别名 / 检索词：** HLC、Hybrid Logical Clock、Hybrid Logical Clocks、混合逻辑时钟

**简释：** 结合已知物理分量与逻辑计数，让已编码的因果边对应严格递增时间戳。

HLC以(l,c)字典序比较，发送/本地事件及接收事件按协议更新；因果在先推出较小，较小不能反推因果，相等也可能来自不同节点。物理接近性依赖时钟假设，持续时间、全局唯一、提交、完整读取和排他执行需各自协议。

**例子：** A发送(100,0)，B原为(95,0)，在物理读数96接收得到(100,1)；A本地仍为(100,0)、物理读数99，收到(100,2)时得到(100,3)。计数差不是经过毫秒。

**深入阅读：** [混合逻辑时钟：时间戳怎样尊重因果，又保留物理时间参照](../knowledge/distributed/hybrid-logical-clocks-and-timestamp-boundaries.md)

<a id="distributed.crdt"></a>

## Conflict-free Replicated Data Type

**ID：** `distributed.crdt` · **建议优先级：** P1

**别名 / 检索词：** CRDT、CRDTs、Conflict-free Replicated Data Type、Conflict-free Replicated Data Types、无冲突复制数据类型

**简释：** 把允许更新、并发语义与合并规则共同设计，在传播前提成立时使同一对象的副本收敛。

状态型用单调内部状态与join合并，操作型还须满足其可靠交付、顺序和重复处理要求。收敛不等于即时最新、业务约束、持久化或外部动作幂等；添加/删除、元数据清理和身份恢复都属于类型契约。

**例子：** 贡献状态(3,0)与(0,4)逐分量max得到(3,4)，读数7；不是总数取max得到4。PN计数仍可让余额1在两次并发减少后收敛到−1。

**深入阅读：** [CRDT：怎样合并并发更新，收敛又没有保证什么](../knowledge/distributed/crdts-convergence-and-concurrent-merge-semantics.md)

## 资料与延伸

下列资料提供相关机制的进一步说明，并不表示覆盖本页所有术语。各条已关联的专题文章另列具体来源、适用版本与验证边界。

- [Raft：共识与复制日志](https://raft.github.io/)
- [Jepsen：一致性模型](https://jepsen.io/consistency)
- [Gray / Lamport：Consensus on Transaction Commit](https://arxiv.org/pdf/cs/0408036)
- [Microsoft：Saga 分布式事务模式](https://learn.microsoft.com/en-us/azure/architecture/patterns/saga)
- [Microsoft：补偿事务模式](https://learn.microsoft.com/en-us/azure/architecture/patterns/compensating-transaction)
- [Lamport：Time, Clocks, and the Ordering of Events in a Distributed System](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/12/Time-Clocks-and-the-Ordering-of-Events-in-a-Distributed-System.pdf)
- [Mattern：On the Relativistic Structure of Logical Time in Distributed Systems](https://vs.inf.ethz.ch/publ/papers/relativistic_time.pdf)
- [Karger 等：Consistent Hashing and Random Trees](https://people.csail.mit.edu/karger/Papers/web.pdf)
- [Dynamo：Amazon's Highly Available Key-value Store](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf)
- [Apache Cassandra：Dynamo 架构与放置策略](https://cassandra.apache.org/doc/latest/cassandra/architecture/dynamo.html)
- [Gilbert/Lynch：CAP 形式定义、定理与证明（2002，作者副本）](https://www.comp.nus.edu.sg/~gilbert/pubs/BrewersConjecture-SigAct.pdf)
- [Abadi：Consistency Tradeoffs 与 PACELC（2012，作者副本）](https://cs.umd.edu/~abadi/papers/abadi-pacelc.pdf)
- [Herlihy/Wing：线性一致性的历史定义与其他条件比较（1990）](https://www.cs.cmu.edu/~wing/publications/HerlihyWing90.pdf)
- [Attiya：ABD 原作者解释读回写与先新后旧（2010）](https://hagit.net.technion.ac.il/files/2015/09/EATCScolumn.pdf)
- [RFC9562：Universally Unique IDentifiers](https://www.rfc-editor.org/rfc/rfc9562.html)
- [ULID：作者规范](https://github.com/ulid/spec)
- [Twitter Snowflake：snowflake-2010历史IdWorker实现](https://github.com/twitter-archive/snowflake/blob/snowflake-2010/src/main/scala/com/twitter/service/snowflake/IdWorker.scala)
- [PostgreSQL18：Sequence Manipulation Functions](https://www.postgresql.org/docs/18/functions-sequence.html)
- [Python3.13：secrets安全随机源](https://docs.python.org/3.13/library/secrets.html)
- [Ongaro、Ousterhout：Raft Extended Version（2014-05-20）](https://raft.github.io/raft.pdf)
- [etcd-io/raft v3.6.0：配置生效、持久化与节点身份](https://github.com/etcd-io/raft/blob/v3.6.0/README.md)
- [etcd v3.6：Runtime reconfiguration](https://etcd.io/docs/v3.6/op-guide/runtime-configuration/)
- [etcd v3.6：Learner design](https://etcd.io/docs/v3.6/learning/design-learner/)
- [etcd v3.6：Failure modes](https://etcd.io/docs/v3.6/op-guide/failures/)
- [etcd v3.6：API guarantees](https://etcd.io/docs/v3.6/learning/api_guarantees/)
- [etcd v3.6：Disaster recovery](https://etcd.io/docs/v3.6/op-guide/recovery/)
- [Kulkarni等：Logical Physical Clocks 技术报告2014-04](https://cse.buffalo.edu/tech-reports/2014-04.pdf)
- [CockroachDB stable：HLC、时钟偏差与Closed timestamps](https://www.cockroachlabs.com/docs/stable/architecture/transaction-layer.html)
- [Preguiça/Baquero/Shapiro：Conflict-free Replicated Data Types（2018）](https://arxiv.org/pdf/1805.06358)
- [Bieniusa等：An Optimized Conflict-free Replicated Set（2012）](https://arxiv.org/pdf/1210.3368)
- [Akka Distributed Data：类型、持久化与清理边界](https://doc.akka.io/libraries/akka-core/current/typed/distributed-data.html)
- [Jepsen 的线性一致性定义](https://jepsen.io/consistency/models/linearizable)
- [PostgreSQL 18 复制文档](https://www.postgresql.org/docs/18/warm-standby.html)
- [DynamoDB 读取一致性说明](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.ReadConsistency.html)
- [PostgreSQL18 Hot Standby](https://www.postgresql.org/docs/18/hot-standby.html)
- [etcd 3.6 并发 API](https://etcd.io/docs/v3.6/dev-guide/api_concurrency_reference_v3/)
- [Kleppmann 对分布式锁的原始分析](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html)
- [Chubby 原论文](https://storage.googleapis.com/gweb-research2023-media/pubtools/4444.pdf)
- [Redis锁模式说明](https://redis.io/docs/latest/develop/clients/patterns/distributed-locks/)

[返回分类词汇表](index.md) · [完整术语索引](../glossary.md)
