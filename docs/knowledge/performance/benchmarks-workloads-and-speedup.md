---
id: "kb-performance-benchmarking"
title: "基准测试与加速比：局部快四倍，整体为什么只快一点"
kind: "concept"
domain: "performance"
status: "evolving"
summary: "解释比较口径、工作负载、冷暖状态和测量偏差，用 Amdahl 模型说明局部优化与整体收益的边界。"
created: "2026-10-20"
updated: "2026-10-20"
last_verified: "2026-10-20"
verification: "source-checked"
prerequisites: ["kb-performance-latency-queues"]
related: ["kb-systems-cpu-caches", "kb-performance-cpu-metrics", "kb-performance-profiling", "kb-performance-overload-lab", "kb-engineering-test-scopes"]
tags: ["benchmark", "workload", "measurement", "speedup", "amdahl"]
---

# 基准测试与加速比：局部快四倍，整体为什么只快一点

学习入口：改动后某个循环更快，能否宣布服务吞吐提升，或 [P99](../../glossary/performance.md#performance.percentiles) 同比例下降？前置：[延迟、吞吐与统计边界](latency-throughput-and-queues.md)。本文解释怎样设计可比较的性能证据，并用理想模型推演加速上限；参照 Google [Benchmark](../../glossary/performance.md#performance.benchmark)、LLVM、Python 3.13 计时和 Cornell [并行](../../glossary/systems.md#systems.concurrency)材料，没有执行基准或压测。

## 先确认比较的是相同结果

基准测试以约定工作负载衡量某段行为。微基准可隔离一个操作，端到端测量包含完整路径；两者回答不同问题。删除校验、少返回数据或改变持久性后更快，不足以证明同一业务契约得到了优化。

| 对照条件 | 需要固定或明确记录 |
| --- | --- |
| 输入与结果 | 数据规模、分布、命中率、有效/失败输入及正确性要求 |
| 测量边界 | 初始化、分配、构建、网络、清理及等待是否计入 |
| 实现与资源 | 代码、编译/[运行时](../../glossary/runtime.md#runtime.virtual-machine)、依赖、并发、CPU 配额和硬件 |
| 状态与负载 | 冷/暖缓存、[连接复用](../../glossary/networking.md#networking.keepalive)、后台工作及请求发起方式 |

按相同输出检查正确性后，再比较耗时与资源；要说明收益在哪些条件下成立，而不是只报告一个最快数字。源码没有变化也可能因数据、资源或环境不同而得到不同结果。

## 计时、预热与重复分别解决不同问题

经过时间计时应选择适合短时长、不会因日历校时跳变的时钟；[CPU 时间](../../glossary/performance.md#performance.cpu-metrics)则回答实际执行消耗，两者不能混用。Python 3.13 的 [perf_counter 与 process_time](https://docs.python.org/3.13/library/time.html#time.perf_counter)分别展示经过时间与[进程](../../glossary/systems.md#systems.execution-units) CPU 时间的不同口径；本文不提供已运行的计时片段。

预热可让缓存、初始化或运行时进入所关心的状态，却会排除冷启动成本。如果目标是首次请求，就不能把首次加载全部丢弃；如果目标是稳定重复工作，也需记录预热过程并确认行为没有继续漂移。Google Benchmark 的[运行与预热说明](https://google.github.io/benchmark/user_guide.html#runtime-and-reporting-considerations)区分预热、迭代和重复运行，不保证随便预热几次就得到稳态。

这里的迭代指一轮测量内重复执行操作，重复运行指再次取得一轮测量结果；再次运行也不天然独立。同一进程内的大量循环不等于大量相互独立的实验。重复运行、交错或随机化对照顺序，可以帮助识别噪声和顺序效应；仍需保留每轮结果、样本规模与汇总方法，不能只挑最好的一轮。LLVM 的[基准提示](https://llvm.org/docs/Benchmarking.html)强调低噪声仍不能排除测量偏差。

[编译器](../../glossary/runtime.md#runtime.compilation)还可能折叠常量、消除未使用结果，或把重复工作移出测量循环；最终测到的可能不是想测的操作。Google Benchmark 的 [DoNotOptimize 说明](https://google.github.io/benchmark/user_guide.html#preventing-optimization)也明确该机制不禁止表达式内部的一切优化。需要核对实际工作与输出，不能以某个辅助函数的名字代替验证。

## 微基准、负载、压力和长稳测试不要互相代替

微基准主要比较局部操作；目标[负载测试](../../glossary/performance.md#performance.load-tests)观察预期请求组合下的行为；压力测试探索超出目标后的瓶颈和失效；长稳测试观察持续运行中的泄漏、积累或退化。即使某循环长期稳定，也不表示网络服务已经通过长稳或容量验证。

闭环客户端等待完成再发下一项，服务变慢时会自动降低发起率；开放式到达按计划继续产生尝试，可能累积等待。应记录计划/实际发起、接纳、完成、成功、拒绝和[超时](../../glossary/api.md#api.retries)，不能仅凭线程数称承受了某个 [RPS](../../glossary/performance.md#performance.rates)。已有[过载控制实验](overload-control-lab.md)提供局部接纳对照，本篇没有重跑或扩展该证据。

若比较固定工作量的完成时间，说明总量与边界；若比较固定负载下的[延迟](../../glossary/performance.md#performance.latency-throughput)，说明实际负载是否一致；若比较最大吞吐，则还要定义错误率、尾延迟和资源约束。吞吐、平均延迟、P99 与资源成本不能互相按一个比例换算。

## Amdahl 模型约束局部改善的整体收益

设固定工作量的基线时间 T，由互不重叠、可相加的两部分组成；其中 p 比例的部分加速 s 倍，其余不变，且没有新增开销。对 0≤p≤1、s≥1：

```text
新时间 T' = T × [(1 − p) + p/s]
整体加速比 S = T/T' = 1 / [(1 − p) + p/s]
```

这是 Amdahl 思路对局部加速的表达；若 s 来自理想并行，还需能够均分相应工作且忽略协调成本，参照 [Cornell Amdahl 材料](https://cvw.cac.cornell.edu/parallel/efficiency/amdahls-law)。增加工作规模的分析是另一种比较，不能套用固定工作量的同一结论。

纸面例：原任务 100ms，其中 80ms 可优化，20ms 不变。优化部分快 4 倍后为 20ms，总时间为 40ms，整体加速 2.5 倍，并非 4 倍。即使该部分趋近零，剩余 20ms 仍限制整体加速不超过 5 倍；若新实现另添 10ms 协调成本，总时间变成 50ms、加速 2 倍。

p 是该模型中基线时间的占比，不是代码行比例、函数调用比例或任意一张 CPU [火焰图](../../glossary/performance.md#performance.profiling)的宽度。CPU 样本占比和请求经过时间不同，异步阶段还可能重叠；有[排队](../../glossary/performance.md#performance.queueing)、[资源竞争](../../glossary/performance.md#performance.contention)和关键路径变化时，应重新建立模型，不能直接把 80% 的采样比例代入预测请求 P99。

缓存布局、工作规模或算法变化也可能改变原模型条件。实测加速超过某个旧模型上限，首先应核查分解、口径和假设，不必立即断言测量错误或“突破定律”。

## 让结果支持可复查的判断

一份可复查记录至少包含问题、相同业务契约、版本、输入与资源、测量边界、状态准备、每轮结果及汇总方式，并留下正确性和观测开销的检查。结论应同时说明绝对耗时、相对变化及条件，差异小于或接近波动时不要强行判定改进。

分析热点可配合 [Profiling 与火焰图](profiling-stacks-and-flame-graphs.md)，资源范围可配合 [CPU 利用率与配额](cpu-time-utilization-load-and-quotas.md)。定位证据与比较证据相互补充，但都不能用没有实际运行的纸面数字替代。

自检：两版是否完成相同工作？测的是冷启动还是重复稳态？计时是否包含等待和必要初始化？更快是否只是负载变小？局部占比是否与整体目标采用同一时间口径？

2026-10-20 核查 Google Benchmark、LLVM 基准文档、Python 3.13 时间 API 及 Cornell Amdahl 材料，状态为 source-checked。100/40/50ms 与 2.5/5/2 倍为模型计算；未安装基准框架、编译或运行片段、采集样本、执行负载/压力/长稳测试或测量优化收益。
