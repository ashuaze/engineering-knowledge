---
id: "kb-performance-cpu-metrics"
title: "CPU 利用率、负载与配额：主机还有空闲，请求为什么仍在等"
kind: "concept"
domain: "performance"
status: "evolving"
summary: "区分经过时间、CPU 时间、利用率、运行队列和 Linux 负载，解释核数口径、cgroup 带宽与资源压力。"
created: "2026-10-20"
updated: "2026-10-26"
last_verified: "2026-10-20"
verification: "source-checked"
prerequisites: ["kb-systems-execution-units", "kb-performance-latency-queues"]
related: ["kb-systems-cpu-caches", "kb-performance-profiling", "kb-performance-benchmarking", "kb-runtime-async-blocking", "kb-devops-container-boundaries", "kb-performance-backpressure", "kb-systems-context-switch", "kb-performance-hotspots-contention", "kb-performance-capacity-autoscaling"]
tags: ["cpu-time", "utilization", "load-average", "cgroup", "saturation"]
---

# CPU 利用率、负载与配额：主机还有空闲，请求为什么仍在等

把离 [CPU 时间](../../glossary/performance.md#performance.cpu-metrics)继续拆成睡眠等待与就绪[排队](../../glossary/performance.md#performance.queueing)，并区分切换计数和持续时间，见[上下文切换与调度等待](../systems/context-switches-run-queues-and-scheduling-delay.md)。新文采用来源核查与自选时间线，没有新增本篇 CPU 或调度采集。

学习入口：监控显示 CPU 只有 20%，为什么服务还是很慢？负载为 8，又是否说明八个核都跑满了？前置：[进程与线程](../systems/process-thread-coroutine.md)、[延迟与排队](latency-throughput-and-queues.md)。本文以 Linux 时间统计、普通公平调度和 [cgroup v2](../../glossary/devops.md#devops.isolation) 为参照，数值为纸面计算，不读取本机计数器或运行[容器](../../glossary/devops.md#devops.containers)负载。

平均值之外的局部约束见[热点与资源竞争](hotspots-contention-and-serialized-service.md)；百分比分母与故障余量见[容量规划与自动扩缩容](capacity-planning-scaling-and-autoscaling-feedback.md)。

## 经过时间和 CPU 时间不能混为一谈

经过时间是从观察起点到终点的时长，包含边界内的运行与等待。[CPU 时间](../../glossary/performance.md#performance.cpu-metrics)是[线程](../../glossary/systems.md#systems.execution-units)实际被调度执行期间累计的时间，可分[用户态](../../glossary/systems.md#systems.privilege)和内核态；Linux 的 [getrusage](https://man7.org/linux/man-pages/man2/getrusage.2.html)分别提供进程或线程等范围，进程口径可汇总其全部线程。

纸面单线程任务总历时 100ms，假定各段互不重叠：10ms 被调度执行、60ms 等待依赖、30ms 就绪却未获得 CPU。CPU 时间为 10ms，经过时间为 100ms；没有使用 CPU 的 90ms 不能归为“某个函数计算慢”。真实请求可能跨线程、异步任务与服务，不能把所有线程的时间直接相加当作请求经过时间。

“在 CPU 上”也不保证每一周期都在完成有效业务计算；自旋和数据供应造成的停顿仍可能占据执行时段，参照[利用率与停顿周期分析](https://www.brendangregg.com/blog/2017-05-09/cpu-utilization-is-wrong.html)。[CPU-bound](../../glossary/performance.md#performance.bound) 与 I/O-bound 是对当前主要约束的描述，不能用一个固定利用率阈值自动分类。

## 百分比必须说明分母和范围

对指定进程，在窗口 Δt 中累计 CPU 时间增量为 ΔC。一种展示把一个逻辑 CPU 在窗口内的时间作为 100%，即 ΔC/Δt×100%；另一种再除以 N 个逻辑 CPU 的总时间，把整机容量作为 100%。工具和仪表盘未必采用同一口径。

纸面例：8 个逻辑 CPU、10 秒窗口，某进程只用一个线程运行了 10 CPU 秒。按单 CPU 基准为 100%，按八个逻辑 CPU 总时间为 12.5%。同一工作没有因为显示不同而改变。多线程汇总也可能在第一种口径超过 100%；逻辑 CPU 又不等于若干互不干扰、性能相同的物理核。

总量还可能掩盖一个繁忙线程、单核[热点](../../glossary/performance.md#performance.contention)、亲和性限制或一小段突发。先确定主机、进程、线程还是 cgroup，窗口和可用 CPU 集合，再解释平均值；“主机空闲”不等于该任务现在可以获得任意空闲核。

Linux 的 [proc_stat](https://man7.org/linux/man-pages/man5/proc_stat.5.html)给出累计状态时间，通常需取相同计数器的窗口差值。user/system、idle、iowait、steal 等字段含义不同；iowait 并非 CPU 真正在执行 I/O 等待的时长，也不能单独证明磁盘故障。计算时还需核对字段是否重复包含、计数器重置与统计范围，不能任意相加得到业务利用率。

## 利用率、饱和与负载分别回答什么

| 观察 | 主要回答 | 不能直接推出 |
| --- | --- | --- |
| CPU 利用率 | 所选 CPU 时间有多少被使用 | 单核热点或某请求获得了足够时间 |
| 就绪[队列](../../glossary/algorithms.md#algorithms.queues)与调度等待 | 可运行任务是否等待执行资源 | 所有等待都是应用计算太多 |
| Linux load average | 运行/可运行及特定不可中断等待任务的平滑负载 | CPU 百分比或当前请求数 |
| 配额节流与资源压力 | 工作是否受相应资源约束停顿 | 每个慢请求都由同一原因导致 |

Linux [proc_loadavg](https://man7.org/linux/man-pages/man5/proc_loadavg.5.html)记录 1、5、15 分钟负载，涵盖运行/可运行任务及不可中断等待，而不只是正在占用 CPU 的任务。[内核计算说明](https://github.com/torvalds/linux/blob/master/kernel/sched/loadavg.c)使用指数衰减平均，不是三个普通窗口算术均值；不能把 load=8 解释为“CPU 利用率 800%”或“每个核恰有一个任务”。

CPU 总利用率高且就绪等待增加，支持检查执行资源竞争；负载较高但 CPU 不忙，还需检查不可中断等待等情况。[上下文切换](../../glossary/systems.md#systems.context-switch)多可能来自正常调度、短任务或同步，次数本身也不是耗时或根因，仍要结合任务状态与[调用栈](profiling-stacks-and-flame-graphs.md)。

## 配额可以让空闲主机上的任务停下

cgroup v2 的 [cpu.max](https://docs.kernel.org/admin-guide/cgroup-v2.html#cpu-interface-files)用最大 CPU 时间和周期限制相应调度类的组带宽，单位为微秒；本文限定普通公平调度、控制器有效、无突发额度及其他祖先限制的模型。

纸面配置 `50000 100000` 表示每 100ms 周期最多消耗 50ms 聚合 CPU 时间，长期额度约等于半个逻辑 CPU 的执行时间，不是整台主机的一半。多个线程共享额度，并不意味着每个线程都有一份。

若一个周期开始时额度完整，两线程恰好在两个 CPU 上各运行 25ms，就可能合计用完 50ms；即使主机别处仍空闲，组内后续工作也可能等到额度补充。这个例子不预测实际调度顺序或精确停顿长度。

额度上限不是资源预留；允许在一组 CPU 上运行，也不表示这些 CPU 已专属于它。实际还需检查祖先 cgroup、允许 CPU 集合及竞争。cpu.stat 的 usage 和节流计数各有统计范围，不能把“被节流周期比例”当作“[超时](../../glossary/api.md#api.retries)请求比例”，也不能仅凭本组计数排除祖先限额影响。

## 压力指标补充等待证据

Linux [PSI](https://docs.kernel.org/accounting/psi.html)对 CPU、内存和 I/O 提供压力信息；其中 some 表示至少部分任务因相应资源停顿的时间比例，分母是时间，不是慢请求数。系统级与 cgroup 级接口的范围不同，不应未经核对就把百分比混合使用。

PSI、就绪等待、节流、利用率与请求[延迟](../../glossary/performance.md#performance.latency-throughput)可放在相同时间段比较，帮助选择后续证据。相关性仍不是因果证明；锁等待、远端慢响应、[连接池](../../glossary/api.md#api.pool)[排队](../../glossary/performance.md#performance.queueing)与 CPU 限制可以同时存在，不能只挑一张图解释全部延迟。

自检：百分比以单核、主机还是配额为分母？进程 CPU 时间是否包含全部线程？等待是未就绪、就绪未调度还是受配额限制？负载里是否包含不在 CPU 上的任务？

2026-10-20 核查 Linux man-pages 6.19 的 getrusage、proc_stat、proc_loadavg、内核负载计算与 cgroup v2/PSI 文档，以及利用率分析，状态为 source-checked；文档版本不等于本机内核版本。时长、核数与额度为教学设计，未读取 Linux 指标、修改配额或运行 CPU/调度/压力实验。
