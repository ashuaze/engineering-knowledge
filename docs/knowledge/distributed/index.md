<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# 分布式系统

建议优先级：P1。目标：明确故障模型、一致性范围与协调成本。

下方术语用于知识索引。建议从[实际工程问题](../../problems.md)或本页核心问题进入，结合已有正文理解机制、适用边界与相关概念。

## 一个核心问题

租约过期的旧持有者恢复后，如何避免继续写入？

## 已有正文

- [一致性与复制：写入成功后为什么仍可能读到旧值](consistency-and-replication.md)：区分复制进度、单对象读取保证、事务隔离和业务约束，明确结果可见的边界。

## 术语范围

| 术语 | 简释 |
| --- | --- |
| CAP / PACELC | 分区下的取舍及正常情况下延迟和一致性的权衡。 |
| Strong / Eventual Consistency | 不同可见性保证，强一致须进一步说明具体模型。 |
| Linearizability / Serializability | 实时单操作顺序与事务可串行执行的等价性。 |
| Consensus / Raft | 在故障模型下就日志或状态达成一致。 |
| Leader Election / Quorum | 选主与按法定集合达成读写条件。 |
| Heartbeat / Lease / Fencing Token | 存活检测、限时持有与拒绝过期执行者。 |
| Replication Lag | 副本应用变更落后于上游。 |
| Split Brain | 多个节点同时认为自己拥有权威。 |
| Network Partition | 节点间通信被切断或严重不可达。 |
| Distributed Transaction / 2PC | 跨参与者协调提交及其阻塞等成本。 |
| Saga / Compensation | 多步业务通过补偿应对部分成功。 |
| Consistent Hashing | 减少节点变化时键重新分布的范围。 |
| Logical Clock / Clock Skew | 因果顺序表示与物理时钟偏差。 |
| Snowflake ID / ULID | 不同的分布式或可排序标识生成方案。 |

## 练习与验收

选择上面的一个核心问题，先画执行过程或数据边界，再构造一个正常路径和一个失败路径。用原理解释、架构或代码、诊断证据和取舍依据说明保证范围；记录已完成验证与待验证项。

[回到知识地图](../../map.md) · [问题导航](../../problems.md) · [学习路径](../../paths/index.md)
