---
id: "kb-systems-races-atomicity"
title: "竞态与原子性：每一步成功，结果为什么仍然错"
kind: "concept"
domain: "systems"
status: "evolving"
summary: "从共享状态、操作交错和业务不变量出发，区分单步原子、流程正确性与事务保证。"
created: "2026-10-19"
updated: "2026-10-26"
last_verified: "2026-10-19"
verification: "source-checked"
prerequisites: ["kb-systems-execution-units"]
related: ["kb-systems-synchronization", "kb-systems-deadlocks-recovery", "kb-database-concurrent-inventory", "kb-database-inventory-lab", "kb-runtime-event-loop", "kb-api-idempotency", "kb-systems-cpu-caches"]
tags: ["concurrency", "atomicity", "invariants"]
---

# 竞态与原子性：每一步成功，结果为什么仍然错

两个请求都检查到有货、都写入成功，为什么总共只剩一件商品却卖出两件？[并发](../../glossary/systems.md#systems.concurrency)正确性需要说明：哪些状态允许共同变化、哪些执行交错必须被阻止，以及失败后留下什么。单条操作成功不能证明整个业务流程正确。

前置知识：[进程、线程与协程](process-thread-coroutine.md)。本文讨论共享状态的推理方法，以 Python 3.13 asyncio 和 PostgreSQL 18 为具体参照；涉及[内存顺序](../../glossary/systems.md#systems.memory-order)时明确限定 Java SE 24。不同语言和数据库的保证不能互相代用。

## 先写不变量，再找竞争窗口

[不变量](../../glossary/systems.md#systems.atomicity)是系统在约定边界上必须保持的条件。单件库存的教学模型可以写成：没有补货或取消时，剩余库存非负，且“剩余库存 + 已预订数量 = 初始库存”。仅检查库存列不为负，仍可能漏掉多创建了一笔预订。

[竞态条件](../../glossary/systems.md#systems.race-deadlock)（race condition）指正确性依赖多个活动的相对执行时序，而程序没有充分约束这些时序。定位时先列出共享状态和所有写入者，再把“读取 → 判断 → 修改 → 对外确认”拆开。并发活动可以来自不同[线程](../../glossary/systems.md#systems.execution-units)、同一[事件循环](../../glossary/runtime.md#runtime.event-loop)中的多个协程、不同服务进程或数据库会话。

| 交错中的缺口 | 教学例子 | 需要保护的关系 |
| --- | --- | --- |
| 检查后状态改变 | 两个请求都看到库存为 1 | 检查与扣减之间不能重复使用同一份库存 |
| 读改写覆盖 | 两个调用各自读取旧计数，再写回旧值加一 | 两次增量都必须反映到最终值 |
| 多对象只改一半 | 转出余额已减少，转入余额未增加 | 账户总量在提交边界保持一致 |
| [重试](../../glossary/api.md#api.retries)被当作新意图 | 超时后再次创建同一订单 | 同一次业务动作只能形成约定的一份结果 |

这些问题可能同时出现，但修正手段不同：串行化一次扣减，不能自动识别重复请求；使用[幂等](../../glossary/api.md#api.idempotency)键，也不能单独证明跨对象总量守恒。

## 单线程也需要分析交错

下列是未执行的 Python 风格伪代码，state 只表示同一事件循环中共享的内存对象，check_request 表示可能真正挂起的外部校验：

```python
async def reserve(state):
    old = state.remaining
    if old < 1:
        return False
    await check_request()  # 真正挂起期间，其他任务可能改变 state
    state.remaining = old - 1
    state.reservations += 1
    return True
```

纸面时序：A 读到 1 后挂起，B 也读到 1 后挂起；A 恢复写 0、预订加一，B 随后也写 0、预订再加一。最终库存未负，但预订为两件。这里无需同时在两个 CPU 上执行。

[asyncio Task 文档](https://docs.python.org/3.13/library/asyncio-task.html)说明事件循环中的协作式调度：任务真正挂起后，其他任务可以推进。上述例子依赖这个挂起点；不能据此声称每个 await 都会让出，也不能把某个无 await 的片段推广为跨线程、跨 [Runtime](../../glossary/runtime.md#runtime.virtual-machine) 的原子保证。

## 原子操作的边界必须点名

“原子”总要对应具体操作与观察范围。一个原子计数器增量，不代表前面的余额检查和后面的预订写入也包含在同一原子动作中。事务的原子提交或回滚，与并发事务允许看见什么，是两种需要分别说明的保证。

| 声明 | 实际还要核对什么 |
| --- | --- |
| 单个[容器](../../glossary/devops.md#devops.containers)方法是线程安全的 | 多次调用组成的“先检查再插入”是否受同一协议保护 |
| 使用了 atomic/[CAS](../../glossary/systems.md#systems.synchronization) | 比较的是哪些状态，失败后是否重读，其他对象是否一起受保护 |
| 放进了[数据库事务](../../glossary/database.md#database.isolation) | 隔离级别、冲突对象和业务条件是否足以保护不变量 |
| 用了进程内锁 | 所有写入是否经过同一把锁，其他实例是否也会写同一数据库 |

CAS（比较并交换）只在观察值仍符合预期时尝试更新；失败通常意味着需要重新读取和判断，而不是继续沿用旧结论。Java 的[原子变量包](https://docs.oracle.com/en/java/javase/24/docs/api/java.base/java/util/concurrent/atomic/package-summary.html)定义了单变量原子更新与内存语义，不能把它扩展成任意多字段业务事务。具体算法还需考虑重试竞争，以及状态曾改变又恢复成同值的 [ABA](../../glossary/systems.md#systems.memory-reclamation) 等问题；本文不展开[无锁算法](../../glossary/systems.md#systems.lock-free-progress)证明。

## 数据竞争、可见性与业务竞态

硬件层继续见[CPU 缓存与局部性](cpu-caches-locality-and-false-sharing.md)。缓存一致性和语言同步分别约束不同问题；两个独立原子计数器也可能因布局产生[伪共享](../../glossary/systems.md#systems.cpu-cache)，性能争用不等于业务竞态已解决。新文为来源核查与纸面推演，没有扩大本文实验结论。

数据竞争（data race）有语言[内存模型](../../glossary/systems.md#systems.memory-order)中的专门定义，不能把它当作所有业务竞态的同义词。以 Java SE 24 为例，对同一变量的冲突访问缺少相应 happens-before 顺序时可能形成数据竞争；这个顺序关系表达语言保证，不等同于日志中哪个时间戳更早。

Java 的 volatile 可参与建立可见性与顺序保证，但 `volatileCount++` 仍是读取、计算、写入的复合过程；需要原子增量时应选择对应原子操作或同步协议。反过来，即使所有内存访问都有同步，业务上把“检查”和“使用”放在不同受保护阶段，也可能留下时序缺口。依据见 [JLS 17 的内存模型](https://docs.oracle.com/javase/specs/jls/se24/html/jls-17.html)；本文不把 Java 规则推广到 C/C++ 或 Python。

## 从状态所有权选择方案

先考虑减少共享可变状态：让单个执行者拥有状态、通过有界[队列](../../glossary/algorithms.md#algorithms.queues)提交命令，或传递不可变快照。这样仍需处理队列容量、取消、执行者退出及外部持久化，但更容易点名谁有权修改状态。

确实需要共享时，选覆盖范围足够的机制。同一事件循环可按约束使用 asyncio.Lock；数据库中的单行库存可用带条件的原子更新，并把相关预订放进同一事务。PostgreSQL 18 Read Committed 下竞争更新的等待与条件重判规则见[隔离级别文档](https://www.postgresql.org/docs/18/transaction-iso.html)，复杂跨行不变量需另外设计。

方案要覆盖所有参与者和失败路径。只给读取加锁、每次请求新建一把锁、或让某条后台写入绕开协议，都可能使保护失效。临界区越大，也越容易增加等待与故障影响；正确性与持锁成本需一起分析。

## 自检与证据边界

自检：若一个方法单独线程安全，连续调用两次是否也安全？单个事件循环中，哪个实际挂起点会使检查失效？新增一个服务实例后，原有锁还保护哪些写入者？

本文依据一手来源核查机制，伪代码与交错表为教学推演，未执行内存、线程或协程竞争测试。[库存并发实验](../database/inventory-concurrency-lab.md)提供 PostgreSQL 两会话上的局部实测，不替代语言内存模型、跨进程锁或分布式正确性的验证。

核查日期：2026-10-19。继续阅读[锁与同步原语](locks-and-synchronization.md)、[死锁与失败恢复](deadlocks-and-recovery.md)、[幂等性](../api/idempotency.md)，分别处理互斥范围、无法推进与重复业务意图。
