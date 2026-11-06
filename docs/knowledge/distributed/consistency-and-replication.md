---
id: "kb-distributed-consistency"
title: "一致性与复制：写入成功后为什么仍可能读到旧值"
kind: "concept"
domain: "distributed"
status: "evolving"
summary: "区分复制进度、单对象读取保证、事务隔离和业务约束，明确结果可见的边界。"
created: "2026-10-16"
updated: "2026-10-27"
last_verified: "2026-10-27"
verification: "source-checked"
prerequisites: []
related: ["kb-cache-search-cache-aside", "kb-api-idempotency", "kb-messaging-outbox", "kb-networking-https-request", "kb-database-wal-recovery", "kb-database-backups-pitr", "kb-distributed-consensus-quorum", "kb-distributed-leases-fencing", "kb-distributed-transactions-sagas", "kb-distributed-logical-clocks", "kb-distributed-cap-pacelc", "kb-distributed-hlc", "kb-distributed-crdt", "kb-database-cdc"]
tags: ["consistency", "replication", "state"]
---

# 一致性与复制：写入成功后为什么仍可能读到旧值

学习入口：刚修改资料就刷新页面，为什么内容变回旧版本？前置知识：请求响应、读写与副本。本文先建立保证范围的共同语言；产品名中的“强一致”需回到具体接口与配置解释。

## Definition：定义与问题

