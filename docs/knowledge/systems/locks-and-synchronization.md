---
id: "kb-systems-synchronization"
title: "锁与同步原语：保护范围比加锁动作更重要"
kind: "concept"
domain: "systems"
status: "evolving"
summary: "区分互斥、计数准入与条件等待，解释线程锁、协程锁和数据库锁各自的保护范围。"
created: "2026-10-19"
updated: "2026-10-26"
last_verified: "2026-10-19"
verification: "source-checked"
prerequisites: ["kb-systems-races-atomicity"]
related: ["kb-systems-execution-units", "kb-systems-races-atomicity", "kb-systems-deadlocks-recovery", "kb-database-concurrent-inventory", "kb-database-inventory-lab", "kb-performance-latency-queues", "kb-performance-backpressure", "kb-systems-memory-order", "kb-systems-lock-free-progress"]
tags: ["locks", "synchronization", "concurrency"]
---

# 锁与同步原语：保护范围比加锁动作更重要

移除 [mutex](../../glossary/systems.md#systems.synchronization) 以后，正确性、整体完成与单次饥饿仍需分别证明，继续见[无锁算法与进度保证](lock-free-algorithms-linearization-and-progress.md)。该专题为来源核查和教学时序，不构成本篇锁实现或无锁替换的性能对照。

代码已经加锁，为什么多实例部署后仍然超卖？锁只能协调实际参与同一协议的执行者。先回答“保护什么状态、谁会修改、通过哪个共享对象协调”，再选择 API。

前置知识：[竞态与原子性](races-and-atomicity.md)。本文以 Python 3.13 threading/asyncio 为内存同步参照，以 PostgreSQL 18 为数据库锁参照；不同[运行时](../../glossary/runtime.md#runtime.virtual-machine)的公平性、所有权与失败语义需分别核查。

## 三种问题需要不同原语

| 原语 | 主要表达 | 不能由名称直接推导 |
| --- | --- | --- |
| [互斥锁](../../glossary/systems.md#systems.synchronization) Mutex / Lock | 同一时刻只允许一个参与者进入受保护区域 | 自动回滚修改、跨实例互斥、任意公平调度 |
| 信号量 Semaphore | 最多允许约定数量的参与者同时进入 | 每个参与者修改共享对象都安全、等待[队列](../../glossary/algorithms.md#algorithms.queues)有界 |
| 条件变量 Condition | 等某个共享状态谓词成立，再继续推进 | 一次通知保证条件仍成立，或通知会替调用方转移锁 |

例如最多 10 个请求同时访问下游，可以用信号量表达准入数量；若这些请求还要修改同一内存账本，仍需另行保护账本。允许 10 个进入者的信号量不提供单个修改者的互斥。Python 原语定义见 [threading 文档](https://docs.python.org/3.13/library/threading.html)。

读写锁进一步区分读者和写者；“读”必须确实不修改需要保护的状态。读多也不自动意味着它更快，公平性、升级和写者饥饿都取决于实现。本文不提供自制读写锁或性能结论。

## 保护范围要覆盖所有写入者

| 所选机制 | 本文所指协调范围 | 常见缺口 |
| --- | --- | --- |
| Python threading.Lock | 同一[进程](../../glossary/systems.md#systems.execution-units)中共享该锁对象的线程 | 另一个进程拥有另一把锁，不能据此保护共同数据库 |
| Python asyncio.Lock | 同一[事件循环](../../glossary/runtime.md#runtime.event-loop)中遵守该锁的任务 | 它不是线程安全原语；不能代替线程或多实例同步 |
| PostgreSQL 行锁 | 同一数据库中对相关行进行冲突操作的事务 | 普通快照读取不等于预留库存；外部服务动作不在事务锁内 |
| 独立协调服务的[租约](../../glossary/distributed.md#distributed.fencing) | 取决于租约和资源端协议 | 旧持有者失去租约后仍可能继续操作；还需资源端约束 |

asyncio 的边界依据[官方同步原语说明](https://docs.python.org/3.13/library/asyncio-sync.html)。数据库锁的冲突关系依据 [PostgreSQL 显式锁文档](https://www.postgresql.org/docs/18/explicit-locking.html)。最后一行是后续分布式协议的设计提醒，不是本文已经实现的方案。

同一资源必须映射到约定的锁。若每次请求都创建新锁，或者一个调用按用户 id 加锁、另一个按订单 id 加锁，两者可能没有协调同一份状态。设计按键加锁时，还需管理锁对象生命周期，避免清理后产生两把同时使用的“同键锁”。

## 临界区围绕不变量组织

临界区是受同步协议保护的代码或状态转换范围。它应覆盖依赖同一旧状态的检查与修改，同时尽量避免无关耗时。下例是未执行的 Python 风格伪代码，限定所有访问都来自同一事件循环，lock 是参与者共享的 asyncio.Lock：

```python
async def reserve_local(state, lock):
    async with lock:
        if state.remaining < 1:
            return False
        state.remaining -= 1
        state.reservations += 1
        return True
```

它演示局部状态转换的互斥范围，没有磁盘持久性、事务回滚或多实例保证。异常发生在两次修改之间时，离开上下文会释放锁，却不会自动撤销第一项修改；真实对象的转换和错误处理需要保证不留下半成品。

需要外部校验时，可先完成不依赖受保护旧状态的工作，再在锁内重新检查条件。若校验结果绑定某个版本，则在提交时核对版本；不能把耗时操作简单移到锁外，却继续沿用它之前的库存判断。持锁等待远程调用也会扩大竞争，并可能与回调形成依赖环。

## 条件等待必须重新检查状态

条件变量关联一把锁和一个状态谓词。例如消费者等待“队列非空”：在锁内检查，若不成立就等待；等待过程中释放关联锁，醒来后重新获得锁，再检查谓词。通知之后可能已有另一个消费者拿走元素，也可能出现虚假唤醒，因此不能把一次唤醒当成取到资源的凭证。[Java Condition 文档](https://docs.oracle.com/en/java/javase/24/docs/api/java.base/java/util/concurrent/locks/Condition.html)明确说明了等待与虚假唤醒。

以下是未执行的协议伪代码，不绑定具体语言 API：

```text
获得条件变量关联的锁
while 队列为空:
    等待条件变量（释放关联锁；返回前重新获得）
从队列取出元素
释放锁
```

生产者也应在同一状态协议下修改队列并通知。Condition 关注“状态可能改变”，不是一条持久消息；需要消息存储、消费确认和重放时，应选相应队列或消息协议。

## 释放资源、取消与容量

获得与释放应形成配对；在 API 支持时使用上下文管理或 finally，并把异常和取消纳入路径。释放锁只解除互斥，不恢复数据；归还信号量只恢复名额，不代表外部请求已取消。asyncio 取消清理的边界见 [Task 文档](https://docs.python.org/3.13/library/asyncio-task.html)。

使用信号量限制执行中的请求后，外部仍可能不断创建等待任务。要保护整体容量，还需限制入队数量、等待期限和拒绝策略，具体见[背压与有界队列](../performance/backpressure-and-bounded-queues.md)，结合[延迟与排队](../performance/latency-throughput-and-queues.md)分析。锁粒度细可能增加协议复杂度，锁粒度粗可能延长等待；先保证范围正确，再用目标负载观测成本。

故障排查应记录锁标识、持有者、等待者、等待的资源、事务或任务状态，以及持锁期间正在做什么。看到 CPU 不高但请求缓慢时，不要直接增加[并发](../../glossary/systems.md#systems.concurrency)，先检查是否所有工作都排在同一[热点](../../glossary/performance.md#performance.contention)上。

原子读写与跨对象发布还需要语言[内存模型](../../glossary/systems.md#systems.memory-order)的条件，见[内存顺序与原子操作](memory-order-atomics-and-publication.md)；不能从单个原子标志直接推出其他数据已可安全读取。

## 自检与证据边界

自检：服务扩成三个进程后，进程内锁还保护谁？Semaphore(10) 是否允许多个任务同时修改同一对象？条件变量被通知后，为何仍要循环检查？finally 释放锁后，半途修改的数据会自动恢复吗？

本文是来源核查与协议推演，未执行线程锁、协程锁、读写锁、分布式租约或吞吐实验。[库存并发实验](../database/inventory-concurrency-lab.md)仅给出 PostgreSQL 18 两会话中的锁等待和事务结果。继续阅读[死锁与失败恢复](deadlocks-and-recovery.md)，区分互斥正确与系统能够持续推进。

核查日期：2026-10-19。版本与来源分别在相关段落列出；不把某个原语的公平性或释放规则推广为所有语言的约定。
