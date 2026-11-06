---
id: "kb-systems-deadlocks-recovery"
title: "死锁与失败恢复：等待为什么无法自行结束"
kind: "concept"
domain: "systems"
status: "evolving"
summary: "用等待关系区分死锁、竞争与超时，说明锁顺序、数据库回滚和有边界重试的分工。"
created: "2026-10-19"
updated: "2026-10-20"
last_verified: "2026-10-19"
verification: "source-checked"
prerequisites: ["kb-systems-synchronization"]
related: ["kb-systems-races-atomicity", "kb-systems-synchronization", "kb-database-inventory-lab", "kb-database-isolation-mvcc", "kb-reliability-retry-budgets", "kb-api-idempotency"]
tags: ["deadlocks", "recovery", "transactions"]
---

# 死锁与失败恢复：等待为什么无法自行结束

请求都在等锁，增加[线程](../../glossary/systems.md#systems.execution-units)仍没有进展，究竟是[热点](../../glossary/performance.md#performance.contention)[排队](../../glossary/performance.md#performance.queueing)还是[死锁](../../glossary/systems.md#systems.race-deadlock)？关键是查明谁持有资源、谁在等待谁，以及持有者能否在不依赖等待者的情况下继续完成。

前置知识：[锁与同步原语](locks-and-synchronization.md)。本文先用互斥资源模型解释等待环，再以 PostgreSQL 18 的事务错误说明恢复；不假定语言锁都自带死锁检测，也不实现通用分布式死锁检测。

## 从等待关系识别死锁

教学设定：资源 X、Y 各只允许一个持有者，必须由持有者释放，没有替代资源或自动抢占。

| 步骤 | 任务 A | 任务 B |
| --- | --- | --- |
| 1 | 获得 X | 获得 Y |
| 2 | 持有 X，等待 Y | 持有 Y，等待 X |
| 3 | 需要 B 先释放才能继续 | 需要 A 先释放才能继续 |

关系是 A 等 B、B 等 A。若没有取消、[超时](../../glossary/api.md#api.retries)或外部干预，双方都无法走到释放点。在上述每种资源单实例的模型中，等待环说明死锁；资源有多个可替代实例时，仅看一个环不足以直接判定。

PostgreSQL 的[显式锁与死锁说明](https://www.postgresql.org/docs/18/explicit-locking.html)给出数据库里的对应机制：锁竞争可能形成死锁，数据库通过中止其中一个事务解除它。牺牲哪个事务不应成为业务依赖；普通线程锁也不能据此推导有相同检测能力。

## 不要把所有长等待都叫死锁

| 现象 | 需要查的证据 | 处理方向 |
| --- | --- | --- |
| 锁竞争 | 等待者排在仍能完成的持有者后面 | 缩短持锁、减少热点、限制竞争 |
| 死锁 | 满足具体资源模型的[循环依赖](../../glossary/runtime.md#runtime.modules) | 打破依赖、回滚参与者、修订获取顺序 |
| 饥饿 | 系统在推进，但某个参与者长期得不到机会 | 核对公平性、优先级与流量 |
| 活锁 | 参与者不断重试或退让，却没有有效完成 | 改变冲突协议与退避，限制重试 |
| 超时 | 等待或执行超过配置预算 | 判断当时状态与错误类别；超时本身不证明有环 |

某个事务持锁后等待远程服务，只要依赖方仍可能返回，就不能仅凭等待时间长判为数据库死锁。如果依赖跨数据库、应用回调和[连接池](../../glossary/api.md#api.pool)，数据库也未必看得到完整等待关系。应为每条依赖寻找对应证据。

## 一致锁顺序如何减少等待环

对确实需要一起获取的资源规定稳定顺序，例如所有转账都先锁 id 较小的账户，再锁较大的账户，避免不同入口反向获取。该规则必须覆盖后台任务、异常路径和隐式访问；只有部分调用遵守时不能据此保证无环。

顺序键必须稳定且能确定次序；如果业务两次访问其实映射到同一资源，也应处理重入或重复获取。数据库还可能因索引、[外键](../../glossary/database.md#database.constraints)和其他语句产生隐式锁，固定应用层顺序不能证明任意 SQL 都不会死锁。

还可减少嵌套资源、缩短事务、避免持锁调用未知回调，或者以单个所有者串行处理局部状态。每种做法都要说明吞吐、隔离和失败恢复成本。“所有地方放一把全局锁”也可能造成严[重排](../../glossary/cache-search.md#cache-search.hybrid)队，且无法自动覆盖进程外资源。

## 超时是预算，不是死锁检测证明

PostgreSQL 18 的 lock_timeout 限制等待获取锁的时间，statement_timeout 限制语句执行时间；两者不能互相当成同一指标。[连接默认配置文档](https://www.postgresql.org/docs/18/runtime-config-client.html)给出了具体范围。本文实验把检测和等待参数调短，只用于受控复现，不能直接复制为生产默认值。

结合[官方错误码](https://www.postgresql.org/docs/18/errcodes-appendix.html)区分处理分支：

| SQLSTATE | 本文关注的含义 | 不应直接推导 |
| --- | --- | --- |
| 40P01 | 数据库检测到死锁 | 总是同一个会话被中止 |
| 40001 | [序列化](../../glossary/runtime.md#runtime.serialization)失败 | 只重发最后一条写语句就足够 |
| 55P03 | 无法获得锁；本文实测为 lock_timeout | 任意出现该码都说明形成死锁 |
| 23505 | 唯一性冲突 | 一律属于瞬时竞争、应无限重试 |

若连接断开或客户端超时发生在提交附近，调用方还可能不知道事务是否已提交。这个“结果未知”问题与数据库明确报告冲突失败不同；需要按稳定业务标识查询与核对，见[幂等性](../api/idempotency.md)。

## 恢复要覆盖整个业务判断

遇到可重试的数据库[并发](../../glossary/systems.md#systems.concurrency)失败时，先清理失败事务，再在预算允许时开启新事务，重新读取并执行完整业务判断。PostgreSQL 的[序列化失败处理文档](https://www.postgresql.org/docs/18/mvcc-serialization-failure-handling.html)明确要求对序列化失败重试整个事务，死锁错误也可能适合重试；唯一性冲突则需结合业务来源区分。

未执行的协议伪代码：

```text
在次数与总期限预算内:
    开启新事务
    重新读取、判断、写入并提交
    成功则返回
    若收到允许重试的明确错误:
        回滚并清理当前事务
        根据剩余预算退避，再重新开始
    否则传播错误或进入结果核对流程
```

退避时不要继续占用失败事务与其资源；还需按连接库规则归还或重置连接。外部扣款、邮件或消息不会因为数据库回滚而自动撤销，不能在每次尝试中无条件重复发送。组合[重试预算](../reliability/timeouts-and-retry-budgets.md)与[幂等](../../glossary/api.md#api.idempotency)协议，区分“允许再试”和“可以安全再做一次”。

## 用什么证据验收

诊断记录至少包括事务或任务标识、持有资源、等待资源、错误码、事务边界与最终业务状态。数据库中的 pg_blocking_pids 可以帮助观察等待者的[阻塞](../../glossary/systems.md#systems.blocking)来源；SQLSTATE 与错误 DETAIL 则支持区分死锁和锁等待超时。没有记录到等待环，不能只凭一张慢查询图认定死锁。

[库存并发实验](../database/inventory-concurrency-lab.md)在同一 PostgreSQL 18.0 环境分别复现死锁与锁超时，保存两个会话和观察会话的原始输出。本实验验证具体时序与错误分支，没有实现自动重试、跨库依赖检测或生产锁参数调优。

自检：A 等 B，而 B 仍在执行可完成的工作，是否一定死锁？固定锁顺序需要哪些参与者共同遵守？40P01 后重新发最后一条 UPDATE 为什么可能沿用已经失效的业务判断？

本文核查日期：2026-10-19。等待表与恢复伪代码为教学推演；来源核查、数据库实测和未实现的重试策略分别记录。
