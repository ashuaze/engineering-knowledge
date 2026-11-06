---
id: "kb-systems-context-switch"
title: "上下文切换与调度等待：线程已被唤醒，为什么仍没有运行"
kind: "concept"
domain: "systems"
status: "evolving"
summary: "区分运行、就绪与睡眠，解释任务切换、权限入口、CPU 迁移和协程切换的范围，以及切换次数与调度延迟的不同证据。"
created: "2026-10-26"
updated: "2026-10-26"
last_verified: "2026-10-26"
verification: "source-checked"
prerequisites: ["kb-systems-execution-units", "kb-systems-syscalls"]
related: ["kb-performance-cpu-metrics", "kb-performance-profiling", "kb-systems-cpu-caches", "kb-runtime-async-blocking", "kb-systems-lock-free-progress"]
tags: ["context-switch", "scheduler", "linux", "latency"]
---

# 上下文切换与调度等待：线程已被唤醒，为什么仍没有运行

学习入口：I/O 已完成，等待[线程](../../glossary/systems.md#systems.execution-units)也已唤醒，为什么请求还在等待？前置：[执行单元](process-thread-coroutine.md)、[系统调用](syscalls-privilege-and-return-contracts.md)。本文以 Linux 用户线程与当日内核/工具文档为范围，说明调度状态和观测口径；时间线及成本均为教学推演，没有采集真实调度记录。

## 就绪表示可以参与选择，运行表示已经获得 CPU

| 教学状态 | 线程此刻在做什么 | 下一步由什么决定 |
| --- | --- | --- |
| 运行 | 正在某个 CPU 上执行 | 继续执行、[阻塞](../../glossary/systems.md#systems.blocking)、被抢占或退出 |
| 就绪 | 可以执行，但尚未获得运行机会 | 调度策略、允许的 CPU、竞争和资源限制 |
| 睡眠/等待 | 等待指定条件，当前不能正常参与执行选择 | 条件满足与唤醒协议，再进入可运行状态 |

这是用于解释的逻辑状态；Linux 的任务状态字段可能合并“正在运行”和“可运行”，不能只靠一个 R 字母判断线程是否占着 CPU。内核选择的调度实体也不等同应用的一条请求。[sched(7)](https://man7.org/linux/man-pages/man7/sched.7.html)说明策略和优先级作用于线程；本文不把其旧 CFS 概述当成全部现行内核算法。

唤醒通常让等待者重新具备执行条件，不保证它立即抢占当前线程，也不保证条件在真正开始执行时仍成立。条件变量返回后仍需按同步协议重新检查谓词，见[锁与同步原语](locks-and-synchronization.md)。

## 四种“切换”不能合并计数

内核把当前执行任务换成另一任务时，要保存与恢复继续执行所需的上下文，例如寄存器、栈相关状态和相应调度信息；具体内容与路径依体系结构和实现决定。切换地址空间可能引入地址翻译管理，工作集变化也可能增加缓存成本，但不能假定每次切换都清空全部缓存或 [TLB](../../glossary/systems.md#systems.virtual-memory)。

| 事件 | 是否必然换成另一内核任务 | 需要区分 |
| --- | --- | --- |
| [系统调用](../../glossary/systems.md#systems.privilege)、异常或中断入口 | 否 | 进入内核后可以返回原线程，也可能触发调度 |
| 内核任务切换 | 是，在本文所指的任务切换范围内 | 同进程线程可共享地址空间；跨进程并非复制全部内存 |
| CPU 迁移 | 线程后来改到另一 CPU 运行 | 同 CPU 换任务不要求迁移；迁移也需结合先前状态解释 |
| 用户态协程切换 | 不必 | [Runtime](../../glossary/runtime.md#runtime.virtual-machine) 可在同一内核线程上保存/恢复协程状态 |

协程挂起后，如果其所在内核线程继续执行其他协程，应用已经发生执行者变化，内核任务切换计数却可能没有增加。反之，线程在同一个函数中被多次抢占，业务层也可能看不到显式切换。

## 一条时间线拆开运行、睡眠和排队

设同一线程执行这段自选时间线，单位毫秒，忽略其他开销：

| 区间/时刻 | 状态 | 耗时归属 |
| --- | --- | --- |
| 0–2 | 运行，随后发起需等待的 I/O | CPU 执行 2 |
| 2–7 | 等待 I/O | 非就绪等待 5 |
| 7 | 条件满足，线程被唤醒 | 已就绪，尚未得到 CPU |
| 7–10 | 就绪，等待运行机会 | [调度等待](../../glossary/performance.md#performance.cpu-metrics) 3 |
| 10–12 | 恢复运行并结束操作 | CPU 执行 2 |

总历时 12，CPU 执行 4，睡眠等待 5，就绪等待 3。2 到 10 的离 CPU 时间是 8，不能全部叫作 I/O 时间，也不能全部叫作调度等待。这里没有规定时刻 2 到 10 之间 CPU 实际换了多少任务。

[perf sched timehist](https://man7.org/linux/man-pages/man1/perf-sched.1.html)分别报告离 CPU 的 wait time、可运行到真正运行的 scheduling delay 和 run time。采集时还要检查事件丢失、过滤范围及任务身份；线程的一段时间也不一定只服务一条请求。

## 切换次数是线索，持续时间需要另一份证据

[getrusage(2)](https://man7.org/linux/man-pages/man2/getrusage.2.html)区分自愿和非自愿[上下文切换](../../glossary/systems.md#systems.context-switch)，并可按进程或 Linux 单线程范围统计。自愿通常关联等待资源，非自愿通常关联被抢占；它们都不是某种具体锁、I/O 或业务失败的唯一证明。

自选两个计数样本：相隔恰好一秒，从 1200 到 1500，自愿切换增量为 300，即这个范围平均每秒 300 次；若没有切换耗时数据，就不能再乘一个随意常数计算“损失了多少 CPU”。少量切换也可能伴随很长睡眠或一次很长的就绪等待。

内核的[调度统计文档](https://docs.kernel.org/scheduler/sched-stats.html)还区分运行时间、等待运行时间和时间片次数，字段版本与配置需要一并记录。排查时应关联每线程时间线、锁/系统调用等待、CPU 亲和性和配额，而非只看整机 CPU 平均值。资源分母与 CPU 配额造成的暂停见[CPU 利用率与配额](../performance/cpu-time-utilization-load-and-quotas.md)。

## 调度策略与应用完成没有同一个期限

Linux 的 [EEVDF 文档](https://docs.kernel.org/scheduler/sched-eevdf.html)介绍以资格和虚拟期限选择任务的机制；这里的虚拟期限不是一条请求对用户承诺的墙钟 [deadline](../../glossary/reliability.md#reliability.retry-budget)。本文只采用其策略层次，不给所有内核配置套固定时间片或统一等待上界。

减少线程竞争、缩短临界区、控制[排队](../../glossary/performance.md#performance.queueing)和选择合理[并发](../../glossary/systems.md#systems.concurrency)度，可能减少等待；把所有线程绑到同一 CPU 或把优先级调高，也可能将等待转嫁给其他任务。应在相同负载与正确性前提下比较。算法的 [wait-free](../../glossary/systems.md#systems.lock-free-progress) 自身步骤保证同样不能保证线程获得及时调度，见[无锁算法与进度](lock-free-algorithms-linearization-and-progress.md)。

## 自检

1. 唤醒后还有哪段等待，为什么 R 状态不证明线程正在 CPU 上？
2. 系统调用、任务切换、CPU 迁移与协程切换各改变哪个边界？
3. 教学时间线中 CPU、睡眠、就绪等待与总历时各是多少？
4. 计数从 1200 到 1500 能推导什么，为什么不能直接算切换耗时？
5. 为什么虚拟调度期限和 wait-free 都不能独立证明请求墙钟期限？

## 来源与核查

- [Linux sched(7)](https://man7.org/linux/man-pages/man7/sched.7.html)、[getrusage(2)](https://man7.org/linux/man-pages/man2/getrusage.2.html)，2026-10-26 核查当日 man-pages；覆盖策略接口、线程范围与切换计数，未沿用旧调度器名称判断现行实现。
- [Kernel Scheduler Statistics](https://docs.kernel.org/scheduler/sched-stats.html)、[EEVDF](https://docs.kernel.org/scheduler/sched-eevdf.html)，2026-10-26 核查滚动文档；覆盖运行/就绪等待口径及选择机制，不承诺特定发行版行为。
- [perf sched](https://man7.org/linux/man-pages/man1/perf-sched.1.html)，2026-10-26 核查；覆盖 timehist 的三类时长，未执行采集或回放。

本文为 source-checked 概念说明。没有执行线程调度、亲和性/优先级调整、perf 采集、内核切换成本或[延迟](../../glossary/performance.md#performance.latency-throughput)对照实验。