复制把状态传播到多个位置，用于容错、读取或地域部署。一致性模型描述[并发](../../glossary/systems.md#systems.concurrency)与分布式读写允许出现怎样的观察结果。副本数量、持久化程度和读取新鲜度分别需要说明。

“写入成功”要问：哪个节点确认，确认到接收、持久化还是应用完成？“后续读取”要问：从哪里读，读取的是主记录、索引、缓存还是投影？不同路径不一定共享同一个保证。

## Principles：工作机制与核心原理

| 概念 | 核心含义 | 容易混淆之处 |
| --- | --- | --- |
| [线性一致性](../../glossary/distributed.md#distributed.linear-serial) | 操作看起来在调用与返回之间某一瞬间完成，并尊重不重叠操作的实时先后 | 要明确对象与接口范围，不代表自动拥有任意多对象事务 |
| [最终一致性](../../glossary/distributed.md#distributed.consistency) | 在更新停止、传播与冲突处理等条件满足后，副本最终趋于一致 | 本身不规定多久、期间能看到什么版本 |
| 读己之写 | 某主体后续读取能看到自己的已完成写入或更晚状态 | 不一定保证其他主体相同时间的读取 |
| 事务可串行化 | 已提交事务的结果可解释为某种串行执行 | 单凭这一术语不能推导真实时间顺序 |

[Jepsen 的线性一致性定义](https://jepsen.io/consistency/models/linearizable)明确了实时顺序与对象范围。本文以它作为一种精确的强保证例子，而不把所有产品的“强一致”都视为同一个模型。

异步复制可能在确认写入后才使新值对其他读取位置可见。[PostgreSQL 18 复制文档](https://www.postgresql.org/docs/18/warm-standby.html)区分异步传播和等待副本不同阶段的同步设置；收到日志与已经回放到可查询状态不是同一个阶段。

接口保证也可能不同。[DynamoDB 读取一致性说明](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.ReadConsistency.html)区分表、索引等读取路径可选的语义；不能把某条接口的保证直接扩展到缓存或所有索引。

## Trade-offs：优势、限制与适用边界

### 读副本要区分接收、落盘、回放与查询快照

[只读副本](../../glossary/database.md#database.replication)分担查询，但复制链路有多个进度：主端提交、备端接收、备端写盘、回放和查询所用快照。收到日志或确认备端耐久，不自动表示当前查询已看见更新。

[PostgreSQL18 Hot Standby](https://www.postgresql.org/docs/18/hot-standby.html)说明，事务提交记录回放后，变化对随后取得的新快照可见；已经建立的旧快照仍按[隔离级别](../../glossary/database.md#database.isolation)工作。例如READ COMMITTED按语句取快照，REPEATABLE READ可在事务内沿用已有快照，具体支持按版本核对。不能仅凭“回放追平”推出一个先前开始的长事务立即换到新状态。

同步确认还要看对象和阶段。PostgreSQL18的 `remote_apply` 等待当前同步备端报告回放，具体参与者由相应配置决定；不涵盖任意异步副本、缓存或查询投影。这里没有提供完整复制配置，也不把同名选项推广到其他数据库。

### 副本查询、主端切换与历史恢复分开判断

读写分离需要按操作选择路径：允许旧值的展示可使用满足相应新鲜度条件的副本，权限撤销和资金决策则要明确权威执行边界。等待满足进度后，还应在正确的查询/快照时点读取；等待超时不撤销原写入。

备端回放也可能与长期查询冲突，系统可能按配置[延迟](../../glossary/performance.md#performance.latency-throughput)回放或取消查询；把更多读取导向备端并非没有成本。副本存在不保证自动安全切主，仍需确认原主隔离、选定数据状态、客户端连接和剩余容量。

复制会传播已接受的修改，误删也可能传播，不能代替独立历史备份。上述阶段、快照和恢复边界于2026-10-27重新核查；没有部署复制、切主或执行查询冲突实验。

等待更多确认或应用进度，会增加协调与等待成本；较弱读取可能更容易利用副本，但应用必须接受或处理旧数据。[网络分区](../../glossary/distributed.md#distributed.partition)时，要保持线性一致性，就可能无法让一部分操作成功完成；不能同时无条件承诺所有位置持续成功和同一最新状态。

资料展示、统计视图、[授权](../../glossary/security.md#security.identity)撤销和资金判断的需求不同。可以按操作选择保证：例如允许报表稍后更新，但权限决策需要明确撤销何时生效。不能只给整套系统贴一个一致性标签。

## Implementation：代码或架构实现

说明性读写流程如下，不代表某个数据库的通用 API：

```text
写路径：校验与授权 → 写入权威节点 → 按约定确认 → 返回结果/系统支持的提交令牌
读路径：判断需要的读取保证 → 选择满足保证的位置
        → 必要时等待目标应用到指定提交位置，或在预算内改走可满足保证的路径
```

如果使用提交位置或版本令牌，必须由底层系统定义比较和传播语义，不能直接比较不同对象各自独立的版本号。读己之写可采用系统支持的会话机制等方案，但不因此获得全局线性一致性。

复制、[缓存失效](../../glossary/cache-search.md#cache-search.invalidation)、查询索引和事件投影分别记录进度。遇到[超时](../../glossary/api.md#api.retries)先保留“结果未知”，按业务标识查询；不能把一致性等待超时自动当作原写入回滚。

## Failure Modes：常见错误与故障模式

- **把持久化确认等同于所有读取点立即可见**：检查确认阶段和实际读路径。
- **把“最终”理解为固定几秒**：没有单独的[延迟](../../glossary/performance.md#performance.latency-throughput)承诺和恢复条件，就不能据此设定业务期限。
- **读主节点就宣称所有操作线性一致**：还要检查接口、事务、并发和[故障切换](../../glossary/reliability.md#reliability.dr)语义。
- **用读取旧副本做不可重复的业务判断**：需要把决策移到有对应保证的权威执行边界。
- **把复制故障当作普通成功、无限等待或盲目重放**：明确拒绝、降级、查询和恢复策略。

## Practice：工程案例、测试与验证

纸面历史：一个寄存器初始为 v0，唯一一次更新写 v1 且已返回成功，没有其他写入。随后才开始的读取却返回 v0。在同一对象与接口承诺线性一致的前提下，这不符合实时顺序；若走的是允许陈旧读取的副本，则需要按该接口语义解释。

若读取与写入在时间上重叠，不能只按哪条日志先打印就认定结果违规。概念练习应记录每次调用的开始、返回、读取位置、结果和保证范围，再寻找与模型兼容的顺序。

本文为机制解释与教学推演，未运行复制集群或一致性历史检查器。验收：能分别写出单对象、事务、缓存和索引的保证，并指出一个跨越保证范围的错误推论。

继续读[共识与 Quorum](consensus-leaders-and-quorums.md)，区分多数相交和完整提交规则；再读[租约与 Fencing](leases-heartbeats-and-fencing.md)，理解[选主](../../glossary/distributed.md#distributed.leadership)为何不自动阻止旧执行者对外部资源写入。两篇均为概念核查与纸面推演，没有扩大本文集群验证范围。

复制之外，跨服务怎样处理部分提交和恢复决定，见[2PC、Saga 与补偿恢复](two-phase-commit-sagas-and-recovery.md)；补偿是新的业务动作，不自动恢复全局隔离。

事件的排序与因果关系见[逻辑时钟与因果顺序](logical-clocks-causality-and-concurrency.md)，标量时间戳先后不自动证明事件间的因果。

断联时形式可用性与线性一致性的边界，以及正常复制中延迟与一致性的取舍，继续见[CAP 与 PACELC](cap-pacelc-and-operation-guarantees.md)；应按操作和读写配置说明保证。

时间戳与真实读取的边界见[HLC](hybrid-logical-clocks-and-timestamp-boundaries.md)，并发贡献与删除怎样收敛见[CRDT](crdts-convergence-and-concurrent-merge-semantics.md)，来源变化怎样接续与恢复见[CDC](../database/cdc-snapshots-log-positions-and-replay.md)。这些机制分别服务排序、合并和传播，不能独自替代业务提交与约束。

## Related Concepts：关联概念

- [WAL 与崩溃恢复](../database/wal-and-crash-recovery.md)和[备份与时间点恢复](../database/backups-and-point-in-time-recovery.md)：副本可见、本机耐久与历史恢复需要分别验证。

- [Cache-Aside 与失效](../cache-search/cache-aside-and-invalidation.md)：缓存回填会增加另一条状态传播路径。
- [幂等性](../api/idempotency.md)：副作用已发生而结果未知时，重复调用需要稳定业务标识。
- [Transactional Outbox](../messaging/transactional-outbox.md)：同库提交后，消息投递与消费可见性仍有单独边界。
- [HTTPS 请求链路](../networking/https-request-lifecycle.md)：调用方观察与服务端内部完成是不同事实。

## 来源与核查

核查日期：2026-10-27。重新核查Jepsen实时顺序、PostgreSQL18复制/Hot Standby阶段及DynamoDB读取接口范围，增补读副本快照、冲突和切主/备份边界。最终一致、读己之写与可串行化用于概念区分；具体系统需核对其正式承诺。流程和历史为教学设计，无集群实测。

## 读副本与一致性自检

1. 主端确认、备端接收/写盘/回放与查询快照分别说明什么？
2. `remote_apply`为什么不能保证任意副本和旧查询快照立即看到新值？
3. 线性一致、读己之写与多对象事务为什么不能互相替代？
4. 副本已经回放追平，为什么仍需核对切主隔离和读取路径？
5. 为什么复制不能替代历史备份，等待超时也不证明写入回滚？

- [Jepsen：Linearizability](https://jepsen.io/consistency/models/linearizable)
- [PostgreSQL 18：Log-Shipping Standby Servers](https://www.postgresql.org/docs/18/warm-standby.html)
- [AWS：DynamoDB read consistency](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.ReadConsistency.html)
