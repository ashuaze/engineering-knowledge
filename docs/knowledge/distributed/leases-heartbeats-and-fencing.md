---
id: "kb-distributed-leases-fencing"
title: "租约与 Fencing：锁过期后怎样拒绝旧执行者"
kind: "concept"
domain: "distributed"
status: "evolving"
summary: "区分故障怀疑、限时持有与写入代次校验，解释旧进程恢复、迟到请求和权威存储的责任。"
created: "2026-10-20"
updated: "2026-10-27"
last_verified: "2026-10-27"
verification: "source-checked"
prerequisites: ["kb-distributed-consensus-quorum", "kb-systems-races-atomicity"]
related: ["kb-api-idempotency", "kb-ai-workflow-state", "kb-ai-workflow-routing", "kb-messaging-partitions-offsets", "kb-systems-synchronization", "kb-cache-load-coalescing", "kb-distributed-membership-recovery"]
tags: ["lease", "heartbeat", "fencing", "ownership"]
---

# 租约与 Fencing：锁过期后怎样拒绝旧执行者

学习入口：A 的锁已过期，B 已接手，为什么 A 恢复后仍能写坏数据？前置：竞态、权威写入与[共识](../../glossary/distributed.md#distributed.consensus)。锁服务可以改变它记录的持有者，却不能让暂停的[进程](../../glossary/systems.md#systems.execution-units)或已发出的请求消失。防止旧执行者覆盖新状态，需要让实际资源也参与检查执行资格。

## 心跳、租约与隔离承担不同责任

| 机制 | 能提供的依据 | 不能单独证明什么 |
| --- | --- | --- |
| [心跳](../../glossary/distributed.md#distributed.fencing) / [超时](../../glossary/api.md#api.retries)检测 | 最近是否观察到对方响应，可触发故障怀疑 | 对方已经永久停止，或不会再发请求 |
| 租约 Lease | 按约定时间与续约规则授予限时资格 | 持有者的进程、线程和网络包已停止 |
| Fencing / 代次隔离 | 资源拒绝已过时执行代次的动作 | 同代次操作不会重复、业务结果一定正确 |

长暂停、[网络分区](../../glossary/distributed.md#distributed.partition)和[延迟](../../glossary/performance.md#performance.latency-throughput)都可能让存活者暂时没有响应。把超时作为接管条件时，还需明确旧持有者回来后如何处理，而不是把“未收到心跳”解释为“已确认死亡”。

[etcd 3.6 并发 API](https://etcd.io/docs/v3.6/dev-guide/api_concurrency_reference_v3/)的锁所有权与 lease 关联，lease 到期或撤销可释放锁；其所有权 key 可以配合事务保护 etcd 内部更新。这并不表示任意外部数据库、文件服务器或工具自动执行相同检查。

## 一次暂停就能暴露缺口

以下是教学时序，编号只用于解释，没有运行锁服务：

| 顺序 | 事件 |
| --- | --- |
| 1 | A 获得资源 X 的租约，开始准备写入，然后长时间暂停 |
| 2 | 租约失效，B 获得 X 的新资格 |
| 3 | B 更新 X，资源保存新状态 |
| 4 | A 恢复，继续发出此前准备的写请求 |

若资源只信任“调用者说自己拿过锁”，A 仍可能覆盖 B。A 在发请求前检查一次租约也不够：检查之后仍可能暂停，或者请求在网络中迟到。

[Kleppmann 对分布式锁的原始分析](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html)用暂停和延迟说明这一缺口，并提出由资源检查递增的 fencing token。这里借用其机制，不据此评价所有锁产品或假定它们采用相同时间模型。

## 资源必须原子地检查代次并写入

教学设计：可信协调路径为 X 的每次新持有授予严格递增代次。A 持 41，B 持 42；资源为 X 保存已接受的最高代次。处理经过身份与权限校验的请求时：

```text
在同一个权威写入边界中：
  校验代次确由可信授权路径签发、适用于该资源
  若请求代次小于已接受最高代次，拒绝
  否则更新最高代次，并执行受保护的业务修改
```

资源已接受 42 后，迟到的 41 会被拒绝。[Chubby 原论文](https://storage.googleapis.com/gweb-research2023-media/pubtools/4444.pdf)描述了把锁取得计数随写 [RPC](../../glossary/api.md#api.styles) 传给文件服务器，由服务器拒绝较旧计数的做法。实际协议、范围与保存要求要按系统实现核对；上面的流程不是完整鉴权或事务实现。

如果把“先查最高代次”和“稍后修改业务”拆开，两个请求仍可交错。所有受保护的写入口都需要共同执行该约束；旁路脚本、旧接口或另一个没有隔离检查的存储会破坏整体结论。

## 隔离生效点不能说得过早

仅按资源已见最高代次拒绝旧请求时，资源尚未见过 42，迟到的 41 仍可能被接受。因此不能说“B 一拿到租约，A 立即在所有资源失效”。

若要求从接管完成起旧代次就不可写，应把在资源建立新代次屏障纳入接管完成条件，或让资源在同一有效写入边界检查当前权威资格。跨多个资源的屏障完成、部分失败和恢复还需单独设计；额外查一次远程租约、再无条件写入，不会自动消除检查与使用之间的窗口。

即便资源已接受 42，这个较新代次也不能撤销先前已提交的 41 效果。需要回滚、补偿或对账的业务，仍须定义自己的处理方式。

## 代次、权限、顺序和幂等各有范围

| 问题 | 还需要什么 |
| --- | --- |
| 客户端伪造一个极大代次 | 可信签发与[授权](../../glossary/security.md#security.identity)，不能接受任意用户填的整数 |
| 同一代次重复发送扣款 | 稳定业务动作标识与[幂等性](../api/idempotency.md)，代次相同不代表新动作 |
| 同一持有者的两个更新乱序 | 业务版本、序列或事务约束，单个代次无法排列所有更新 |
| 协调器恢复后计数倒退或复用 | 持久化、恢复与作用域协议，必要时建立可比较的新纪元 |
| 不同资源使用不同计数器 | 分别按相同资源范围比较，不能随意比较无关数字 |

随机唯一字符串有助于识别某次持有，但不自动形成新旧顺序；进程本地计数器也不自动获得跨故障的严格递增保证。资源保存的最高代次需要相应耐久与恢复策略，否则回到旧备份可能重新接纳旧执行者。

Fencing 是安全约束，失去权威服务或资源不能完成检查时，可能需要拒绝或等待；不能为提高[可用性](../../glossary/reliability.md#reliability.availability)而悄悄绕过检查，再维持相同保证。

## 时间假设与接管成本要显式说明

### 缓存租约先区分减少重复工作与保护正确性

为了减少重复回源而使用[分布式锁](../../glossary/cache-search.md#cache-search.lock-lease)，需要判断偶尔多执行一次的后果；如果重复会破坏数据或产生不可接受的付款，就不能仅靠“通常不会同时拿到”作为正确性保证。区分效率与正确性目的，也是Kleppmann分析的起点。

释放锁时的持有者标识与fencing代次有不同职责。[Redis锁模式说明](https://redis.io/docs/latest/develop/clients/patterns/distributed-locks/)要求在同一条件操作中核对本次随机持有标识再删除，避免旧持有者误删新锁；这个随机标识本身不提供严格新旧顺序，也不自动阻止旧执行者修改外部资源。

对于缓存回填，还需检查加载时的业务版本、失效代次或资源资格是否仍有效。租约过期后，旧回源结果不应仅因计算完成就无条件覆盖新值；具体条件写入、删除与恢复见[缓存加载合并](../cache-search/cache-load-coalescing-and-stampedes.md)。

这些是边界分析，不是Redlock完整算法或安全性证明；Redis命令可用性、时钟假设、故障模型和持久化要求仍需按具体版本核对。本文没有安装锁客户端或执行缓存竞争。

租约应定义由谁计时、如何续约、续约失败何时停止新工作，以及持有者如何处理不确定状态。系统时钟、暂停和消息延迟的假设影响可用性与某些租约算法的安全范围；不应仅靠把 TTL 加长就声称解决旧写入。

代次检查把部分安全责任放到资源端，也增加保存字段、事务协调、恢复兼容与排障成本。资源不支持相应条件写入时，可以评估受控代理或缩小业务边界，但代理仍需真正控制所有副作用路径，不能只加一层转发就宣布完成隔离。

共享加载中的旧持有者见[缓存加载合并与惊群控制](../cache-search/cache-load-coalescing-and-stampedes.md)，旧集群与恢复后外部副作用见[共识成员变更与分区恢复](membership-changes-and-partition-recovery.md)。租约、配置或集群身份变化，仍需资源端真正拒绝过时代次。

## 自检与核查范围

1. 心跳缺失、租约到期和资源端fencing分别证明什么？
2. B得到42但资源从未见过42，能否保证41已被拒绝？
3. 为什么允许同一代次写入，仍需要独立业务幂等键与顺序约束？
4. 条件释放中的随机持有标识与严格递增代次有何区别？
5. 缓存回填与锁/业务存储恢复时，为什么不能只核对曾拿到锁？

核查日期：2026-10-27。重新核查etcd3.6锁/lease、Kleppmann分析、Chubby锁计数相关段落，增补Redis持有标识条件释放与缓存用途边界；未声称阅读全文或证明任意锁产品安全。时序、原子检查与接管条件为教学综合。未部署锁集群、注入进程暂停或验证不同资源的隔离效果。可对照[编排状态与检查点](../ai/workflow-state-and-checkpoints.md)理解旧工作者恢复，也可继续读[分区、消费组与偏移](../messaging/partitions-consumer-groups-and-offsets.md)中的分工变化。
